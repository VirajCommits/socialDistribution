// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import axios from 'axios';

axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.withCredentials = true;

// Create the Vue app
const app = createApp(App);

// Set up Axios base URL (replace with your API's base URL)
// Update the axios base URL configuration
axios.defaults.baseURL = process.env.NODE_ENV === 'production'
  ? 'https://teal-rakshit-a972530cc317.herokuapp.com/service/api'
  : 'http://localhost:8000/service/api';

console.log('Current Axios base URL:', axios.defaults.baseURL);
// Request Interceptor to add the Authorization header with the token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token'); // Get the token from localStorage
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`; // Set the Authorization header
      console.log('Token found and added to request');
    } else {
      console.log('No token found in localStorage');
    }
    return config;
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
    if (error.response && error.response.status === 401) {
      // Token might be invalid or expired, handle re-authentication
      localStorage.removeItem('token'); // Clear the token
      router.push('/login'); // Redirect to login page
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
