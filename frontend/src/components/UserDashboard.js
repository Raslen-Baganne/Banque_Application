import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import './UserDashboard.css';

const UserDashboard = () => {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showEditAccount, setShowEditAccount] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const navigate = useNavigate();

  const [newAccount, setNewAccount] = useState({
    name: '',
    email: '',
    phone: '',
    cin: '',
    balance: ''
  });

  const [newTransaction, setNewTransaction] = useState({
    sender_id: '',
    receiver_id: '',
    amount: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const accountsResponse = await fetch('/api/user/accounts', {
        headers
      });
      if (!accountsResponse.ok) throw new Error('Erreur lors de la récupération des comptes');
      const accountsData = await accountsResponse.json();
      setAccounts(accountsData);

      const transactionsResponse = await fetch('/api/user/transactions', {
        headers
      });
      if (!transactionsResponse.ok) throw new Error('Erreur lors de la récupération des transactions');
      const transactionsData = await transactionsResponse.json();
      setTransactions(transactionsData);

      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce compte ?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/accounts/${accountId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error('Erreur lors de la suppression du compte');
        fetchData();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette transaction ?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/transactions/${transactionId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error('Erreur lors de la suppression de la transaction');
        fetchData();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleEditAccount = (account) => {
    setSelectedAccount(account);
    setNewAccount({
      name: account.name,
      email: account.email,
      phone: account.phone,
      cin: account.cin,
      balance: account.balance
    });
    setShowEditAccount(true);
  };

  const handleUpdateAccount = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/accounts/${selectedAccount.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newAccount)
      });

      if (!response.ok) throw new Error('Erreur lors de la mise à jour du compte');

      setShowEditAccount(false);
      setSelectedAccount(null);
      setNewAccount({ name: '', email: '', phone: '', cin: '', balance: '' });
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddAccount = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/accounts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newAccount)
      });

      if (!response.ok) throw new Error('Erreur lors de l\'ajout du compte');

      setShowAddAccount(false);
      setNewAccount({ name: '', email: '', phone: '', cin: '', balance: '' });
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/transactions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newTransaction)
      });

      if (!response.ok) throw new Error('Erreur lors de l\'ajout de la transaction');

      setShowAddTransaction(false);
      setNewTransaction({ sender_id: '', receiver_id: '', amount: '' });
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Chargement...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Tableau de bord bancaire</h1>
        <button onClick={handleLogout} className="logout-btn">
          Déconnexion
        </button>
      </header>

      <div className="dashboard-content">
        <section className="actions-section">
          <button 
            className="action-btn add-account"
            onClick={() => setShowAddAccount(true)}
          >
            + Nouveau Compte
          </button>
          <button 
            className="action-btn add-transaction"
            onClick={() => setShowAddTransaction(true)}
          >
            + Nouvelle Transaction
          </button>
        </section>

        {showAddAccount && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Ajouter un nouveau compte</h2>
              <form onSubmit={handleAddAccount}>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Nom"
                    value={newAccount.name}
                    onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Email"
                    value={newAccount.email}
                    onChange={(e) => setNewAccount({...newAccount, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="tel"
                    placeholder="Téléphone"
                    value={newAccount.phone}
                    onChange={(e) => setNewAccount({...newAccount, phone: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="CIN"
                    value={newAccount.cin}
                    onChange={(e) => setNewAccount({...newAccount, cin: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="number"
                    placeholder="Solde initial"
                    value={newAccount.balance}
                    onChange={(e) => setNewAccount({...newAccount, balance: e.target.value})}
                    required
                  />
                </div>
                <div className="modal-actions">
                  <button type="submit" className="submit-btn">Ajouter</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => setShowAddAccount(false)}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showEditAccount && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Modifier le compte</h2>
              <form onSubmit={handleUpdateAccount}>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Nom"
                    value={newAccount.name}
                    onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Email"
                    value={newAccount.email}
                    onChange={(e) => setNewAccount({...newAccount, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="tel"
                    placeholder="Téléphone"
                    value={newAccount.phone}
                    onChange={(e) => setNewAccount({...newAccount, phone: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="CIN"
                    value={newAccount.cin}
                    onChange={(e) => setNewAccount({...newAccount, cin: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="number"
                    placeholder="Solde"
                    value={newAccount.balance}
                    onChange={(e) => setNewAccount({...newAccount, balance: e.target.value})}
                    required
                  />
                </div>
                <div className="modal-actions">
                  <button type="submit" className="submit-btn">Mettre à jour</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => {
                      setShowEditAccount(false);
                      setSelectedAccount(null);
                    }}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showAddTransaction && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Nouvelle transaction</h2>
              <form onSubmit={handleAddTransaction}>
                <div className="form-group">
                  <select
                    value={newTransaction.sender_id}
                    onChange={(e) => setNewTransaction({...newTransaction, sender_id: e.target.value})}
                    required
                  >
                    <option value="">Sélectionner l'expéditeur</option>
                    {accounts.map(account => (
                      <option key={account.id} value={account.id}>
                        {account.name} - Solde: {account.balance} TND
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <select
                    value={newTransaction.receiver_id}
                    onChange={(e) => setNewTransaction({...newTransaction, receiver_id: e.target.value})}
                    required
                  >
                    <option value="">Sélectionner le destinataire</option>
                    {accounts.map(account => (
                      <option key={account.id} value={account.id}>
                        {account.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <input
                    type="number"
                    placeholder="Montant"
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
                    required
                  />
                </div>
                <div className="modal-actions">
                  <button type="submit" className="submit-btn">Effectuer le transfert</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => setShowAddTransaction(false)}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <section className="accounts-section">
          <h2>Comptes Bancaires</h2>
          <div className="table-container">
            <table className="accounts-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Email</th>
                  <th>Téléphone</th>
                  <th>CIN</th>
                  <th>Solde</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map(account => (
                  <tr key={account.id}>
                    <td>{account.name}</td>
                    <td>{account.email}</td>
                    <td>{account.phone}</td>
                    <td>{account.cin}</td>
                    <td className="balance">{account.balance.toLocaleString()} TND</td>
                    <td className="actions">
                      <button 
                        className="icon-btn edit"
                        onClick={() => handleEditAccount(account)}
                      >
                        <EditIcon />
                      </button>
                      <button 
                        className="icon-btn delete"
                        onClick={() => handleDeleteAccount(account.id)}
                      >
                        <DeleteIcon />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="transactions-section">
          <h2>Historique des Transactions</h2>
          <div className="table-container">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>De</th>
                  <th>À</th>
                  <th>Montant</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(transaction => (
                  <tr key={transaction.id}>
                    <td>{new Date(transaction.date).toLocaleString()}</td>
                    <td>{transaction.sender_name}</td>
                    <td>{transaction.receiver_name}</td>
                    <td className="amount">{transaction.amount.toLocaleString()} TND</td>
                    <td className="actions">
                      <button 
                        className="icon-btn delete"
                        onClick={() => handleDeleteTransaction(transaction.id)}
                      >
                        <DeleteIcon />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

export default UserDashboard;
