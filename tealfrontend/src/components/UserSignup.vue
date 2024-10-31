<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1>Sign Up</h1>
      <form @submit.prevent="signup">
        <input v-model="username" type="text" placeholder="Username" required />
        <input v-model="email" type="email" placeholder="Email" required />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          required
        />
        <input
          v-model="displayName"
          type="text"
          placeholder="Display Name"
          required
        />
        <input v-model="github" type="url" placeholder="GitHub URL" />
        <input
          v-model="profileImage"
          type="url"
          placeholder="Profile Image URL"
        />
        <button type="submit">Sign Up</button>
      </form>
      <button class="login-button" @click="loginRedirect">
        Already have an account? Login
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UserSignup",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      displayName: "",
      github: "",
      profileImage: "",
      error: "",
    };
  },
  methods: {
    async signup() {
      try {
        const response = await axios.post(
          "http://localhost:8000/project/api/signup/",
          {
            username: this.username,
            email: this.email,
            password: this.password,
            displayName: this.displayName,
            github: this.github,
            profileImage: this.profileImage,
          }
        );
        localStorage.setItem("token", response.data.access);
        localStorage.setItem("user", JSON.stringify(response.data.user));
        this.$router.push("/stream");
      } catch (error) {
        this.error = "Signup failed";
      }
    },
    loginRedirect() {
      this.$router.push("/login");
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
.signup-container {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

/* Signup Box */
.signup-box {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 40px 30px;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  text-align: center;
  width: 400px;
}

/* Heading */
.signup-box h1 {
  margin-bottom: 30px;
  color: #333333;
  font-weight: 700;
}

/* Form Inputs */
.signup-box input[type="text"],
.signup-box input[type="email"],
.signup-box input[type="password"],
.signup-box input[type="url"] {
  width: 100%;
  padding: 12px 20px;
  margin: 8px 0;
  border: 1px solid #cccccc;
  border-radius: 30px;
  box-sizing: border-box;
  font-size: 16px;
  background-color: #f7f7f7;
}

/* Form Inputs Focus */
.signup-box input[type="text"]:focus,
.signup-box input[type="email"]:focus,
.signup-box input[type="password"]:focus,
.signup-box input[type="url"]:focus {
  border-color: #66afe9;
  background-color: #ffffff;
  outline: none;
}

/* Buttons */
.signup-box button[type="submit"],
.login-button {
  width: 100%;
  padding: 14px 20px;
  margin-top: 15px;
  background-color: #4caf50;
  border: none;
  border-radius: 30px;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 700;
}

/* Login Button */
.login-button {
  background-color: #007bff;
}

.signup-box button[type="submit"]:hover {
  background-color: #45a049;
}

.login-button:hover {
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
  .signup-box {
    width: 90%;
    padding: 30px 20px;
  }
}
</style>
