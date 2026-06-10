import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { setAuthToken } from './api/axios';

function App() {
  const [token, setToken] = useState(null);

  const handleLoginSuccess = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    setToken(null);
    setAuthToken(null);
  };

  return (
    <Router>
      <Routes>
        {/* Login Page Route */}
        <Route 
          path="/login" 
          element={
            token ? <Navigate to="/" replace /> : <Login onLoginSuccess={handleLoginSuccess} />
          } 
        />
        
        {/* Protected Dashboard Route */}
        <Route 
          path="/" 
          element={
            token ? (
              <Dashboard token={token} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        
        {/* Catch-all Redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
