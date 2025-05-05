import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000';
const CALLBACK_PATH = '/linkedin-callback';

export default function App() {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [keyword, setKeyword] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const didExchange = useRef(false);

  useEffect(() => {
    if (
      window.location.pathname === CALLBACK_PATH &&
      !didExchange.current
    ) {
      didExchange.current = true;
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      const state = params.get('state');
      if (code && state) {
        setStatus('exchanging');
        axios.post(`${API_BASE}/exchange_token`, { code, state })
          .then(res => {
            setData(res.data);
            setStatus('done');
          })
          .catch(err => {
            console.error(err);
            setError(err.response?.data?.error || 'Exchange failed');
            setStatus('error');
          });
      } else {
        setError('Missing code or state');
        setStatus('error');
      }
    }
  }, []);

  const handleLogin = async () => {
    setStatus('starting');
    try {
      const res = await axios.get(`${API_BASE}/start_oauth`);
      window.location.href = res.data.authUrl;
    } catch (err) {
      console.error(err);
      setError('Failed to initiate LinkedIn login');
      setStatus('error');
    }
  };

  const handleStartBot = async () => {
    if (!data?.access_token || !keyword || !email || !password) {
      alert('Please login and enter a keyword, email, and password.');
      return;
    }
    try {
      const res = await axios.post(`${API_BASE}/start_bot`, {
        access_token: data.access_token,
        keyword: keyword,
        email: email,
        password: password
      });
      if (res.data.started) setStatus('running');
      else alert('Bot is already running.');
    } catch (err) {
      console.error(err);
      alert('Failed to start bot');
    }
  };

  const handleStopBot = async () => {
    try {
      const res = await axios.post(`${API_BASE}/stop_bot`);
      if (res.data.stopped) setStatus('stopped');
      else alert('Bot was not running.');
    } catch (err) {
      console.error(err);
      alert('Failed to stop bot');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>LinkedIn Bot Control</h1>
      <p>Status: <strong>{status}</strong></p>
      {status === 'error' && (
        <p style={{ color: 'red' }}>{error}</p>
      )}
      <button onClick={handleLogin} disabled={status === 'running'}>
        Login with LinkedIn
      </button>
      {data && (
        <div>
          <h3>
            Welcome,{' '}
            {data.profile?.localizedFirstName}{' '}
            {data.profile?.localizedLastName}
          </h3>
          <div>
            <label>Keyword:</label>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              style={{ margin: '0.5rem', padding: '0.5rem' }}
            />
          </div>
          <div>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ margin: '0.5rem', padding: '0.5rem' }}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ margin: '0.5rem', padding: '0.5rem' }}
            />
          </div>
          <button onClick={handleStartBot} disabled={status === 'running'}>
            Start Bot
          </button>
          <button onClick={handleStopBot} disabled={status !== 'running'}>
            Stop Bot
          </button>
        </div>
      )}
    </div>
  );
}