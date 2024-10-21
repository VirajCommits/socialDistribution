<template>
    <div>
      <h1>Stream/Author-feed Page</h1>
      <button class="logout-button" @click="logoutNode">
        Logout
      </button>
      <button class="profile-button" @click="goToProfile">
        Profile
      </button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StreamPage',
    methods: {
        goToProfile() {
            this.$router.push('/profile');
        },
        logoutNode() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            this.$router.push('/login');
        }
    }
  }
  </script>
  
  <style scoped>
  h1 {
    color: #42b983;
  }
  
  .logout-button, .profile-button {
    position: absolute;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 50%;
    padding: 10px 15px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  .profile-button {
    top: 20px;
    right: 20px;
  }
  .logout-button {
    top: 20px;
    left: 20px;
  }
  
  .profile-button:hover {
    background-color: #2c8a6a;
  }
  </style>
  