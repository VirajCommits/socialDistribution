// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import axios from 'axios';

// Get the base URL from the environment variable or default to localhost
// const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api';
const isProduction = window.location.hostname.includes('herokuapp.com');
const baseURL = isProduction
  ? 'https://social-distribution-1-3adb84f120d9.herokuapp.com/api'
  : 'http://127.0.0.1:8000/api';

// Axios configuration
import Cookies from 'js-cookie';
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
axios.defaults.withCredentials = true;
axios.defaults.baseURL = baseURL;

console.log('Environment:', process.env.NODE_ENV === 'production' ? 'Production' : 'Development');
console.log('Using API URL:', baseURL);

// Create the Vue app
const app = createApp(App);
// Request Interceptor to add the Authorization header with the token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token'); // Get the token from localStorage

    // Check if the Authorization header is already set
    if (config.headers['Authorization']) {
      // If the header is already Basic, do nothing
      if (config.headers['Authorization'].startsWith('Basic')) {
        return config; // Return the config as is
      }
    }

    // If no Basic header is present and a token exists, set it as Bearer
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`; // Set the Authorization header to Bearer token
    } else {
      // If no token is found, remove it from localStorage and redirect to login
      localStorage.removeItem('token');
      router.push('/login');
    }

    return config; // Return the modified config object
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor for error handling
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.warn('Authentication error - redirecting to login');
          // localStorage.removeItem('token');
          // localStorage.removeItem('user');
          // router.push('/login');
          break;
        case 403:
          console.error('Authorization error:', error.response.data);
          break;
        case 500:
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.status, error.response.data);
      }
    } else if (error.request) {
      console.error('Network error - no response received');
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Make Axios available globally
app.config.globalProperties.$axios = axios;

// Use router
app.use(router);

// Mount the app
app.mount('#app');
