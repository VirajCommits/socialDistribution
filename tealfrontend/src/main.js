// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import axios from 'axios';

// Get the base URL from the environment variable or default to localhost
// const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api';
const isProduction = window.location.hostname.includes('herokuapp.com');
const baseURL = isProduction
  ? 'https://project-teal-1-2b076456090f.herokuapp.com/api'
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
    if (token) {
      console.log("inside config headers: =================== " , config.headers["Authorization"])
      if(!config.headers["Authorization"]){
        config.headers['Authorization'] = `Bearer ${token}`
      }
      if (config.headers["Authorization"] && !config.headers["Authorization"].startsWith("Basic ")){
        config.headers['Authorization'] = `Bearer ${token}`; // Set the Authorization header
        
      }
      console.log("inside config headers: =================== " , config.headers["Authorization"])
      if(!config.headers["Authorization"]){
        config.headers['Authorization'] = `Bearer ${token}`
      }
      if (config.headers["Authorization"] && !config.headers["Authorization"].startsWith("Basic ")){
        config.headers['Authorization'] = `Bearer ${token}`; // Set the Authorization header
        
      }
      // console.log('Token found and added to request');
    } else {
      // console.log('No token found in localStorage');
      localStorage.removeItem('token');
      router.push('/login');
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