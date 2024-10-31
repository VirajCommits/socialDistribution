import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js'; 
import axios from 'axios'

axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.withCredentials = true;

axios.interceptors.request.use(
    config => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );

  const app = createApp(App)

app.use(router); // Register the router
app.mount('#app');