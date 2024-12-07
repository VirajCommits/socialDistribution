<!-- src/pages/StreamPage.vue -->
<template>
  <div class="stream-container">
    <!-- Navigation Bar -->
    <nav class="nav-bar">
      <h1>Social Space</h1>
      <div class="nav-buttons">
        <button class="nav-button explore" @click="goToExploreAuthors">
          <i class="fas fa-compass"></i>
          Explore
        </button>
        <div class="button-wrapper">
          <span v-if="followRequestCount > 0" class="notification-count">
            {{ followRequestCount }}
          </span>
          <button class="nav-button requests" @click="toggleFollowRequests">
            <i class="fas fa-user-plus"></i>
            Requests
          </button>
        </div>
        <button class="nav-button profile" @click="goToProfile">
          <i class="fas fa-user"></i>
          Profile
        </button>
        <button class="nav-button logout" @click="logoutNode">
          <i class="fas fa-sign-out-alt"></i>
          Logout
        </button>
      </div>
    </nav>

    <!-- Follow Requests Modal -->
    <div v-if="followRequestsVisible" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Follow Requests</h2>
          <button class="close-button" @click="toggleFollowRequests">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="followRequests.length" class="requests-list">
            <div
              v-for="request in followRequests"
              :key="request.uuid"
              class="request-item"
            >
              <span class="user-name">{{ request.actor.displayName }}</span>
              <div class="request-actions">
                <button
                  class="accept-btn"
                  @click="acceptFollowRequest(request.actor.uuid)"
                >
                  <i class="fas fa-check"></i> Accept
                </button>
                <button
                  class="decline-btn"
                  @click="declineFollowRequest(request.actor.uuid)"
                >
                  <i class="fas fa-times"></i> Decline
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-requests">
            <i class="fas fa-user-friends"></i>
            <p>No pending follow requests</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-circle-notch fa-spin"></i>
        <p>Loading your feed...</p>
      </div>

      <!-- No Posts State -->
      <div v-else-if="visiblePosts.length === 0" class="empty-state">
        <i class="fas fa-newspaper"></i>
        <h2>Your feed is empty</h2>
        <p>Start following authors to see their posts here</p>
      </div>

      <!-- Posts Feed -->
      <div v-else class="posts-feed">
        <div v-for="post in visiblePosts" :key="post.id" class="post-card">
          <div class="post-header">
            <div class="author-info" @click="navigateToProfile(post.author.uuid)">
              <i class="fas fa-user-circle"></i>
              <span>{{ post.author.displayName }}</span>
            </div>
            <span
              :class="[
                'visibility-badge',
                `visibility-${post.visibility.toLowerCase()}`,
              ]"
            >
              {{ post.visibility }}
            </span>
          </div>

          <div class="post-content">
            <h2 class="post-title" v-html="post.title"></h2>
            <p class="post-description" v-html="post.description"></p>

            <div v-if="isImageContent(post.content)" class="post-image">
              <img :src="extractImageSrc(post.content)" alt="Post Image" />
            </div>
            <div v-else class="post-text" v-html="post.content"></div>
            <button @click="copyToClipboard(post)" class="copy-url-button">
              <i class="fas fa-copy"></i> Copy URL
            </button>
          </div>

          <div class="post-actions">
            <LikeButton :postId="post.id" />
            <CommentSection :postId="post.id" />
          </div>
        </div>
      </div>
    </main>

    <!-- Error Toast -->
    <div v-if="errorMessage" class="error-toast">
      <i class="fas fa-exclamation-circle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import LikeButton from "./LikeButton.vue";
import CommentSection from "./CommentSection.vue";

