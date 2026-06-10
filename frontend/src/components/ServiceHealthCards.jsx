import React from 'react';

const ServiceHealthCards = ({ rules = [], recentErrors5m = [] }) => {
  // Group rules by service
  const serviceThresholds = {};
  rules.forEach(rule => {
    serviceThresholds[rule.service] = {
      threshold: rule.threshold,
      window: rule.window_minutes,
      email: rule.notify_email,
      webhook: rule.notify_webhook_url
    };
  });

  // Count errors per service in the last 5 minutes
  const serviceErrorCounts = {};
  recentErrors5m.forEach(log => {
    if (log.level === 'ERROR' || log.level === 'CRITICAL') {
      serviceErrorCounts[log.service] = (serviceErrorCounts[log.service] || 0) + 1;
    }
  });

  // We want to make sure we show all services that have alert rules, plus any others that have sent logs
  const allServices = Array.from(
    new Set([...rules.map(r => r.service), ...recentErrors5m.map(l => l.service)])
  );

  return (
    <div style={styles.grid}>
      {allServices.length === 0 ? (
        <div className="glass-card animate-fade-in" style={styles.emptyCard}>
          No services monitored yet. Send some logs to see health status.
        </div>
      ) : (
        allServices.map(service => {
          const ruleInfo = serviceThresholds[service];
          const errorCount = serviceErrorCounts[service] || 0;
          const threshold = ruleInfo ? ruleInfo.threshold : null;
          
          let status = 'green';
          let statusLabel = 'HEALTHY';
          let statusClass = 'status-green';

          if (threshold !== null) {
            if (errorCount >= threshold) {
              status = 'red';
              statusLabel = 'CRITICAL BREACH';
              statusClass = 'status-red';
            } else if (errorCount > 0) {
              status = 'yellow';
              statusLabel = 'WARNING';
              statusClass = 'status-yellow';
            }
          } else if (errorCount > 0) {
            status = 'yellow';
            statusLabel = 'UNMONITORED ERRORS';
            statusClass = 'status-yellow';
          }

          const cardGlowStyle = {
            ...styles.card,
            boxShadow: 
              status === 'red' ? 'var(--glow-red)' :
              status === 'yellow' ? 'var(--glow-yellow)' :
              'var(--glow-green)',
            borderColor:
              status === 'red' ? 'rgba(239, 68, 68, 0.4)' :
              status === 'yellow' ? 'rgba(245, 158, 11, 0.4)' :
              'rgba(16, 185, 129, 0.3)'
          };

          return (
            <div key={service} className="glass-card animate-fade-in" style={cardGlowStyle}>
              <div style={styles.cardHeader}>
                <span style={styles.serviceName}>{service}</span>
                <span style={{ ...styles.statusIndicator, ...styles[statusClass] }}>
                  {statusLabel}
                </span>
              </div>
              <div style={styles.metricContainer}>
                <span style={styles.metricValue}>{errorCount}</span>
                <span style={styles.metricLabel}>errors / 5m</span>
              </div>
              <div style={styles.footer}>
                {threshold !== null ? (
                  <div style={styles.ruleText}>
                    Threshold: <strong>{threshold}</strong> errors per <strong>{ruleInfo.window}</strong> min
                  </div>
                ) : (
                  <div style={styles.noRuleText}>No alerting rule configured</div>
                )}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.25rem',
    marginBottom: '2rem',
  },
  card: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    padding: '1.25rem',
    borderRadius: '12px',
    borderWidth: '1px',
    borderStyle: 'solid',
  },
  emptyCard: {
    gridColumn: '1 / -1',
    textAlign: 'center',
    color: 'var(--text-secondary)',
    padding: '2rem',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  serviceName: {
    fontWeight: '700',
    fontSize: '1.1rem',
    letterSpacing: '-0.01em',
    textTransform: 'capitalize',
  },
  statusIndicator: {
    fontSize: '0.7rem',
    fontWeight: '700',
    padding: '0.2rem 0.5rem',
    borderRadius: '4px',
    letterSpacing: '0.05em',
  },
  'status-green': {
    backgroundColor: 'rgba(16, 185, 129, 0.12)',
    color: '#34d399',
    border: '1px solid rgba(16, 185, 129, 0.25)',
  },
  'status-yellow': {
    backgroundColor: 'rgba(245, 158, 11, 0.12)',
    color: '#fbbf24',
    border: '1px solid rgba(245, 158, 11, 0.25)',
  },
  'status-red': {
    backgroundColor: 'rgba(239, 68, 68, 0.12)',
    color: '#f87171',
    border: '1px solid rgba(239, 68, 68, 0.25)',
    animation: 'pulse 2s infinite ease-in-out',
  },
  metricContainer: {
    display: 'flex',
    alignItems: 'baseline',
    margin: '0.5rem 0 1rem 0',
  },
  metricValue: {
    fontSize: '2rem',
    fontWeight: '800',
    lineHeight: '1',
    marginRight: '0.35rem',
  },
  metricLabel: {
    fontSize: '0.8125rem',
    color: 'var(--text-secondary)',
    fontWeight: '500',
  },
  footer: {
    borderTop: '1px solid var(--border-color)',
    paddingTop: '0.75rem',
    fontSize: '0.75rem',
    color: 'var(--text-secondary)',
  },
  ruleText: {
    lineHeight: '1.4',
  },
  noRuleText: {
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  },
};

export default ServiceHealthCards;
