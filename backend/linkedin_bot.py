import time
import os, uuid, logging, requests, json, threading
from urllib.parse import urlencode
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '788tikx31tlxr7')# LinkedIn app client ID
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', 'WPL_AP1.UH17vI9IwnynugWZ.G9nCzg==')# LinkedIn app client secret
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:3000/linkedin-callback')# Redirect URI for LinkedIn app
# Ensure the redirect URI is registered in your LinkedIn app settings
SCOPES = 'profile email w_member_social openid'# Scopes for LinkedIn API access
# Ensure the scopes are registered in your LinkedIn app settings

VALID_STATES = set()

@app.route('/start_oauth')
def start_oauth():
    state = str(uuid.uuid4())
    VALID_STATES.add(state)
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': SCOPES
    }
    auth_url = 'https://www.linkedin.com/oauth/v2/authorization?' + urlencode(params)
    logging.info(f"Generated auth URL: {auth_url}")
    return jsonify({'authUrl': auth_url})

@app.route('/exchange_token', methods=['POST'])
def exchange_token():
    data = request.json or {}
    code = data.get('code')
    state = data.get('state')
    logging.info(f"Exchanging code={code} state={state}")

    if not code or not state or state not in VALID_STATES:
        return jsonify({'error': 'Invalid code or state'}), 400
    VALID_STATES.remove(state)

    token_resp = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    logging.info(f"Token endpoint status: {token_resp.status_code}")
    if token_resp.status_code != 200:
        return jsonify({
            'error': 'Failed to get token',
            'details': token_resp.text
        }), 400

    token_data = token_resp.json()
    access_token = token_data.get('access_token')

    profile_resp = requests.get(
        'https://api.linkedin.com/v2/me?projection=(id,localizedFirstName,localizedLastName,profilePicture(displayImage~:playableStreams))',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    logging.info(f"Profile status: {profile_resp.status_code}")
    profile = profile_resp.ok and profile_resp.json()

    email_resp = requests.get(
        'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    logging.info(f"Email status: {email_resp.status_code}")
    email = email_resp.ok and email_resp.json()

    return jsonify({
        'access_token': access_token,
        'profile': profile,
        'email': email
    })

class LinkedInBot:
    def __init__(self, email, password, access_token, search_query):
        self.email = email
        self.password = password
        self.access_token = access_token
        self.search_query = search_query
        self.driver = None
        self.wait = None
        self.history_file = 'engagement_history.json'
        self.engagement_history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed loading history: {e}")
        return {"posts": []}

    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.engagement_history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed saving history: {e}")

    def setup_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 300)  # 5-minute timeout

    def login(self):
        logging.info("Logging into LinkedIn via Selenium...")
        self.driver.get("https://www.linkedin.com/login")
        user = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        pwd = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        user.send_keys(self.email)
        pwd.send_keys(self.password)
        pwd.send_keys(Keys.RETURN)
        time.sleep(20)
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "global-nav")))
            logging.info("Selenium login successful")
            return True
        except TimeoutException:
            logging.error("Selenium login failed")
            return False

    def find_top_post(self):
        encoded = quote_plus(self.search_query)
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded}"
        logging.info(f"Searching for: {self.search_query}")
        self.driver.get(url)
        time.sleep(2)
        for _ in range(5):
            self.driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(1)
        posts = self.driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
        best, best_score = None, -1
        for p in posts:
            try:
                pid = p.get_attribute('data-urn') or p.get_attribute('id')
                if pid in (x['post_id'] for x in self.engagement_history['posts']):
                    continue
                # reactions
                try:
                    r = p.find_element(By.XPATH, ".//button[contains(@aria-label,'reactions')]/span").text
                    rc = int(''.join(filter(str.isdigit, r)))
                except Exception:
                    rc = 0
                # comments
                try:
                    c = p.find_element(By.XPATH, ".//button[contains(@aria-label,'comment')]/span").text
                    cc = int(''.join(filter(str.isdigit, c)))
                except Exception:
                    cc = 0
                score = rc + cc
                if score > best_score:
                    best, best_score = p, score
            except Exception:
                continue
        return best

    def fetch_user_id(self):
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                sub = data.get("sub")
                if sub:
                    logging.info(f"Fetched LinkedIn user ID (sub): {sub}")
                    return sub
                else:
                    logging.error("No 'sub' found in userinfo response.")
            else:
                logging.error(f"Failed to fetch userinfo: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error fetching userinfo: {e}")
        return None

    def create_post_api(self, text):
        user_id = self.fetch_user_id()
        if not user_id:
            logging.error("Cannot create post: user_id (sub) not retrieved.")
            return False

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        body = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        resp = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=body)
        if resp.status_code == 201:
            logging.info("API post created successfully")
            return True
        logging.error(f"API post failed: {resp.status_code} {resp.text}")
        return False

    def repost_once(self):
        post = self.find_top_post()
        if not post:
            logging.info("No post found to repost")
            return
        pid = post.get_attribute('data-urn') or post.get_attribute('id')
        # author
        try:
            actor = post.find_element(By.CSS_SELECTOR,
                "div.update-components-actor__meta span.update-components-actor__title span").text
        except Exception:
            actor = "Unknown"
        # expand text
        try:
            btn = post.find_element(By.CSS_SELECTOR, ".feed-shared-inline-show-more-text__see-more-less-toggle")
            self.driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
        except NoSuchElementException:
            pass
        # text
        try:
            body = post.find_element(By.CSS_SELECTOR,
                "div.feed-shared-update-v2__description span.break-words").text
        except Exception:
            body = ""
        content = f"Repost from {actor}:\n\n{body}"
        content = ''.join(ch for ch in content if ord(ch) <= 0xFFFF)

        # Use API to post
        if self.create_post_api(content):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.engagement_history['posts'].append({'post_id': pid, 'author': actor, 'timestamp': now})
            self._save_history()

    def close(self):
        if self.driver:
            self.driver.quit()

