const login = async (username, password) => {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    throw new Error('Invalid credentials');
  }
  
  const data = await response.json();
  if (data.token) {
    localStorage.setItem('user', JSON.stringify(data));
  }
  return data;
};

const register = async (username, email, password) => {
  const response = await fetch('/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error during registration');
  }

  const data = await response.json();
  if (data.token) {
    localStorage.setItem('user', JSON.stringify(data));
  }
  return data;
};

const logout = () => {
  localStorage.removeItem('user');
};

const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) return JSON.parse(userStr);
  return null;
};

const authService = {
  login,
  register,
  logout,
  getCurrentUser,
};

export default authService;
