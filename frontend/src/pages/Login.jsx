import React, { useState } from 'react';
import axiosInstance, { setAuthToken } from '../api/axios';

const Login = ({ onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      if (isRegister) {
        // Register flow
        await axiosInstance.post('/auth/register', { email, password });
        setSuccessMsg('Registration successful! Please log in.');
        setIsRegister(false);
        setPassword('');
      } else {
        // Login flow
        const response = await axiosInstance.post('/auth/login', { email, password });
        const { access_token } = response.data;
        setAuthToken(access_token);
        onLoginSuccess(access_token);
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
          ? detail[0]?.msg
          : 'An unexpected error occurred. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div className="glass-card animate-fade-in" style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logo}>⚡ LOGFLOW</div>
          <h2 style={styles.title}>{isRegister ? 'Create Account' : 'Sign In'}</h2>
          <p style={styles.subtitle}>
            {isRegister
              ? 'Get started with real-time log monitoring'
              : 'Access your real-time log alerting system'}
          </p>
        </div>

        {error && <div style={styles.error}>{error}</div>}
        {successMsg && <div style={styles.success}>{successMsg}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              className="form-input"
              type="email"
              id="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@company.com"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              className="form-input"
              type="password"
              id="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            style={styles.submitBtn}
            disabled={loading}
          >
            {loading ? 'Processing...' : isRegister ? 'Register' : 'Login'}
          </button>
        </form>

        <div style={styles.footer}>
          <button
            style={styles.toggleBtn}
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
              setSuccessMsg('');
            }}
            type="button"
          >
            {isRegister
              ? 'Already have an account? Sign in'
              : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '1.5rem',
  },
  card: {
    width: '100%',
    maxWidth: '420px',
    padding: '2.5rem',
    borderRadius: '16px',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  logo: {
    fontSize: '1.25rem',
    fontWeight: '800',
    color: '#8b5cf6',
    letterSpacing: '0.1em',
    marginBottom: '0.75rem',
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: '700',
    marginBottom: '0.5rem',
    letterSpacing: '-0.02em',
  },
  subtitle: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    lineHeight: '1.4',
  },
  submitBtn: {
    width: '100%',
    padding: '0.8rem',
    marginTop: '0.5rem',
    fontSize: '0.9375rem',
  },
  error: {
    background: 'rgba(239, 68, 68, 0.12)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#f87171',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    fontSize: '0.875rem',
    marginBottom: '1.25rem',
  },
  success: {
    background: 'rgba(16, 185, 129, 0.12)',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    color: '#34d399',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    fontSize: '0.875rem',
    marginBottom: '1.25rem',
  },
  footer: {
    textAlign: 'center',
    marginTop: '1.5rem',
  },
  toggleBtn: {
    background: 'none',
    border: 'none',
    color: '#8b5cf6',
    fontSize: '0.8125rem',
    cursor: 'pointer',
    textDecoration: 'none',
    fontWeight: '500',
  },
};

export default Login;
