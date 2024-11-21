<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>Welcome Back</h1>
        <p>Sign in to connect with your fellow authors</p>
      </div>

      <form @submit.prevent="login">
        <div class="input-group">
          <input 
            v-model="username" 
            type="text" 
            placeholder="Username" 
            required 
            class="modern-input"
          />
        </div>

        <div class="input-group">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            required
            class="modern-input"
          />
          <button 
            type="button"
            class="visibility-toggle"
            @click="showPassword = !showPassword"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>

        <button type="submit" class="modern-button login-button" :disabled="isLoading">
          <span v-if="!isLoading">Login</span>
          <i v-else class="fas fa-spinner fa-spin"></i>
        </button>
      </form>

      <div class="divider">
        <span>OR</span>
      </div>

      <div class="signup-button-container">
        <button class="modern-button signup-button" @click="signupredirect">
          Create New Account
        </button>
      </div>

      <transition name="fade">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </transition>
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
      isLoading: false,
      showPassword: false,
    };
  },
  methods: {
    async login() {
      this.error = "";
      this.isLoading = true;

      try {
        // Attempt to log in the user
        const response = await axios.post("/login/", {
          username: this.username,
          password: this.password,
        });

        // Store authentication tokens and user data
        const accessToken = response.data.access;
        localStorage.setItem("token", accessToken);
        localStorage.setItem("user", JSON.stringify(response.data.user));

        const userId = response.data.user.id;
        const uuid = userId.split("/").pop();
        localStorage.setItem("uuid", uuid);

        // Call the sync posts endpoint
        await this.syncPosts(accessToken);

        // Redirect to the stream page
        this.$router.push("/stream");
      } catch (error) {
        this.error = "Invalid username or password";
      } finally {
        this.isLoading = false;
      }
    },
    async syncPosts(accessToken) {
      try {
        const syncResponse = await axios.get("sync_public_posts/", {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });
        console.log("Sync successful:", syncResponse.data);
      } catch (syncError) {
        console.error("Error syncing posts:", syncError);
        // Optionally display an error message to the user
        // this.error = "Failed to sync posts. Please try again later.";
      }
    },
    signupredirect() {
      this.$router.push("/signup");
    },
  },
};
</script>

<style scoped>
/* Reset default margins and padding */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  height: 100vh; /* Fixed height */
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  background-size: 300% 300%;
  animation: gradient 12s ease infinite;
  /* Remove padding to prevent scrolling */
  padding: 0;
  /* Prevent overflow */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 30px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  /* Prevent overflow */
}

form {
  width: 100%;
  max-width: 340px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  color: #1f2937;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.login-header p {
  color: #6b7280;
  font-size: 16px;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
  width: 100%;
}

.modern-input {
  width: 100%;
  padding: 15px 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  color: #1f2937;
  background: #f9fafb;
  transition: all 0.2s;
  box-sizing: border-box;
}

.modern-input:focus {
  outline: none;
  border-color: #7c3aed;
  background: white;
  box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
}

.visibility-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 5px;
}

.modern-button {
  width: 100%;
  max-width: 340px;
  padding: 15px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-sizing: border-box;
}

.login-button {
  background: #7c3aed;
  color: white;
  margin-top: 10px;
}

.login-button:hover {
  background: #6d28d9;
}

.login-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.divider {
  width: 100%;
  max-width: 340px;
  text-align: center;
  margin: 25px 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background: #e5e7eb;
}

.divider::before { left: 0; }
.divider::after { right: 0; }

.divider span {
  background: white;
  padding: 0 15px;
  color: #6b7280;
  font-size: 14px;
}

.signup-button {
  background: white;
  color: #7c3aed;
  border: 1px solid #7c3aed;
}

.signup-button:hover {
  background: #7c3aed;
  color: white;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
}

@media (max-width: 480px) {
  .login-box {
    padding: 30px 20px;
  }
}
</style>