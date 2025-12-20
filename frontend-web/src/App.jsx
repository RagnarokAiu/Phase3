import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './layout/Layout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import ChatInterface from './pages/ChatInterface';
import QuizInterface from './pages/QuizInterface';
import SpeechInterface from './pages/SpeechInterface';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />

          <Route path="/documents" element={
            <ProtectedRoute allowedRoles={['admin', 'teacher']}>
              <Documents />
            </ProtectedRoute>
          } />

          <Route path="/chat" element={
            <ProtectedRoute>
              <ChatInterface />
            </ProtectedRoute>
          } />

          <Route path="/quiz" element={
            <ProtectedRoute>
              <QuizInterface />
            </ProtectedRoute>
          } />

          <Route path="/speech" element={
            <ProtectedRoute>
              <SpeechInterface />
            </ProtectedRoute>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  );
}

export default App;
