<template>
  <div class="profile-container">
    <!-- Top Navigation -->
    <div class="top-nav">
      <button class="back-button" @click="backToStream">
        <i class="fas fa-arrow-left"></i>
      </button>
      <div class="nav-actions">
        <button class="action-button" @click="makePost">
          <i class="fas fa-plus"></i> Create Post
        </button>
        <button class="action-button" @click="showPost">
          <i class="fas fa-list"></i> View Posts
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="profile-banner"></div>

      <!-- Profile Header with Display-Only Information -->
      <div class="profile-header">
        <div class="profile-image-wrapper">
          <img
            :src="user?.profileImage || 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'"
            :alt="user?.displayName || 'Profile'"
            class="profile-image"
            @error="handleImageError"
          />
        </div>
        <h1 class="display-name">{{ user?.displayName || 'Loading...' }}</h1>
        
        <!-- Stats Section (Display-Only) -->
        <div class="stats-container">
          <div class="stat-card" v-for="(value, key) in stats" :key="key">
            <div class="stat-value">
              <span class="stat-number">{{ value }}</span>
              <span class="stat-label">{{ key.toUpperCase() }}</span>
            </div>
            <div class="stat-icon">
              <i :class="getStatIcon(key)"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Display-Only Information -->
      <div class="profile-details">
        <h2>Profile Information</h2>
        <div class="info-grid">
          <div class="info-card">
            <i class="fas fa-user"></i>
            <div class="info-content">
              <label>Username: </label>
              <span>{{ user.username }}</span>
            </div>
          </div>
          <div class="info-card">
            <i class="fas fa-user"></i>
            <div class="info-content">
              <label>Github: </label>
              <span>{{ user.github || "Not provided" }}</span>
            </div>
          </div>
          <div class="info-card">
            <i class="fas fa-envelope"></i>
            <div class="info-content">
              <label>Email: </label>
              <span>{{ user.email }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Editable Form for User Profile -->
      <div class="editable-form">
        <h2>Edit Profile</h2>
        <form @submit.prevent="saveProfile">
          <div class="form-group">
            <label for="displayName">Display Name:</label>
            <input v-model="user.displayName" id="displayName" required />
          </div>
          <div class="form-group">
            <label for="github">GitHub:</label>
            <input v-model="user.github" id="github" placeholder="GitHub URL" />
          </div>
          <div class="form-group">
            <label for="profileImage">Profile Image URL:</label>
            <input v-model="user.profileImage" id="profileImage" placeholder="Profile Image URL" />
          </div>
          <button type="submit">Save Changes</button>
          <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "ProfilePage",
  data() {
    return {
      user: JSON.parse(localStorage.getItem("user")),
      stats: { following: 0, followers: 0, friends: 0 },
      successMessage: '',
      errorMessage: ''
    };
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    backToStream() {
      this.$router.push("/stream");
    },
    makePost() {
      this.$router.push("/addPost");
    },
    showPost() {
      this.$router.push("/posts/all");
    },
    async fetchStats() {
      // Fetch stats data here
    },
    async saveProfile() {
      try {
        const url = `http://localhost:8000/service/api/authors/${this.user.uuid}/`;
      
        const response = await axios.post(url, this.user, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });

        localStorage.setItem("user", JSON.stringify(response.data));
        this.successMessage = "Profile updated successfully!";
        this.errorMessage = '';
      } catch (error) {
        this.errorMessage = "Error updating profile. Please try again.";
        this.successMessage = '';
      }
    },
    getStatIcon(key) {
      const icons = {
        following: "fas fa-user-plus",
        followers: "fas fa-users",
        friends: "fas fa-user-friends"
      };
      return icons[key] || "fas fa-info-circle";
    }
  }
};
</script>

<style scoped>

.profile-container {
  min-height: 100vh;
  overflow-y: auto;
  background-color: #f8f9fa;
  padding-top: 80px;

}
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.back-button,
.action-button {
  border: none;
  background-color: #f0f2f5;
  color: #1a1a1a;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.back-button:hover,
.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-header {
  text-align: center;
  margin-top: 1rem;
  margin-bottom: 2rem;
}

.profile-image-wrapper {
  margin: 0 auto;
  width: 150px;
  height: 150px;
}

.profile-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 5px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.display-name {
  margin-top: 1rem;
  font-size: 1.8rem;
  color: #1a1a1a;
}

.main-content {
  padding: 1rem 2rem;
  max-width: 800px;
  margin: auto;
}

.stats-container {
  display: flex;
  justify-content: space-around;
  margin: 2rem 0;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
  flex: 1;
  margin: 0 0.5rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 0.3rem;
}

.profile-details h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #1a1a1a;
  font-size: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  padding: 0 1rem;
}

.info-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.info-content label {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.info-content span,
.info-content a {
  color: #1a1a1a;
  word-break: break-all;
  text-decoration: none;
}

@media (max-width: 768px) {
  .nav-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}

  .profile-image-wrapper {
    width: 120px;
    height: 120px;
  }

  .stats-container {
    flex-direction: column;
  }

  .stat-card {
    margin: 0.5rem 0;
  }


.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1rem;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-item:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-name {
  font-weight: 500;
}

.user-github {
  color: #333;
  text-decoration: none;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>


