import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddUser, setShowAddUser] = useState(false);
  const [showEditUser, setShowEditUser] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const navigate = useNavigate();

  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    status: 'active'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Erreur lors de la récupération des utilisateurs');
      const data = await response.json();
      setUsers(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/admin/users', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });

      if (!response.ok) throw new Error('Erreur lors de l\'ajout de l\'utilisateur');

      setShowAddUser(false);
      setNewUser({ username: '', email: '', password: '', status: 'active' });
      fetchUsers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setNewUser({
      username: user.username,
      email: user.email,
      status: user.status,
      password: '' // Le mot de passe n'est pas pré-rempli pour des raisons de sécurité
    });
    setShowEditUser(true);
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/admin/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });

      if (!response.ok) throw new Error('Erreur lors de la mise à jour de l\'utilisateur');

      setShowEditUser(false);
      setSelectedUser(null);
      setNewUser({ username: '', email: '', password: '', status: 'active' });
      fetchUsers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/admin/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error('Erreur lors de la suppression de l\'utilisateur');
        fetchUsers();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  if (loading) return <div className="loading">Chargement...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>Administration</h1>
        <button onClick={handleLogout} className="logout-btn">
          Déconnexion
        </button>
      </header>

      <main className="admin-content">
        <section className="users-section">
          <div className="section-header">
            <h2>Gestion des Utilisateurs</h2>
            <button 
              className="add-btn"
              onClick={() => setShowAddUser(true)}
            >
              + Nouvel Utilisateur
            </button>
          </div>

          <div className="table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nom d'utilisateur</th>
                  <th>Email</th>
                  <th>Statut</th>
                  <th>Date de création</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{user.status}</td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                    <td>
                      <EditIcon onClick={() => handleEditUser(user)} className="edit-icon" />
                      <DeleteIcon onClick={() => handleDeleteUser(user.id)} className="delete-icon" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {showAddUser && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Ajouter un utilisateur</h2>
              <form onSubmit={handleAddUser}>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Nom d'utilisateur"
                    value={newUser.username}
                    onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="password"
                    placeholder="Mot de passe"
                    value={newUser.password}
                    onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <select
                    value={newUser.status}
                    onChange={(e) => setNewUser({...newUser, status: e.target.value})}
                    required
                  >
                    <option value="active">Actif</option>
                    <option value="inactive">Inactif</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="submit" className="submit-btn">Ajouter</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => setShowAddUser(false)}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showEditUser && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Modifier l'utilisateur</h2>
              <form onSubmit={handleUpdateUser}>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Nom d'utilisateur"
                    value={newUser.username}
                    onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="password"
                    placeholder="Nouveau mot de passe (laisser vide pour ne pas changer)"
                    value={newUser.password}
                    onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <select
                    value={newUser.status}
                    onChange={(e) => setNewUser({...newUser, status: e.target.value})}
                    required
                  >
                    <option value="active">Actif</option>
                    <option value="inactive">Inactif</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="submit" className="submit-btn">Mettre à jour</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => {
                      setShowEditUser(false);
                      setSelectedUser(null);
                    }}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