class BotManager:
    def __init__(self, email, password, access_token, keyword):
        self.bot = LinkedInBot(email, password, access_token, keyword)
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            return False
        self.running = True
        def target():
            self.bot.setup_browser()
            if self.bot.login():
                while self.running:
                    self.bot.repost_once()
                    time.sleep(60*30)  # every 30 minutes
            else:
                logging.error("Failed to login")
            self.bot.close()
        self.thread = threading.Thread(target=target, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if not self.running:
            return False
        self.running = False
        self.thread.join(timeout=5)
        return True
        
@app.route('/novnc/')
def serve_novnc():
    # Read and modify the vnc.html file
    with open('/opt/novnc/vnc.html', 'r') as f:
        content = f.read()
    
    # Force WebSocket connection to use the same HTTPS domain
    content = content.replace(
        'host = window.location.hostname;',
        f'host = "{os.getenv("RENDER_EXTERNAL_HOSTNAME", "repostig-backend.onrender.com")};'
    ).replace(
        'port = 6080;',
        'port = window.location.port || (window.location.protocol === "https:" ? 443 : 80);'
    )
    
    response = make_response(content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/start_bot', methods=['POST'])
def start_bot():
    data = request.json or {}
    access_token = data.get('access_token')
    keyword = data.get('keyword')
    email = data.get('email')
    password = data.get('password')
    if not access_token or not keyword or not email or not password:
        return jsonify({'error': 'Missing access_token, keyword, email, or password'}), 400
    manager = BotManager(email, password, access_token, keyword)
    started = manager.start()
    status_code = 200 if started else 409
    return jsonify({'started': started}), status_code

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    global manager
    if manager is None:
        return jsonify({'stopped': False}), 409
    stopped = manager.stop()
    status_code = 200 if stopped else 409
    return jsonify({'stopped': stopped}), status_code

if __name__ == '__main__':
    app.run(port=5000, debug=True)
