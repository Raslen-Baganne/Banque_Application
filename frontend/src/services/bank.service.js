const getAuthHeader = () => {
  const user = JSON.parse(localStorage.getItem('user'));
  if (user && user.token) {
    return { 'Authorization': 'Bearer ' + user.token };
  }
  return {};
};

const getAllAccounts = async () => {
  const response = await fetch('/api/accounts', {
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) {
    throw new Error('Failed to fetch accounts');
  }
  return response.json();
};

const getAllTransactions = async () => {
  const response = await fetch('/api/transactions', {
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) {
    throw new Error('Failed to fetch transactions');
  }
  return response.json();
};

const makeTransfer = async (sender_id, receiver_id, amount) => {
  const response = await fetch('/api/transactions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ sender_id, receiver_id, amount })
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to make transfer');
  }
  return response.json();
};

const getAllUsers = async () => {
  const response = await fetch('/api/users', {
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json();
};

const updateUser = async (userId, userData) => {
  const response = await fetch(`/api/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(userData)
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to update user');
  }
  return response.json();
};

const deleteUser = async (userId) => {
  const response = await fetch(`/api/users/${userId}`, {
    method: 'DELETE',
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to delete user');
  }
  return response.json();
};

const bankService = {
  getAllAccounts,
  getAllTransactions,
  makeTransfer,
  getAllUsers,
  updateUser,
  deleteUser
};

export default bankService;
