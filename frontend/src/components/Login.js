import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Stocker le token et les informations de l'utilisateur
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('userRole', data.user.role);

        // Rediriger en fonction du rôle
        if (data.user.role === 'admin') {
          navigate('/admin-dashboard'); // Redirection vers le dashboard admin
        } else {
          navigate('/user-dashboard'); // Redirection vers le dashboard utilisateur
        }
      } else {
        setError(data.message || 'Erreur de connexion');
      }
    } catch (err) {
      console.error('Erreur de connexion:', err);
      setError('Erreur lors de la connexion au serveur');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Connexion</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="username"
              placeholder="Nom d'utilisateur"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Mot de passe"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-btn">
            Se connecter
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
