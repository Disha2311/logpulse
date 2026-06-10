import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

const COLOR_PALETTE = [
  '#8b5cf6', // Purple
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f59e0b', // Yellow
  '#ec4899', // Pink/Critical
  '#06b6d4', // Cyan
  '#f43f5e', // Rose
];

const ErrorRateChart = ({ stats = [] }) => {
  // Transform raw stats into chart-friendly format
  // Raw stats format: [{ service: 'web', hour: '2026-06-10T08:00:00Z', error_count: 5 }]
  // Chart format: [{ name: '08:00', web: 5, database: 2 }]

  // 1. Find all unique hours and services
  const hourMap = {};
  const serviceSet = new Set();

  stats.forEach(item => {
    const dateObj = new Date(item.hour);
    // Format hour as "HH:00" in local timezone
    const hourLabel = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    
    serviceSet.add(item.service);

    if (!hourMap[item.hour]) {
      hourMap[item.hour] = {
        rawTime: item.hour,
        name: hourLabel,
      };
    }
    hourMap[item.hour][item.service] = item.error_count;
  });

  // Convert map to sorted array by raw timestamp
  const chartData = Object.values(hourMap).sort((a, b) => new Date(a.rawTime) - new Date(b.rawTime));
  const services = Array.from(serviceSet);

  // If no services or data, return a placeholder
  if (chartData.length === 0) {
    return (
      <div style={styles.placeholderContainer}>
        <p style={styles.placeholderText}>No error stats available for the last 24 hours.</p>
      </div>
    );
  }

  return (
    <div style={styles.chartWrapper}>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis 
            dataKey="name" 
            stroke="var(--text-secondary)" 
            fontSize={11}
            tickLine={false}
            dy={8}
          />
          <YAxis 
            stroke="var(--text-secondary)" 
            fontSize={11}
            tickLine={false}
            dx={-4}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#161827',
              borderColor: 'var(--border-color)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
              fontSize: '12px'
            }}
            itemStyle={{ color: 'var(--text-primary)' }}
            labelStyle={{ fontWeight: 'bold', color: 'var(--text-secondary)' }}
          />
          <Legend 
            verticalAlign="top" 
            height={36} 
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: '12px', color: 'var(--text-primary)' }}
          />
          {services.map((service, index) => (
            <Line
              key={service}
              type="monotone"
              dataKey={service}
              stroke={COLOR_PALETTE[index % COLOR_PALETTE.length]}
              strokeWidth={2}
              dot={{ r: 3, strokeWidth: 1 }}
              activeDot={{ r: 5 }}
              name={service}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const styles = {
  chartWrapper: {
    paddingTop: '1rem',
  },
  placeholderContainer: {
    display: 'flex',
    height: '280px',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--text-secondary)',
  },
  placeholderText: {
    fontSize: '0.875rem',
    fontStyle: 'italic',
  },
};

export default ErrorRateChart;
