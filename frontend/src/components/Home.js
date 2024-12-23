import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home">
      <header className="home-header">
        <nav>
          <div className="logo">BanqueApp</div>
          <div className="nav-buttons">
            <button onClick={() => navigate('/login')} className="login-button">
              Connexion
            </button>
          </div>
        </nav>
      </header>

      <main className="home-main">
        <section className="hero">
          <div className="hero-content">
            <h1>Bienvenue sur BanqueApp</h1>
            <p>Votre solution bancaire moderne et sécurisée</p>
            <button onClick={() => navigate('/login')} className="cta-button">
              Commencer maintenant
            </button>
          </div>
        </section>

        <section className="features">
          <h2>Nos Services</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">💳</div>
              <h3>Gestion de Comptes</h3>
              <p>Gérez vos comptes bancaires en toute simplicité</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Transactions Rapides</h3>
              <p>Effectuez des transactions en quelques clics</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Sécurité Maximale</h3>
              <p>Vos données sont protégées avec les dernières technologies</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <p>&copy; 2024 BanqueApp. Tous droits réservés.</p>
      </footer>
    </div>
  );
};

export default Home;
