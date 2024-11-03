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

      <div class="profile-header">
        <div class="profile-image-wrapper">
          <img
            :src="
              user?.profileImage ||
              'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
            "
            :alt="user?.displayName || 'Profile'"
            class="profile-image"
            @error="handleImageError"
          />
        </div>
        <h1 class="display-name">{{ user?.displayName || "Loading..." }}</h1>

        <!-- New Stats Section -->
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-value">
              <span class="stat-number">{{ stats.following }}</span>
              <span class="stat-label">FOLLOWING</span>
            </div>
            <div class="stat-icon">
              <i class="fas fa-user-plus"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-value">
              <span class="stat-number">{{ stats.followers }}</span>
              <span class="stat-label">FOLLOWERS</span>
            </div>
            <div class="stat-icon">
              <i class="fas fa-users"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-value">
              <span class="stat-number">{{ stats.friends }}</span>
              <span class="stat-label">FRIENDS</span>
            </div>
            <div class="stat-icon">
              <i class="fas fa-user-friends"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Details -->
      <div v-if="user" class="profile-details">
        <h2>Personal Information</h2>
        <div class="info-grid">
          <div class="info-card">
            <i class="fas fa-user"></i>
            <div class="info-content">
              <label>Username</label>
              <span>{{ user.username }}</span>
            </div>
          </div>

          <div class="info-card">
            <i class="fas fa-envelope"></i>
            <div class="info-content">
              <label>Email</label>
              <span>{{ user.email }}</span>
            </div>
          </div>

          <div class="info-card">
            <i class="fab fa-github"></i>
            <div class="info-content">
              <label>GitHub</label>
              <span v-if="user.github">
                <a :href="user.github" target="_blank">{{ user.github }}</a>
              </span>
              <span v-else>Not Connected</span>
            </div>
          </div>

          <div class="info-card">
            <i class="fas fa-globe"></i>
            <div class="info-content">
              <label>Personal Page</label>
              <a :href="user.page" target="_blank">{{ user.page }}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProfilePage",
  data() {
    return {
      user: null,
      stats: {
        following: 0,
        followers: 0,
        friends: 0,
      },
    };
  },
  async mounted() {
    this.user = JSON.parse(localStorage.getItem("user"));
    if (this.user) {
      await this.fetchStats();
    }
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
      try {
        // Debug logs
        console.log("User data:", this.user);
        console.log("User UUID:", this.user.uuid);
        const url = `http://localhost:8000/service/api/authors/${this.user.uuid}/stats/`;
        console.log("Requesting URL:", url);

        const response = await axios.get(url, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        console.log("Response:", response.data);
        this.stats = response.data;
      } catch (error) {
        console.error("Error fetching stats:", error);
        // More detailed error logging
        if (error.response) {
          console.log("Error status:", error.response.status);
        }
      }
    },
    handleImageError(e) {
      // Fallback if even the default image fails to load
      e.target.src =
        "https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg";
    },
  },
};
</script>

<style scoped>
/* General Container Styling */

.profile-container {
  height: 100vh;
  overflow-y: auto;
  background-color: #f8f9fa;
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

.back-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: #f0f2f5;
  color: #1a1a1a;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  background: linear-gradient(45deg, #3b82f6, #10b981);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-button:hover,
.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-banner {
  height: 250px;
  background: linear-gradient(45deg, #3b82f6, #10b981);
  margin-bottom: 80px;
}

.profile-header {
  text-align: center;
  margin-top: -125px;
  margin-bottom: 3rem;
}

.profile-image-wrapper {
  margin: 0 auto;
  width: 200px;
  height: 200px;
}

.profile-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 8px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.display-name {
  margin-top: 1rem;
  font-size: 2rem;
  color: #1a1a1a;
}

.profile-details {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-details h2 {
  text-align: center;
  margin-bottom: 3rem;
  color: #1a1a1a;
  font-size: 1.8rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 0 1rem;
}

.info-card {
  background: white;
  padding: 2rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.info-card i {
  font-size: 1.8rem;
  color: #3b82f6;
}

.info-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.info-content label {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 0.8rem;
  font-weight: 600;
}

.info-content span,
.info-content a {
  color: #1a1a1a;
  text-decoration: none;
  word-break: break-all;
}

.info-content a:hover {
  color: #3b82f6;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 2rem auto;
  max-width: 800px;
  padding: 0 1rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(45deg, #3b82f6, #10b981);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-value {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 1px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(45deg, #3b82f6, #10b981);
  color: white;
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .top-nav {
    padding: 1rem;
  }

  .nav-actions {
    flex-direction: column;
    gap: 0.5rem;
  }

  .action-button {
    font-size: 0.8rem;
  }

  .profile-banner {
    height: 150px;
  }

  .profile-image-wrapper {
    width: 120px;
    height: 120px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .stats-container {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 0 1rem;
  }

  .stat-card {
    padding: 1.2rem;
  }

  .stat-number {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.7rem;
  }

  .stat-icon {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }
}
</style>
