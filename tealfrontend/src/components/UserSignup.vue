<template>
  <div class="signup-container">
    <div class="signup-box">
      <div class="signup-header">
        <h1>Create Account</h1>
        <p>Join our community of authors</p>
      </div>

      <form @submit.prevent="signup">
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
            v-model="email" 
            type="email" 
            placeholder="Email" 
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

        <div class="input-group">
          <input
            v-model="displayName"
            type="text"
            placeholder="Display Name"
            required
            class="modern-input"
          />
        </div>

        <div class="input-group">
          <input 
            v-model="github" 
            type="url" 
            placeholder="GitHub URL (Optional)" 
            class="modern-input"
          />
        </div>

        <div class="input-group">
          <input
            v-model="profileImage"
            type="url"
            placeholder="Profile Image URL (Optional)"
            class="modern-input"
          />
        </div>

        <button type="submit" class="modern-button signup-button" :disabled="isLoading">
          <span v-if="!isLoading">Create Account</span>
          <i v-else class="fas fa-spinner fa-spin"></i>
        </button>
      </form>

      <div class="divider">
        <span>OR</span>
      </div>

      <button class="modern-button login-redirect" @click="loginRedirect">
        Already have an account? Sign in
      </button>

      <transition name="fade">
        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
      </transition>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.signup-container {
  min-height: 100vh;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.signup-box {
  background: white;
  padding: 30px;
  border-radius: 30px;
  width: 100%;
  max-width: 460px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-height: 100vh;
}

.signup-header {
  text-align: center;
  margin-bottom: 20px;
}

.signup-header h1 {
  color: #1f2937;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.signup-header p {
  color: #6b7280;
  font-size: 16px;
}

.input-group {
  position: relative;
  margin-bottom: 12px;
  width: 100%;
}

.modern-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  color: #1f2937;
  background: #f9fafb;
  transition: all 0.2s;
}

.modern-input:focus {
  outline: none;
  border-color: #7c3aed;
  background: white;
  box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
}

.modern-input::placeholder {
  color: #9ca3af;
}

.modern-input:focus::placeholder {
  color: #d1d5db;
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
  padding: 15px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.signup-button {
  background: #7c3aed;
  color: white;
  margin-top: 5px;
}

.signup-button:hover {
  background: #6d28d9;
}

.signup-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.divider {
  text-align: center;
  margin: 15px 0;
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

.login-redirect {
  background: white;
  color: #7c3aed;
  border: 1px solid #7c3aed;
}

.login-redirect:hover {
  background: #7c3aed;
  color: white;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

@media (max-width: 480px) {
  .signup-box {
    padding: 25px 20px;
    margin: 15px;
  }
}

.required-label::after {
  content: " *";
  color: #dc2626;
  font-weight: bold;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  color: #4b5563;
  font-size: 14px;
}
</style>

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
      isLoading: false,
      showPassword: false
    };
  },
  methods: {
    async signup() {
      this.error = "";
      this.isLoading = true;
      
      try {
        const response = await axios.post(
          "/service/api/signup/",
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
        this.error = "Signup failed. Please check your information and try again.";
      } finally {
        this.isLoading = false;
      }
    },
    loginRedirect() {
      this.$router.push("/login");
    },
  },
};
</script>
