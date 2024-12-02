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
        <button class="action-button" @click="toggleEdit">
          <i :class="isEditing ? 'fas fa-save' : 'fas fa-edit'"></i>
          {{ isEditing ? 'Save Profile' : 'Edit Profile' }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="profile-banner"></div>
      
      <div class="profile-header">
        <div class="profile-image-container">
          <div class="profile-image-wrapper">
            <img 
              :src="user?.profileImage || defaultProfileImage" 
              :alt="user?.displayName || 'Profile'" 
              class="profile-image"
              @error="handleImageError"
            />
            <button class="edit-image-button" @click="showImageUrlPrompt">
              <i class="fas fa-camera"></i>
            </button>
          </div>
          
          <div class="display-name-container">
            <h1 v-if="!isEditing" class="display-name">{{ user?.displayName || 'Loading...' }}</h1>
            <input
              v-if="isEditing"
              v-model="editedUser.displayName"
              class="edit-input display-name-input"
              type="text"
            />
          </div>
        </div>

        <!-- Stats Section -->
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


        <!-- Profile Details -->
        <div v-if="user" class="profile-details">
          <h2>Personal Information</h2>
          <div class="info-grid">
            <div class="info-card">
              <div class="info-content">
                <div class="info-header">
                  <div class="info-label">
                    <i class="fas fa-user info-icon"></i>
                    <label>Username</label>
                  </div>
                </div>
                <div class="info-value">
                  <span>{{ user.username }}</span>
                </div>
              </div>
            </div>

            <div class="info-card">
              <div class="info-content">
                <div class="info-header">
                  <div class="info-label">
                    <i class="fas fa-envelope info-icon"></i>
                    <label>Email</label>
                  </div>
                </div>
                <div class="info-value">
                  <span v-if="!isEditing">{{ user.email }}</span>
                  <input
                    v-else
                    v-model="editedUser.email"
                    type="email"
                    class="edit-input"
                  />
                </div>
              </div>
            </div>

            <div class="info-card">
              <div class="info-content">
                <div class="info-header">
                  <div class="info-label">
                    <i class="fab fa-github info-icon"></i>
                    <label>GitHub</label>
                  </div>
                </div>
                <div class="info-value">
                  <span v-if="!isEditing">
                    <a v-if="user.github" :href="user.github" target="_blank">{{ user.github }}</a>
                    <span v-else>Not Connected</span>
                  </span>
                  <input
                    v-else
                    v-model="editedUser.github"
                    type="url"
                    class="edit-input"
                    placeholder="Enter GitHub URL"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal Component -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ modalTitle }}</h2>
          <button @click="closeModal" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="loading">Loading...</div>
          <div v-else class="user-list">
            <div v-for="user in modalUsers" :key="user.uuid" class="user-item">
              <img :src="user.profileImage || defaultProfileImage" :alt="user.displayName" class="user-avatar">
              <div class="user-info">
                <span class="user-name">{{ user.displayName }}</span>
                <a :href="user.github" target="_blank" class="user-github" v-if="user.github">
                  <i class="fab fa-github"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal for Image URL Input -->
    <div v-if="showImageUrlModal" class="modal-overlay" @click="closeImageUrlModal">
      <div class="modal-content" @click.stop>
        <h3>Update Profile Picture</h3>
        <input 
          v-model="newImageUrl" 
          type="url" 
          placeholder="Enter image URL"
          class="image-url-input"
        />
        <div class="modal-buttons">
          <button @click="updateProfileImage" class="save-button">Save</button>
          <button @click="closeImageUrlModal" class="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';


