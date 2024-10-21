<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="login">
      <input v-model="username" type="text" placeholder="Username" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
    <button @click="signupredirect">Not a User? Signup!</button>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:8000/project/api/login/', {
          username: this.username,
          password: this.password
        });
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        const userId = response.data.user.id;
        const uuid = userId.split('/').pop(); // Extract UUID from the ID
        localStorage.setItem('uuid', uuid);
        this.$router.push('/stream');
      } catch (error) {
        this.error = 'Invalid credentials';
      }
    },
    signupredirect(){
        this.$router.push('/signup');
    }
  }
}
</script>

<style scoped>
div{
    display: flex;
    flex-direction: column;
    align-items: center;
}

form{
    display: flex;
    flex-direction: column;
    width: 25%;
}
</style>
