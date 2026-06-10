import React, { useEffect, useState } from 'react';

const LiveLogFeed = ({ token }) => {
  const [liveLogs, setLiveLogs] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!token) return;

    let ws = null;
    let reconnectTimeout = null;

    const connect = () => {
      const wsUrl = `ws://127.0.0.1:8000/ws/logs?token=${token}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connection established.');
      };

      ws.onmessage = (event) => {
        try {
          const logData = JSON.parse(event.data);
          setLiveLogs((prev) => [logData, ...prev].slice(0, 100)); // Limit to last 100
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        console.log(`WebSocket closed: ${event.code}. Attempting reconnect...`);
        reconnectTimeout = setTimeout(connect, 3000); // Reconnect in 3s
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [token]);

  const formatTime = (isoString) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
  };

  const getLogStyle = (level) => {
    switch (level) {
      case 'ERROR':
      case 'CRITICAL':
        return styles.logError;
      case 'WARNING':
        return styles.logWarning;
      case 'INFO':
        return styles.logInfo;
      default:
        return styles.logDebug;
    }
  };

  return (
    <div className="glass-card animate-fade-in" style={styles.card}>
      <div style={styles.header}>
        <div>
          <h3 style={styles.title}>Live Log Feed</h3>
          <p style={styles.subtitle}>Streaming log activity in real time</p>
        </div>
        <div style={styles.statusContainer}>
          <span style={{ 
            ...styles.statusDot, 
            backgroundColor: isConnected ? 'var(--color-green)' : 'var(--color-red)',
            boxShadow: isConnected ? 'var(--glow-green)' : 'var(--glow-red)'
          }} />
          <span style={styles.statusText}>
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
        </div>
      </div>

      <div style={styles.feedContainer}>
        {liveLogs.length === 0 ? (
          <div style={styles.emptyState}>
            {isConnected ? 'Waiting for incoming logs...' : 'Reconnecting to stream...'}
          </div>
        ) : (
          liveLogs.map((log, index) => (
            <div key={log.id || index} style={{ ...styles.logItem, ...getLogStyle(log.level) }}>
              <div style={styles.logHeader}>
                <span style={styles.logTime}>{formatTime(log.timestamp)}</span>
                <span style={styles.logService}>{log.service}</span>
                <span style={styles.logLevel}>{log.level}</span>
              </div>
              <div style={styles.logMessage}>{log.message}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const styles = {
  card: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    padding: '1.25rem',
    borderRadius: '16px',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.25rem',
    borderBottom: '1px solid var(--border-color)',
    paddingBottom: '0.75rem',
  },
  title: {
    fontSize: '1.1rem',
    fontWeight: '700',
  },
  subtitle: {
    fontSize: '0.75rem',
    color: 'var(--text-secondary)',
  },
  statusContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  statusText: {
    fontSize: '0.65rem',
    fontWeight: '700',
    letterSpacing: '0.05em',
    color: 'var(--text-secondary)',
  },
  feedContainer: {
    flex: 1,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.625rem',
    paddingRight: '4px',
    maxHeight: '620px',
  },
  emptyState: {
    display: 'flex',
    height: '200px',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.8125rem',
    color: 'var(--text-secondary)',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  logItem: {
    padding: '0.625rem 0.875rem',
    borderRadius: '8px',
    borderLeftWidth: '3px',
    borderLeftStyle: 'solid',
    fontSize: '0.8125rem',
    lineHeight: '1.4',
    fontFamily: 'monospace',
    animation: 'fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards',
  },
  logHeader: {
    display: 'flex',
    gap: '0.75rem',
    fontSize: '0.75rem',
    fontWeight: '600',
    marginBottom: '0.25rem',
    opacity: 0.85,
  },
  logTime: {
    color: 'var(--text-secondary)',
  },
  logService: {
    color: 'var(--text-primary)',
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  logLevel: {
    marginLeft: 'auto',
  },
  logMessage: {
    color: 'var(--text-primary)',
    wordBreak: 'break-all',
  },
  logInfo: {
    backgroundColor: 'rgba(16, 185, 129, 0.06)',
    borderLeftColor: 'var(--color-green)',
    color: '#34d399',
  },
  logWarning: {
    backgroundColor: 'rgba(245, 158, 11, 0.06)',
    borderLeftColor: 'var(--color-yellow)',
    color: '#fbbf24',
  },
  logError: {
    backgroundColor: 'rgba(239, 68, 68, 0.06)',
    borderLeftColor: 'var(--color-red)',
    color: '#f87171',
  },
  logDebug: {
    backgroundColor: 'rgba(59, 130, 246, 0.06)',
    borderLeftColor: 'var(--color-blue)',
    color: '#60a5fa',
  },
};

export default LiveLogFeed;
