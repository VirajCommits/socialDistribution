<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Login</h1>
      <form @submit.prevent="login">
        <input v-model="username" type="text" placeholder="Username" required />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
      </form>
      <button class="signup-button" @click="signupredirect">
        Not a User? Sign Up!
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UserLogin",
  data() {
    return {
      username: "",
      password: "",
      error: "",
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post(
          "http://localhost:8000/project/api/login/",
          {
            username: this.username,
            password: this.password,
          }
        );
        localStorage.setItem("token", response.data.access);
        localStorage.setItem("user", JSON.stringify(response.data.user));
        const userId = response.data.user.id;
        const uuid = userId.split("/").pop(); // Extract UUID from the ID
        localStorage.setItem("uuid", uuid);
        this.$router.push("/stream");
      } catch (error) {
        this.error = "Invalid credentials";
      }
    },
    signupredirect() {
      this.$router.push("/signup");
    },
  },
};
</script>

<style scoped>
/* Import Google Fonts */
@import url("https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap");

/* General Styles */
body {
  margin: 0;
  font-family: "Roboto", sans-serif;
  background-color: #f0f2f5;
}

/* Background */
.login-container {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  /* Alternatively, you can use an image:
  background-image: url('your-background-image.jpg');
  background-size: cover;
  background-position: center;
  */
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

/* Login Box */
.login-box {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 40px 30px;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  text-align: center;
  width: 350px;
}

/* Heading */
.login-box h1 {
  margin-bottom: 30px;
  color: #333333;
  font-weight: 700;
}

/* Form Inputs */
.login-box input[type="text"],
.login-box input[type="password"] {
  width: 100%;
  padding: 12px 20px;
  margin: 10px 0;
  border: 1px solid #cccccc;
  border-radius: 30px;
  box-sizing: border-box;
  font-size: 16px;
  background-color: #f7f7f7;
}

/* Form Inputs Focus */
.login-box input[type="text"]:focus,
.login-box input[type="password"]:focus {
  border-color: #66afe9;
  background-color: #ffffff;
  outline: none;
}

/* Buttons */
.login-box button[type="submit"],
.signup-button {
  width: 100%;
  padding: 14px 20px;
  margin-top: 20px;
  background-color: #4caf50;
  border: none;
  border-radius: 30px;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 700;
}

/* Signup Button */
.signup-button {
  background-color: #007bff;
}

.login-box button[type="submit"]:hover {
  background-color: #45a049;
}

.signup-button:hover {
  background-color: #0069d9;
}

/* Error Message */
.error-message {
  color: #e74c3c;
  margin-top: 15px;
  font-weight: 700;
}

/* Responsive Design */
@media (max-width: 400px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
  }
}
</style>
