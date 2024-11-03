<template>
  <div class="explore-container">
    <div class="explore-header">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <i class="fas fa-arrow-left"></i>
        </button>
        <h1>Explore Authors</h1>
        <div class="spacer"></div>
      </div>
    </div>

    <div class="explore-content">
      <p class="explore-description">
        Discover and connect with other authors in the community
      </p>

      <div v-if="authors.length" class="authors-grid">
        <div v-for="author in authors" :key="author.id" class="author-card">
          <div class="author-content">
            <div class="author-avatar">
              <img
                v-if="author.profileImage"
                :src="author.profileImage"
                :alt="`${author.displayName}'s profile`"
                class="profile-image"
                @error="$event.target.style.display = 'none'"
              />
              <i v-else class="fas fa-user-circle default-avatar"></i>
            </div>

            <div class="author-info">
              <h2 class="author-name">{{ author.displayName }}</h2>
              <div class="author-stats">
                <span class="stat">
                  <i class="fab fa-github"></i>
                  <a
                    v-if="author.github"
                    :href="author.github"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="github-link"
                  >
                    {{ author.github.split("/").pop() }}
                  </a>
                  <span v-else class="no-github">Not connected</span>
                </span>
                <span class="stat">
                  <i class="fas fa-users"></i>
                  {{ author.followers?.length || 0 }} Followers
                </span>
              </div>
            </div>

            <button
              v-if="isFollowing(author)"
              @click="handleUnfollow(author)"
              class="following-button"
            >
              <i class="fas fa-user-check"></i> Following
            </button>
            <button
              v-else-if="hasPendingRequest(author)"
              @click="handlePendingRequest(author)"
              class="pending-button"
            >
              <i class="fas fa-clock"></i> Request Pending
            </button>
            <button
              v-else
              @click="sendFollowRequest(author.id)"
              class="follow-button"
            >
              <i class="fas fa-user-plus"></i> Follow
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-authors">
        <p>Nobody else here yet.</p>
      </div>
    </div>

    <!-- Unfollow Modal -->
    <div v-if="showUnfollowModal" class="modal">
      <div class="modal-content">
        <h3>Confirm Unfollow</h3>
        <p>
          Are you sure you want to unfollow {{ selectedAuthor?.displayName }}?
        </p>
        <div class="modal-buttons">
          <button @click="confirmUnfollow" class="unfollow-button">Yes</button>
          <button @click="showUnfollowModal = false" class="cancel-button">
            No
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="notification.show"
      class="notification-toast"
      :class="notification.type"
    >
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ExploreAuthors",
  data() {
    return {
      authors: [],
      pendingRequests: [],
      following: [],
      token: localStorage.getItem("token"),
      showUnfollowModal: false,
      selectedAuthor: null,
      notification: {
        show: false,
        message: "",
        type: "success",
        icon: "fas fa-check-circle",
      },
    };
  },
  created() {
    // Check if user is authenticated
    if (!this.token) {
      this.$router.push("/login");
      return;
    }
  },
  mounted() {
    if (this.token) {
      this.fetchAuthors();
      this.startPolling();
      this.setupWebSocket();
    }
  },
  methods: {
    async fetchAuthors() {
      if (!this.token) {
        this.showNotification(
          "Authentication required",
          "error",
          "fas fa-lock"
        );
        this.$router.push("/login");
        return;
      }

      try {
        const response = await axios.get(
          "http://localhost:8000/service/api/authors/",
          {
            headers: {
              Authorization: `Token ${this.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        this.authors = response.data;
        await this.fetchPendingRequests();
      } catch (error) {
        console.error("Error fetching authors:", error);
        if (error.response?.status === 401) {
          this.showNotification(
            "Session expired. Please login again",
            "error",
            "fas fa-lock"
          );
          this.$router.push("/login");
        } else {
          this.showNotification(
            "Failed to load authors",
            "error",
            "fas fa-exclamation-circle"
          );
        }
      }
    },
    goBack() {
      this.$router.push("/stream");
    },
    async fetchPendingRequests() {
      if (!this.token) return;

      try {
        const response = await axios.get(
          "http://localhost:8000/service/api/authors/pending_requests/",
          {
            headers: {
              Authorization: `Token ${this.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        this.pendingRequests = response.data.map((req) => req.object.id);
      } catch (error) {
        console.error("Error fetching pending requests:", error);
        if (error.response?.status === 401) {
          localStorage.removeItem("token");
          this.$router.push("/login");
        }
      }
    },
    async sendFollowRequest(authorId) {
      try {
        const targetUuid = authorId.split("/").pop();
        await axios.post(
          `http://localhost:8000/service/api/authors/${targetUuid}/send_follow_request/`,
          null,
          {
            headers: { Authorization: `Token ${this.token}` },
          }
        );

        this.showNotification(
          "Follow request sent successfully!",
          "success",
          "fas fa-user-plus"
        );
        this.pendingRequests.push(authorId);
        this.fetchAuthors();
      } catch (error) {
        this.showNotification(
          "Failed to send follow request",
          "error",
          "fas fa-exclamation-circle"
        );
        console.error("Error sending follow request:", error);
      }
    },
    async handlePendingRequest(author) {
      try {
        const authorUUID = author.id.split("/").pop();
        await axios.delete(
          `http://localhost:8000/service/api/authors/${authorUUID}/remove_follow_request/`,
          {
            headers: { Authorization: `Token ${this.token}` },
          }
        );

        this.showNotification(
          "Follow request removed",
          "success",
          "fas fa-user-clock"
        );
        this.pendingRequests = this.pendingRequests.filter(
          (id) => id !== author.id
        );
        this.fetchAuthors();
      } catch (error) {
        this.showNotification(
          "Failed to remove follow request",
          "error",
          "fas fa-exclamation-circle"
        );
        console.error("Error removing follow request:", error);
      }
    },
    isFollowing(author) {
      const currentUserUUID = localStorage.getItem("uuid");
      return author.followers?.some((follower) =>
        typeof follower === "string"
          ? follower.includes(currentUserUUID)
          : follower.uuid === currentUserUUID
      );
    },
    hasPendingRequest(author) {
      return this.pendingRequests.includes(author.id);
    },
    startPolling() {
      this.pollInterval = setInterval(() => {
        this.fetchAuthors();
      }, 5000); // Poll every 5 seconds
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
      }
    },
    setupWebSocket() {
      const uuid = localStorage.getItem("uuid");
      if (!uuid) return;

      const ws = new WebSocket(`ws://localhost:8000/ws/notifications/${uuid}/`);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "follow_request_notification") {
          // Refresh the data when a follow request is updated
          this.fetchAuthors();
          this.fetchPendingRequests();

          // Show notification to user
          if (data.message) {
            alert(data.message);
          }
        }
      };

      ws.onclose = () => {
        // Attempt to reconnect after a delay
        setTimeout(() => this.setupWebSocket(), 1000);
      };

      this.ws = ws;
    },
    beforeDestroy() {
      if (this.ws) {
        this.ws.close();
      }
      this.stopPolling();
    },
    async handleUnfollow(author) {
      this.selectedAuthor = author;
      this.showUnfollowModal = true;
    },
    async confirmUnfollow() {
      try {
        const authorUUID = this.selectedAuthor.id.split("/").pop();
        await axios.delete(
          `http://localhost:8000/service/api/authors/${authorUUID}/unfollow/`,
          null,
          {
            headers: { Authorization: `Token ${this.token}` },
          }
        );

        this.showNotification(
          "Successfully unfollowed author",
          "success",
          "fas fa-user-minus"
        );
        this.following = this.following.filter(
          (id) => id !== this.selectedAuthor.id
        );
        this.showUnfollowModal = false;
        this.selectedAuthor = null;
        this.fetchAuthors();
      } catch (error) {
        this.showNotification(
          "Failed to unfollow author",
          "error",
          "fas fa-exclamation-circle"
        );
        console.error("Error unfollowing author:", error);
      }
    },
    showNotification(message, type = "success", icon = "fas fa-check-circle") {
      this.notification = {
        show: true,
        message,
        type,
        icon,
      };

      setTimeout(() => {
        this.notification.show = false;
      }, 3000);
    },
  },
  beforeUnmount() {
    this.stopPolling(); // Clean up when component unmounts
  },
};
</script>

