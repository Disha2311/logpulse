import React from 'react';

const LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

const LogTable = ({
  logs = [],
  filters = { service: '', level: '', dateFrom: '', dateTo: '', page: 1 },
  onFilterChange,
  availableServices = []
}) => {
  const handleInputChange = (field, value) => {
    onFilterChange({
      ...filters,
      [field]: value,
      page: 1 // Reset to page 1 on filter change
    });
  };

  const handlePageChange = (direction) => {
    const newPage = direction === 'next' ? filters.page + 1 : Math.max(1, filters.page - 1);
    onFilterChange({
      ...filters,
      page: newPage
    });
  };

  const formatTimestamp = (isoString) => {
    const d = new Date(isoString);
    return d.toLocaleString([], {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  return (
    <div className="glass-card animate-fade-in" style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>Historical Log Finder</h3>
        <p style={styles.subtitle}>Filter and search database-persisted logs</p>
      </div>

      {/* Filter Controls Bar */}
      <div style={styles.filterBar}>
        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>Service</label>
          <select
            className="form-input"
            value={filters.service}
            onChange={(e) => handleInputChange('service', e.target.value)}
            style={styles.select}
          >
            <option value="">All Services</option>
            {availableServices.map(srv => (
              <option key={srv} value={srv}>{srv}</option>
            ))}
          </select>
        </div>

        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>Severity Level</label>
          <select
            className="form-input"
            value={filters.level}
            onChange={(e) => handleInputChange('level', e.target.value)}
            style={styles.select}
          >
            <option value="">All Levels</option>
            {LOG_LEVELS.map(lvl => (
              <option key={lvl} value={lvl}>{lvl}</option>
            ))}
          </select>
        </div>

        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>From (Start Date)</label>
          <input
            className="form-input"
            type="datetime-local"
            value={filters.dateFrom}
            onChange={(e) => handleInputChange('dateFrom', e.target.value)}
            style={styles.dateInput}
          />
        </div>

        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>To (End Date)</label>
          <input
            className="form-input"
            type="datetime-local"
            value={filters.dateTo}
            onChange={(e) => handleInputChange('dateTo', e.target.value)}
            style={styles.dateInput}
          />
        </div>

        <button
          className="btn btn-secondary"
          onClick={() => {
            onFilterChange({ service: '', level: '', dateFrom: '', dateTo: '', page: 1 });
          }}
          style={styles.resetBtn}
        >
          Reset Filters
        </button>
      </div>

      {/* Table Container */}
      <div style={styles.tableContainer}>
        {logs.length === 0 ? (
          <div style={styles.emptyState}>
            No logs matched the selected filter criteria.
          </div>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr style={styles.tableHeaderRow}>
                <th style={styles.th}>Timestamp</th>
                <th style={styles.th}>Service</th>
                <th style={styles.th}>Level</th>
                <th style={styles.th}>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} style={styles.tr}>
                  <td style={styles.tdTime}>{formatTimestamp(log.timestamp)}</td>
                  <td style={styles.tdService}>{log.service}</td>
                  <td style={styles.td}>
                    <span className={`badge badge-${log.level.toLowerCase()}`}>
                      {log.level}
                    </span>
                  </td>
                  <td style={styles.tdMessage}>{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Bar */}
      {logs.length > 0 && (
        <div style={styles.paginationBar}>
          <button
            className="btn btn-secondary"
            disabled={filters.page === 1}
            onClick={() => handlePageChange('prev')}
            style={styles.pageBtn}
          >
            ← Previous Page
          </button>
          <span style={styles.pageIndicator}>Page {filters.page}</span>
          <button
            className="btn btn-secondary"
            disabled={logs.length < 50} // If less than 50 rows returned, there is no next page
            onClick={() => handlePageChange('next')}
            style={styles.pageBtn}
          >
            Next Page →
          </button>
        </div>
      )}
    </div>
  );
};

const styles = {
  card: {
    padding: '1.5rem',
    borderRadius: '16px',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
  },
  header: {
    marginBottom: '1.5rem',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '700',
  },
  subtitle: {
    fontSize: '0.8125rem',
    color: 'var(--text-secondary)',
  },
  filterBar: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '1rem',
    alignItems: 'flex-end',
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: 'rgba(0,0,0,0.15)',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
  },
  filterGroup: {
    flex: '1 1 200px',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.35rem',
  },
  filterLabel: {
    fontSize: '0.75rem',
    fontWeight: '600',
    color: 'var(--text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  select: {
    padding: '0.5rem 0.75rem',
    fontSize: '0.875rem',
    cursor: 'pointer',
  },
  dateInput: {
    padding: '0.5rem 0.75rem',
    fontSize: '0.875rem',
  },
  resetBtn: {
    height: '38px',
    fontSize: '0.8125rem',
    padding: '0 1rem',
  },
  tableContainer: {
    overflowX: 'auto',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.875rem',
    textAlign: 'left',
  },
  tableHeaderRow: {
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderBottom: '1px solid var(--border-color)',
  },
  th: {
    padding: '0.875rem 1rem',
    fontWeight: '600',
    color: 'var(--text-secondary)',
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  tr: {
    borderBottom: '1px solid var(--border-color)',
    transition: 'background-color 0.2s ease',
  },
  td: {
    padding: '0.875rem 1rem',
    verticalAlign: 'middle',
  },
  tdTime: {
    padding: '0.875rem 1rem',
    color: 'var(--text-secondary)',
    fontFamily: 'monospace',
    whiteSpace: 'nowrap',
  },
  tdService: {
    padding: '0.875rem 1rem',
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  tdMessage: {
    padding: '0.875rem 1rem',
    fontFamily: 'monospace',
    color: 'var(--text-primary)',
    wordBreak: 'break-all',
  },
  emptyState: {
    textAlign: 'center',
    padding: '3rem',
    color: 'var(--text-secondary)',
    fontStyle: 'italic',
  },
  paginationBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '1.25rem',
  },
  pageIndicator: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    fontWeight: '500',
  },
  pageBtn: {
    fontSize: '0.8125rem',
    padding: '0.5rem 1rem',
  },
};

export default LogTable;