export default {
  name: "StreamPage",
  components: {
    LikeButton,
    CommentSection,
  },
  data() {
    return {
      posts: [],
      loading: true,
      errorMessage: "",
      user: null,
      authID: "",
      followRequestsVisible: false,
      followRequests: [],
      followRequestCount: 0,
      socket: null,
      inboxActivities: [], // New data property if needed in future
    };
  },
  computed: {
    visiblePosts() {
      return this.posts.filter((post) => post.visibility !== "INVISIBLE");
    },
  },
  async mounted() {
    // Initialize user and fetch posts
    await this.initializeUser();
    await this.fetchStreamPosts();

    if (localStorage.getItem("token")) {
      this.initializeWebSocket();
      await this.fetchInitialCount();
    } else {
      console.error("No authentication token found");
      this.$router.push("/login");
    }
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  },
  methods: {
  navigateToProfile(authorId) {
      this.$router.push({ name: "PublicProfile", params: { authorId } });
    },
  copyToClipboard(post) {
      // Construct a simpler URL for the post
      const postUrl = `${window.location.origin}/posts/${post.id}`;

      navigator.clipboard
        .writeText(postUrl)
        .then(() => {
          alert("URL copied to clipboard!");
        })
        .catch((err) => {
          console.error("Failed to copy: ", err);
          this.errorMessage = "Failed to copy URL.";
        });
    },
    // WebSocket related methods
    initializeWebSocket() {
      const uuid = localStorage.getItem("uuid");
      const token = localStorage.getItem("token");

      if (!uuid || !token) {
        console.error("Missing authentication information");
        return;
      }

      try {
        // Use environment variable or fallback for WebSocket URL
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsBaseUrl = process.env.NODE_ENV === 'production'
          ? window.location.hostname 
          : 'localhost:8000';
        // const wsBaseUrl = window.location.hostname
        
        this.socket = new WebSocket(
          `${wsProtocol}//${wsBaseUrl}/ws/notifications/${uuid}/`
        );

        console.log("Connecting to WebSocket:", this.socket.url); // Debug log

        this.socket.onopen = () => {
          console.log("WebSocket connected successfully");
          this.socket.send(
            JSON.stringify({
              type: "authenticate",
              token: token,
            })
          );
        };

        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === "follow_request") {
            this.followRequestCount = data.count;
            if (this.followRequestsVisible) {
              this.fetchFollowRequests();
            }
          }
        };

        this.socket.onclose = (event) => {
          console.log("WebSocket connection closed:", event.code, event.reason);
          setTimeout(() => {
            if (this.$el && document.body.contains(this.$el)) {
              this.initializeWebSocket();
            }
          }, 5000);
        };

        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
        };
      } catch (error) {
        console.error("Error initializing WebSocket:", error);
      }
    },

    /**
     * Initializes user information from localStorage.
     */
    async initializeUser() {
      try {
        this.user = JSON.parse(localStorage.getItem("user"));
        if (this.user && this.user.id) {
          this.authID = this.user.id.split("/").pop();
        } else {
          throw new Error("User information not found");
        }
      } catch (error) {
        console.error("Error initializing user:", error);
        this.errorMessage = "Failed to retrieve user information.";
      }
    },

    /**
     * Fetches the main stream posts.
     */
    async fetchStreamPosts() {
      try {
        const apiUrl = `/authors/${encodeURIComponent(
          this.authID
        )}/stream/`;

        const response = await axios.get(apiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        this.posts = response.data?.results || [];
        this.loading = false;
      } catch (error) {
        console.error("Error fetching stream posts:", error.response || error);
        this.errorMessage = "An error occurred while fetching stream posts.";
        this.loading = false;
      }
    },

    /**
     * Fetches the initial count of follow requests.
     */
    async fetchInitialCount() {
      try {
        const response = await axios.get(
          "/authors/follow_requests/",
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        );
        this.followRequestCount = response.data.length;
      } catch (error) {
        console.error("Error fetching initial count:", error);
      }
    },

    goToProfile() {
      this.$router.push("/profile");
    },

    goToExploreAuthors() {
      this.$router.push("/explore");
    },

    logoutNode() {
      if (this.socket) {
        this.socket.close();
      }
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("uuid");
      this.$router.push("/login");
    },

    toggleFollowRequests() {
      this.followRequestsVisible = !this.followRequestsVisible;
      if (this.followRequestsVisible) {
        this.fetchFollowRequests();
        this.followRequestCount = 0;
      }
    },

    fetchFollowRequests() {
      axios
        .get(
          `/authors/follow_requests/`,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          this.followRequests = response.data;
        })
        .catch((error) => {
          console.error("Error fetching follow requests:", error);
        });
    },

    acceptFollowRequest(uuid) {
      axios
        .post(
          `/authors/${uuid}/accept_follow_request/`,
          null,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then(() => {
          this.fetchFollowRequests();
          this.followRequestCount = Math.max(0, this.followRequestCount - 1);
        })
        .catch((error) => {
          console.error("Error accepting follow request:", error);
        });
    },
    sendPostsToNode(followerUuid) {
      axios
        .post(
          `/authors/${this.currentUserId}/send_posts_to_node/`,
          { followerUuid },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          console.log("Posts sent successfully:", response.data);
        })
        .catch((error) => {
          console.error("Error sending posts to node:", error);
        });
    },


    declineFollowRequest(uuid) {
      axios
        .post(
          `/authors/${uuid}/decline_follow_request/`,
          null,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then(() => {
          this.fetchFollowRequests();
          this.followRequestCount = Math.max(0, this.followRequestCount - 1);
        })
        .catch((error) => {
          console.error("Error declining follow request:", error);
        });
    },

    isImageContent(content) {
      if (!content) return false;

      // Use regex to extract the data URI
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      return match !== null;
    },

    extractImageSrc(content) {
      if (!content) return "";

      // Extract the data URI using regex
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      return match ? match[0] : "";
    },

    stripHtmlTags(content) {
      if (!content) return "";
      // Remove all HTML tags
      return content.replace(/<\/?[^>]+(>|$)/g, "").trim();
    },
  },
};
</script>

