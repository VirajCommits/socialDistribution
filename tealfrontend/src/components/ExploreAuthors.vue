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
              <div class="get-author-stats">
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
              v-if="isFriend(author)"
              @click="handleUnfollow(author)"
              class="friend-button"
            >
              <i class="fas fa-user-friends"></i>
              {{ isRemoteAuthor(author) ? 'Remote Friend' : 'Friend' }}
            </button>
            <button
              v-else-if="isFollowing(author)"
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
              @click="sendFollowRequest(author)"
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
      relationships: {},
      authID: null,
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
    const user = JSON.parse(localStorage.getItem("user"));
    if (user && user.id) {
      this.authID = user.id.split("/").pop(); // Extract the UUID from the user ID
    }
  },
  async mounted() {
    if (this.token) {
      await this.fetchAuthors();
      await this.fetchAllRelationships();
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
          "/authors/",
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        // this.authors = response.data;
        this.authors = response.data.map(author => ({
            ...author,
            host: author.host || window.location.origin + '/'
        }));
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
          `/authors/${this.authID}/inbox/`,
          {
            headers: {
              Authorization: `Token ${this.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        // console.log("Inbox response data:", response.data);
        this.pendingRequests = response.data.items
            .filter(item => item.type === 'follow')
            .map(req => req.object.id);
        console.log("Pending requests:", this.pendingRequests);
      } catch (error) {
        console.error("Error fetching pending requests:", error);
        if (error.response?.status === 401) {
          localStorage.removeItem("token");
          this.$router.push("/login");
        }
      }
    },
    async sendFollowRequest(author) {
    try {
        
        const user = JSON.parse(localStorage.getItem("user"));
        const followRequest = {
            type: "follow",
            summary: `${user.displayName} wants to follow ${author.displayName}`,
            actor: {
                type: "author",
                id: user.id,
                host: user.host || window.location.origin + '/',
                displayName: user.displayName,
                github: user.github || "",
                profileImage: user.profileImage || "",
                page: `${user.host || window.location.origin + '/'}authors/${user.uuid}`
            },
            object: {
                type: "author",
                id: author.id,
                host: author.host,
                displayName: author.displayName,
                github: author.github || "",
                profileImage: author.profileImage || "",
                page: author.page || `${author.host}authors/${author.uuid}`
            }
        };
        console.log("aaaaaaaaaaaaaaaaaaaa: ", author.host)
        const targetUrl = author.host && author.host !== window.location.origin + '/' ?
            `${author.host}service/api/authors/${author.id.split('/').pop()}/inbox/` :
            `/authors/${author.id.split("/").pop()}/inbox/`;

        await axios.post(
            targetUrl,
            followRequest,
            {
                headers: { 
                    Authorization: `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        this.showNotification(
            "Follow request sent successfully!",
            "success",
            "fas fa-user-plus"
        );
        this.pendingRequests.push(author.id);
        console.log("requests: ", this.pendingRequests);
        await this.fetchAuthors();
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
          `/authors/${authorUUID}/remove_follow_request/`,
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
    async fetchRelationshipStatus(author) {
        try {
            const authorUUID = author.id.split("/").pop();
            const response = await axios.get(
                `/authors/${authorUUID}/relationship/`,
                {
                    headers: { Authorization: `Token ${this.token}` }
                }
            );
            this.relationships[author.id] = response.data;
        } catch (error) {
            console.error("Error fetching relationship status:", error);
        }
    },

    // async fetchAllRelationships() {
    //     for (const author of this.authors) {
    //         await this.fetchRelationshipStatus(author);
    //     }
    // },
    async fetchAllRelationships() {
    try {
        const user = JSON.parse(localStorage.getItem("user"));
        this.relationships = {};  // Reset relationships

        // Get followers
        const followersResponse = await axios.get(
            `/authors/${user.uuid}/followers/`,
            { headers: { Authorization: `Token ${this.token}` } }
        );
        
        // Get following
        const followingResponse = await axios.get(
            `/authors/${user.uuid}/following/`,
            { headers: { Authorization: `Token ${this.token}` } }
        );

        // Add null check and ensure data structure exists
        const followers = followersResponse.data.followers || [];
        console.log("this is followers: ", followers)
        const following = followingResponse.data || [];
        console.log("this is following: ", following)

        // Process all authors and their relationships
        this.authors.forEach(author => {
            const authorId = author.id;  // Full URL for remote authors
            const isFollower = followers.some(
                follower => follower.id === authorId
            );
            const isFollowing = following.some(
                following => following.id === authorId
            );

            this.relationships[authorId] = {
                is_following: isFollowing,
                is_follower: isFollower,
                is_friend: isFollower && isFollowing,
                host: author.host || window.location.origin + '/',
                pending: this.pendingRequests.includes(authorId)
            };
        });
    } catch (error) {
        console.error("Error fetching relationships:", error);
        this.showNotification(
            "Failed to fetch relationships",
            "error",
            "fas fa-exclamation-circle"
        );
    }
},
async checkIsFollower(authorId) {
    try {
        const user = JSON.parse(localStorage.getItem("user"));
        const response = await axios.get(
            `/authors/${user.uuid}/followers/${encodeURIComponent(authorId)}/`,
            {
                headers: { Authorization: `Token ${this.token}` }
            }
        );
        return response.status === 200;
    } catch (error) {
        if (error.response && error.response.status === 404) {
            return false;
        }
        console.error("Error checking follower status:", error);
        return false;
    }
  },

    isRemoteAuthor(author) {
        return author.host && author.host !== window.location.origin + '/';
    },
    getAuthorId(author) {
        return this.isRemoteAuthor(author) ? 
            author.id : 
            author.id.split('/').pop();
    },
    getAuthorHost(author) {
        return author.host || window.location.origin + '/';
    },
    isFriend(author) {
        return this.relationships[author.id]?.is_friend || false;
    },
    isFollowing(author) {
        return this.relationships[author.id]?.is_following || false;
    },
    hasPendingRequest(author) {
      console.log("author : ", author);
      console.log("haspedignauthour: ", author.id);
      console.log("pending requests: ", this.pendingRequests);
      return this.pendingRequests.includes(author.id.split("/").pop());
    },
    startPolling() {
      this.pollInterval = setInterval(() => {
        this.fetchAuthors();
        this.fetchAllRelationships();
      }, 5000); // Poll every 5 seconds
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
      }
    },
    setupWebSocket() {
      const uuid = localStorage.getItem("uuid");
      if (!uuid) {
        console.log('No UUID found, skipping WebSocket setup');
        return;
      }

      // Check if we're in production
      const isProduction = window.location.hostname.includes('herokuapp.com');
      
      // Set up the WebSocket URL based on environment
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsHost = isProduction 
        ? 'teal-rakshit-a972530cc317.herokuapp.com'  // Production host
        : 'localhost:8000';                          // Development host
      
      const wsUrl = `${wsProtocol}://${wsHost}/ws/notifications/${uuid}/`;
      
      console.log('Setting up WebSocket connection to:', wsUrl);
      
      const ws = new WebSocket(wsUrl);

      // WebSocket event handlers
      ws.onopen = () => {
        console.log('WebSocket connected successfully');
      };

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received WebSocket message:', data);
          
          if (data.type === "follow_request_notification") {
            await this.fetchAuthors();
            await this.fetchAllRelationships();
            await this.fetchPendingRequests();

            if (data.message) {
              this.showNotification(data.message, "info", "fas fa-bell");
            }
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed, attempting to reconnect...');
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
        const user = JSON.parse(localStorage.getItem("user"));
        const unfollowRequest = {
            type: "unfollow",
            summary: `${user.displayName} unfollowed ${this.selectedAuthor.displayName}`,
            actor: {
                type: "author",
                id: user.id,
                host: user.host || window.location.origin + '/',
                displayName: user.displayName
            },
            object: {
                type: "author",
                id: this.selectedAuthor.id,
                host: this.selectedAuthor.host,
                displayName: this.selectedAuthor.displayName
            }
        };

        const targetUuid = this.selectedAuthor.id.split("/").pop();
        const response = await axios.post(
            `/authors/${targetUuid}/inbox/`,
            unfollowRequest,
            {
                headers: { 
                    Authorization: `Token ${this.token}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        if (response.status === 200) {
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
            await this.fetchAuthors();
            await this.fetchAllRelationships();
        }
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

.get-author-stats {
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
.friend-button,
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

.friend-button {
  background: #c233ea;
  color: white;
}

.following-button:hover {
  background: #ff4444;
}

.friend-button:hover {
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
