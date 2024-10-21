<template>
  <div>
    <h1>Signup</h1>
    <form @submit.prevent="signup">
      <input v-model="username" type="text" placeholder="Username" required>
      <input v-model="email" type="email" placeholder="Email" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <input v-model="displayName" type="text" placeholder="Display Name" required>
      <input v-model="github" type="url" placeholder="GitHub URL">
      <input v-model="profileImage" type="url" placeholder="Profile Image URL">
      <button type="submit">Signup</button>
    </form>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserSignup',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      displayName: '',
      github: '',
      profileImage: '',
      error: ''
    }
  },
  methods: {
    async signup() {
      try {
        const response = await axios.post('http://localhost:8000/project/api/signup/', {
          username: this.username,
          email: this.email,
          password: this.password,
          displayName: this.displayName,
          github: this.github,
          profileImage: this.profileImage
        });
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        this.$router.push('/stream');
      } catch (error) {
        this.error = 'Signup failed';
      }
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
