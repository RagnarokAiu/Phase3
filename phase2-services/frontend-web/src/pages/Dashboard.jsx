import React from 'react';

const Dashboard = () => {
  return (
    <div>
      <h1 className="gradient-text" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Dashboard</h1>
      <p style={{ color: 'var(--text-muted)' }}>Welcome to the Cloud Learning Platform.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
        {['User Service', 'Chat Service', 'Document Service', 'Quiz Service', 'STT Service', 'TTS Service'].map((service) => (
          <div key={service} style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
            <h3 style={{ margin: '0 0 0.5rem 0' }}>{service}</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="status-indicator"></div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Operational</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
