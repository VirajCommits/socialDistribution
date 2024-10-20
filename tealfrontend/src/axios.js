import axios from 'axios';

// Create an axios instance
const instance = axios.create({
  baseURL: 'http://localhost:8000/api/',
});

// Add the CSRF token to every request
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    const csrfToken = getCookie('csrftoken');  // Extract CSRF token

    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }

    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Helper function to get the CSRF token from the cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default instance;
