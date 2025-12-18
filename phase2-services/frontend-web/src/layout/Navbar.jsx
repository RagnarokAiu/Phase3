import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, FileText, BrainCircuit, Mic, LogOut, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null; // Don't show navbar if not logged in (optional, usually layouts handle this but for simplicity)

  return (
    <nav className="navbar">
      <div className="container nav-container">
        <NavLink to="/" className="nav-logo">
          <span className="gradient-text">CloudLearn</span>
        </NavLink>

        <div className="nav-links">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          {(user.role === 'admin' || user.role === 'teacher') && (
            <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <FileText size={18} />
              Documents
            </NavLink>
          )}

          <NavLink to="/chat" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <MessageSquare size={18} />
            AI Chat
          </NavLink>
          <NavLink to="/quiz" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <BrainCircuit size={18} />
            Quiz
          </NavLink>
          <NavLink to="/speech" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <Mic size={18} />
            Speech
          </NavLink>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div className="nav-status" style={{ background: 'transparent', border: 'none', padding: 0 }}>
            <User size={16} />
            <span style={{ textTransform: 'capitalize' }}>{user.username} ({user.role})</span>
          </div>
          <button onClick={handleLogout} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', padding: '0.5rem', cursor: 'pointer' }}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
