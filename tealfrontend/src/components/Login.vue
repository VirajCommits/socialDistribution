<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  name: 'UserLogin', // Changed the name to a multi-word name
  data() {
    return {
      username: '',
      password: '',
      error: null,
    };
  },
  methods: {
    login() {
      axios
        .post('/auth/login/', { // Ensure this endpoint is correct
          username: this.username,
          password: this.password,
        })
        .then((response) => {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('uuid', response.data.uuid); // Store the UUID in local storage
          this.$router.push({ name: 'AuthorProfile', params: { uuid: response.data.uuid } });
        })
        .catch(() => {
          this.error = 'Invalid username or password.';
        });
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
</style>