export default {
  name: "ProfilePage",
  data() {
    return {
      user: null,
      stats: {
        following: 0,
        followers: 0,
        friends: 0
      },
      showModal: false,
      modalTitle: '',
      modalUsers: [],
      loading: false,
      defaultProfileImage: 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg',
      isEditing: false,
      editedUser: {
        displayName: '',
        username: '',
        email: '',
        github: '',
        profileImage: ''
      },
      imageInput: null,
      showImageUrlModal: false,
      newImageUrl: '',
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
        const url = `/authors/${this.user.uuid}/stats/`;
        
        const response = await axios.get(url, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        console.log('Response:', response.data);
        this.stats.following = response.data.following?.length || 0;
        this.stats.followers = response.data.followers?.length || 0;
        this.stats.friends = response.data.friends?.length || 0;
      } catch (error) {
        console.error("Error fetching stats:", error);
        // More detailed error logging
        if (error.response) {
          console.log('Error status:', error.response.status);
        }
      }
    },
    handleImageError(e) {
      // Fallback if even the default image fails to load
      e.target.src = 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg';
    },
    async showFollowingList() {
      this.modalTitle = 'Following';
      this.showModal = true;
      this.loading = true;
      try {
        const response = await axios.get(
          `/authors/${this.user.uuid}/following/`,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        );
        this.modalUsers = response.data;
      } catch (error) {
        console.error('Error fetching following list:', error);
      }
      this.loading = false;
    },

    async showFollowersList() {
      this.modalTitle = 'Followers';
      this.showModal = true;
      this.loading = true;
      try {
        const response = await axios.get(
          `/authors/${this.user.uuid}/followers/`,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        );
        this.modalUsers = response.data;
      } catch (error) {
        console.error('Error fetching followers list:', error);
      }
      this.loading = false;
    },

    async showFriendsList() {
      this.modalTitle = 'Friends';
      this.showModal = true;
      this.loading = true;
      try {
        const response = await axios.get(
          `/authors/${this.user.uuid}/friends/`,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        );
        this.modalUsers = response.data;
      } catch (error) {
        console.error('Error fetching friends list:', error);
      }
      this.loading = false;
    },

    closeModal() {
      this.showModal = false;
      this.modalUsers = [];
    },
    editProfileImage() {
      // Create a hidden file input
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      
      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          try {
            const formData = new FormData();
            formData.append('profileImage', file);
            const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies
            
            const response = await axios.put(
              `/authors/${this.user.uuid}/`,
              formData,
              {
                headers: {
                  'Authorization': `Token ${localStorage.getItem("token")}`,
                  'Content-Type': 'multipart/form-data',
                  "X-CSRFToken": csrfToken,
                },
              }
            );
            
            this.user.profileImage = response.data.profileImage;
            localStorage.setItem('user', JSON.stringify(this.user));
          } catch (error) {
            console.error('Error uploading profile image:', error);
            alert('Failed to upload image. Please try again.');
          }
        }
      };
      
      input.click();
    },
    toggleEdit() {
      if (this.isEditing) {
        this.saveChanges();
      } else {
        this.startEditing();
      }
    },

    startEditing() {
      this.editedUser = {
        displayName: this.user.displayName,
        email: this.user.email,
        github: this.user.github,
        profileImage: this.user.profileImage
      };
      this.isEditing = true;
    },

    async saveChanges() {
      try {
        const response = await axios.put(
          `/authors/${this.user.uuid}/`,
          this.editedUser,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
              'Content-Type': 'application/json'
            },
          }
        );
        
        // Update local user data
        this.user = { ...this.user, ...response.data };
        localStorage.setItem('user', JSON.stringify(this.user));
        
        this.isEditing = false;
      } catch (error) {
        console.error('Error saving profile changes:', error);
        alert('Failed to save changes. Please try again.');
      }
    },

    showImageUrlPrompt() {
      this.showImageUrlModal = true;
      this.newImageUrl = this.user.profileImage || '';
    },

    closeImageUrlModal() {
      this.showImageUrlModal = false;
      this.newImageUrl = '';
    },

    async updateProfileImage() {
      try {
        await axios.put(
          `/authors/${this.user.uuid}/`,
          { ...this.user, profileImage: this.newImageUrl },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
              'Content-Type': 'application/json'
            },
          }
        );
        
        // Update local user data
        this.user = { ...this.user, profileImage: this.newImageUrl };
        localStorage.setItem('user', JSON.stringify(this.user));
        
        this.closeImageUrlModal();
      } catch (error) {
        console.error('Error updating profile image:', error);
        alert('Failed to update profile image. Please try again.');
      }
    }
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background-color: #3b82f6;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-button:hover {
  background-color: #2563eb;
}

.action-button i {
  font-size: 0.875rem;
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

.profile-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-image-wrapper {
  width: 150px;
  height: 150px;
  position: relative;
  margin-bottom: 1rem;
}

.profile-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.display-name-container {
  text-align: center;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.display-name {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
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
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-content {
  flex: 1;
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

.info-content span, .info-content a {
  color: #1a1a1a;
  text-decoration: none;
  word-break: break-all;
}

.info-content a:hover {
  color: #3b82f6;
}

.stats-container {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin: 2rem 0;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(45deg, #3b82f6, #10b981);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
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

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #374151;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #374151;
}

.modal-body {
  padding: 3rem 1.5rem;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: #d1d5db;
}

.empty-state p {
  margin: 0;
  font-size: 1.1rem;
  color: #6b7280;
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

.edit-button {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.edit-button:hover {
  background: #f3f4f6;
}

.edit-image-button {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.edit-image-button:hover {
  background: #2563eb;
}

.edit-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 1rem;
}

.editable-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.info-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.info-header {
  width: 100%;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: center;
}

.info-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.info-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.info-header {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  position: relative;
}

.info-icon {
  font-size: 1rem;
  color: #3b82f6;
  display: flex;
  align-items: center;
}

.info-header label {
  font-weight: 500;
  color: #6b7280;
  margin: 0;
  display: flex;
  align-items: center;
}

.info-value {
  text-align: center;
  width: 100%;
}

.edit-input {
  width: 80%;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 1rem;
  text-align: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #374151;
}

.image-url-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 1rem;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.save-button, .cancel-button {
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.save-button {
  background-color: #3b82f6;
  color: white;
}

.save-button:hover {
  background-color: #2563eb;
}

.cancel-button {
  background-color: #e5e7eb;
  color: #374151;
}

.cancel-button:hover {
  background-color: #d1d5db;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #d1d5db;
}

.empty-state p {
  margin: 0;
  font-size: 1rem;
}

.modal-body {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  font-size: 2rem;
  color: #3b82f6;
}
</style>