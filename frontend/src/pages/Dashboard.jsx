import React, { useEffect, useState, useCallback } from 'react';
import axiosInstance from '../api/axios';
import ServiceHealthCards from '../components/ServiceHealthCards';
import ErrorRateChart from '../components/ErrorRateChart';
import LogTable from '../components/LogTable';
import LiveLogFeed from '../components/LiveLogFeed';

const Dashboard = ({ token, onLogout }) => {
  const [rules, setRules] = useState([]);
  const [recentErrors5m, setRecentErrors5m] = useState([]);
  const [stats, setStats] = useState([]);
  
  // Log Table states
  const [tableLogs, setTableLogs] = useState([]);
  const [filters, setFilters] = useState({
    service: '',
    level: '',
    dateFrom: '',
    dateTo: '',
    page: 1
  });
  
  const [availableServices, setAvailableServices] = useState([]);
  
  // Alert Rule Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [ruleForm, setRuleForm] = useState({
    service: '',
    threshold: 5,
    window_minutes: 5,
    notify_email: '',
    notify_webhook_url: ''
  });
  const [modalError, setModalError] = useState('');
  const [modalSuccess, setModalSuccess] = useState('');
  const [modalLoading, setModalLoading] = useState(false);

  // centralized fetch for stats & rules (auto-refreshes every 30s)
  const fetchDashboardStats = useCallback(async () => {
    try {
      // 1. Fetch rules
      const rulesRes = await axiosInstance.get('/alert-rules');
      setRules(rulesRes.data);

      // 2. Fetch stats
      const statsRes = await axiosInstance.get('/logs/stats');
      setStats(statsRes.data);

      // 3. Fetch logs from last 5 minutes to compute service health
      const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
      const healthLogsRes = await axiosInstance.get(`/logs?date_from=${fiveMinAgo}&limit=100`);
      setRecentErrors5m(healthLogsRes.data);

      // Extract unique services list
      const serviceSet = new Set([
        ...rulesRes.data.map(r => r.service),
        ...healthLogsRes.data.map(l => l.service)
      ]);
      setAvailableServices(Array.from(serviceSet));

    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  }, []);

  // Fetch log table based on filters
  const fetchTableLogs = useCallback(async () => {
    try {
      let query = `/logs?page=${filters.page}&limit=50`;
      if (filters.service) query += `&service=${filters.service}`;
      if (filters.level) query += `&level=${filters.level}`;
      if (filters.dateFrom) {
        query += `&date_from=${new Date(filters.dateFrom).toISOString()}`;
      }
      if (filters.dateTo) {
        query += `&date_to=${new Date(filters.dateTo).toISOString()}`;
      }

      const response = await axiosInstance.get(query);
      setTableLogs(response.data);
    } catch (err) {
      console.error('Error fetching table logs:', err);
    }
  }, [filters]);

  useEffect(() => {
    fetchDashboardStats();
    // Auto refresh every 30 seconds
    const interval = setInterval(fetchDashboardStats, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardStats]);

  useEffect(() => {
    fetchTableLogs();
  }, [fetchTableLogs]);

  // Handle alert rule submission
  const handleCreateRule = async (e) => {
    e.preventDefault();
    setModalError('');
    setModalSuccess('');
    setModalLoading(true);

    try {
      await axiosInstance.post('/alert-rules', ruleForm);
      setModalSuccess('Alert rule created successfully!');
      setRuleForm({
        service: '',
        threshold: 5,
        window_minutes: 5,
        notify_email: '',
        notify_webhook_url: ''
      });
      // Refresh rules list
      fetchDashboardStats();
      // Auto close modal after 1.5s
      setTimeout(() => {
        setIsModalOpen(false);
        setModalSuccess('');
      }, 1500);
    } catch (err) {
      setModalError(err.response?.data?.detail || 'Failed to create alert rule.');
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Top Navigation Panel */}
      <header className="glass-card animate-fade-in" style={styles.header}>
        <div style={styles.brand}>
          <span style={styles.brandLogo}>⚡</span>
          <div>
            <h1 style={styles.brandName}>LogFlow</h1>
            <p style={styles.brandTag}>Real-Time Log Aggregation Dashboard</p>
          </div>
        </div>
        <div style={styles.headerActions}>
          <button 
            className="btn btn-primary" 
            onClick={() => setIsModalOpen(true)}
            style={styles.ruleBtn}
          >
            + Create Alert Rule
          </button>
          <button className="btn btn-secondary" onClick={onLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main style={styles.layout}>
        {/* Left Side: Health, Chart, Table */}
        <section style={styles.mainContent}>
          {/* Service Health Cards */}
          <h2 style={styles.sectionTitle}>Service Health Status</h2>
          <ServiceHealthCards rules={rules} recentErrors5m={recentErrors5m} />

          {/* Chart Section */}
          <div className="glass-card" style={styles.chartCard}>
            <h2 style={styles.sectionTitle}>Error Rate Trend (Last 24h)</h2>
            <p style={styles.sectionSubtitle}>Hourly count of ERROR and CRITICAL events per service</p>
            <ErrorRateChart stats={stats} />
          </div>

          {/* Table Section */}
          <LogTable
            logs={tableLogs}
            filters={filters}
            onFilterChange={setFilters}
            availableServices={availableServices}
          />
        </section>

        {/* Right Side: WebSocket Live Stream */}
        <aside style={styles.sidebar}>
          <LiveLogFeed token={token} />
        </aside>
      </main>

      {/* Modal Dialog for Alert Rules */}
      {isModalOpen && (
        <div style={styles.modalOverlay}>
          <div className="glass-card animate-fade-in" style={styles.modalCard}>
            <div style={styles.modalHeader}>
              <h3>Add Alerting Policy</h3>
              <button style={styles.closeBtn} onClick={() => setIsModalOpen(false)}>×</button>
            </div>
            
            {modalError && <div style={styles.modalError}>{modalError}</div>}
            {modalSuccess && <div style={styles.modalSuccess}>{modalSuccess}</div>}

            <form onSubmit={handleCreateRule}>
              <div className="form-group">
                <label className="form-label">Service Name</label>
                <input
                  className="form-input"
                  type="text"
                  required
                  placeholder="e.g. auth-service"
                  value={ruleForm.service}
                  onChange={(e) => setRuleForm({ ...ruleForm, service: e.target.value })}
                  disabled={modalLoading}
                />
              </div>

              <div style={styles.row}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Error Threshold</label>
                  <input
                    className="form-input"
                    type="number"
                    required
                    min="1"
                    value={ruleForm.threshold}
                    onChange={(e) => setRuleForm({ ...ruleForm, threshold: parseInt(e.target.value) })}
                    disabled={modalLoading}
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Window (Minutes)</label>
                  <input
                    className="form-input"
                    type="number"
                    required
                    min="1"
                    value={ruleForm.window_minutes}
                    onChange={(e) => setRuleForm({ ...ruleForm, window_minutes: parseInt(e.target.value) })}
                    disabled={modalLoading}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Notification Email</label>
                <input
                  className="form-input"
                  type="email"
                  required
                  placeholder="ops-alerts@company.com"
                  value={ruleForm.notify_email}
                  onChange={(e) => setRuleForm({ ...ruleForm, notify_email: e.target.value })}
                  disabled={modalLoading}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Webhook URL (Optional)</label>
                <input
                  className="form-input"
                  type="url"
                  placeholder="https://api.slack.com/services/..."
                  value={ruleForm.notify_webhook_url}
                  onChange={(e) => setRuleForm({ ...ruleForm, notify_webhook_url: e.target.value })}
                  disabled={modalLoading}
                />
              </div>

              <div style={styles.modalFooter}>
                <button 
                  className="btn btn-secondary" 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  disabled={modalLoading}
                >
                  Cancel
                </button>
                <button 
                  className="btn btn-primary" 
                  type="submit"
                  disabled={modalLoading}
                >
                  {modalLoading ? 'Creating...' : 'Create Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1440px',
    margin: '0 auto',
    padding: '1.5rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 1.5rem',
    borderRadius: '16px',
    marginBottom: '1.5rem',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  brandLogo: {
    fontSize: '2rem',
    background: 'linear-gradient(135deg, var(--color-purple), var(--color-blue))',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  brandName: {
    fontSize: '1.25rem',
    fontWeight: '800',
    lineHeight: '1.1',
  },
  brandTag: {
    fontSize: '0.75rem',
    color: 'var(--text-secondary)',
  },
  headerActions: {
    display: 'flex',
    gap: '1rem',
  },
  ruleBtn: {
    fontSize: '0.8125rem',
  },
  layout: {
    display: 'flex',
    flexDirection: 'row',
    gap: '1.5rem',
    alignItems: 'flex-start',
  },
  mainContent: {
    flex: '1 1 65%',
    display: 'flex',
    flexDirection: 'column',
  },
  sidebar: {
    flex: '1 1 30%',
    position: 'sticky',
    top: '1.5rem',
  },
  sectionTitle: {
    fontSize: '1.1rem',
    fontWeight: '700',
    marginBottom: '0.75rem',
    letterSpacing: '-0.01em',
  },
  sectionSubtitle: {
    fontSize: '0.75rem',
    color: 'var(--text-secondary)',
    marginTop: '-0.5rem',
    marginBottom: '1.25rem',
  },
  chartCard: {
    borderRadius: '16px',
    marginBottom: '1.5rem',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0,0,0,0.6)',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalCard: {
    width: '100%',
    maxWidth: '500px',
    padding: '2rem',
    borderRadius: '16px',
    boxShadow: '0 24px 48px rgba(0,0,0,0.5)',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
    borderBottom: '1px solid var(--border-color)',
    paddingBottom: '0.75rem',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '1.5rem',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
  },
  row: {
    display: 'flex',
    gap: '1rem',
  },
  modalFooter: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.75rem',
    marginTop: '1.5rem',
    borderTop: '1px solid var(--border-color)',
    paddingTop: '1rem',
  },
  modalError: {
    backgroundColor: 'rgba(239, 68, 68, 0.12)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#f87171',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    fontSize: '0.8125rem',
    marginBottom: '1rem',
  },
  modalSuccess: {
    backgroundColor: 'rgba(16, 185, 129, 0.12)',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    color: '#34d399',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    fontSize: '0.8125rem',
    marginBottom: '1rem',
  },
};

export default Dashboard;