<style scoped>
.stream-container {
  height: 100vh;
  overflow-y: auto;
  background: #f8f9fa;
}

/* Navigation Bar */
.nav-bar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-bar h1 {
  color: #4f46e5;
  font-size: 1.5rem;
  font-weight: 600;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
}

.nav-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-button i {
  font-size: 1rem;
}

.nav-button.explore {
  background: #4f46e5;
  color: white;
}
.nav-button.requests {
  background: #f3f4f6;
  color: #4b5563;
}
.nav-button.profile {
  background: #f3f4f6;
  color: #4b5563;
}
.nav-button.logout {
  background: #ef4444;
  color: white;
}

.nav-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  border: 2px solid white;
}

@keyframes badgePop {
  0% {
    transform: scale(0);
  }
  80% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.notification-badge {
  animation: badgePop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #6b7280;
}

.close-button:hover {
  color: #374151;
}

.modal-body {
  padding: 16px 24px;
}

.no-requests {
  text-align: center;
  padding: 32px 0;
  color: #6b7280;
}

.no-requests i {
  font-size: 2.5rem;
  margin-bottom: 16px;
  color: #9ca3af;
}

.no-requests p {
  font-size: 1rem;
  margin: 0;
}

.requests-list {
  max-height: 400px;
  overflow-y: auto;
}

.request-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.request-item:last-child {
  border-bottom: none;
}

.user-name {
  font-size: 0.95rem;
  color: #1f2937;
}

.request-actions {
  display: flex;
  gap: 8px;
}

.accept-btn,
.decline-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.accept-btn {
  background: #4f46e5;
  color: white;
}

.accept-btn:hover {
  background: #4338ca;
}

.decline-btn {
  background: #ef4444;
  color: white;
}

.decline-btn:hover {
  background: #dc2626;
}

/* Posts Feed */
.main-content {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
  padding-bottom: 2rem;
}

.post-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.post-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.visibility-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.visibility-public {
  background: #dcfce7;
  color: #166534;
}

.visibility-unlisted {
  background: #8e44ad;
  color: #ffffff;
}
.visibility-friends {
  background: #fef3c7;
  color: #92400e;
}
.visibility-private {
  background: #fee2e2;
  color: #991b1b;
}

.post-content {
  padding: 1.5rem;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.post-image img {
  width: 100%;
  border-radius: 8px;
  margin: 1rem 0;
}

.post-actions {
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Error Toast */
.error-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: #fee2e2;
  color: #991b1b;
  padding: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 640px) {
  .nav-bar {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }

  .nav-buttons {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-button {
    flex: 1 1 40%;
    justify-content: center;
  }
}

.button-wrapper {
  position: relative;
  display: inline-block;
}

.notification-count {
  position: absolute;
  top: -10px;
  right: 8px;
  color: #ef4444;
  font-size: 1rem;
  font-weight: 600;
  z-index: 1;
  background: none;
  border: none;
  padding: 0;
}
</style>