<style scoped>
.explore-container {
  height: 100vh;
  overflow-y: auto;
  background: #f8fafc;
}

.explore-header {
  position: sticky;
  top: 0;
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  z-index: 10;
  text-align: center;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.back-button {
  position: absolute;
  left: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #42b983;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-button:hover {
  background: #4f46e5;
}

h1 {
  margin: 0;
  color: #4f46e5;
  font-size: 1.5rem;
  font-weight: 600;
}

.explore-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.explore-description {
  text-align: center;
  color: #6b7280;
  margin-bottom: 2rem;
}

.authors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.author-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.author-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  font-size: 2.5rem;
  color: #9ca3af;
}

.author-info {
  text-align: center;
  width: 100%;
}

.author-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0.5rem 0;
}

.author-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
  font-size: 0.875rem;
}

.github-link {
  color: #42b983;
  text-decoration: none;
  transition: color 0.2s;
}

.github-link:hover {
  text-decoration: underline;
}

.no-github {
  color: #9ca3af;
  font-style: italic;
}

/* Button styles */
.follow-button,
.following-button,
.pending-button {
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.follow-button {
  background: #4f46e5;
  color: white;
}

.follow-button:hover {
  background: #4f46e5;
}

.following-button {
  background: #42b983;
  color: white;
}

.following-button:hover {
  background: #ff4444;
}

.pending-button {
  background: #ffa500;
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  text-align: center;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.unfollow-button {
  background-color: #ff4444;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.unfollow-button:hover {
  background-color: #cc0000;
}

.cancel-button {
  background-color: #666;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.cancel-button:hover {
  background-color: #444;
}

@media (max-width: 768px) {
  .explore-header {
    padding: 1rem;
  }

  .explore-content {
    padding: 1rem;
  }

  .authors-grid {
    grid-template-columns: 1fr;
  }
}

.notification-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease-out forwards;
  z-index: 1000;
  min-width: 300px;
  justify-content: center;
}

.notification-toast.success {
  background: #4f46e5;
  color: white;
}

.notification-toast.error {
  background: #ef4444;
  color: white;
}

.notification-toast.warning {
  background: #f59e0b;
  color: white;
}

.notification-toast i {
  font-size: 1.25rem;
}

@keyframes slideUp {
  from {
    transform: translate(-50%, 100%);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
</style>
