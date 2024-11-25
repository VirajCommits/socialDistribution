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
        <div
          v-for="author in authors"
          :key="author.id"
          class="author-card"
          @click="navigateToProfile(author.uuid)"
          style="cursor: pointer;"
        >

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
          </div>

          <!-- Follow/Unfollow Buttons -->
          <button
            v-if="isFriend(author)"
            @click.stop="handleUnfollow(author)"
            class="friend-button"
          >
            <i class="fas fa-user-friends"></i> Friend
          </button>
          <button
            v-else-if="isFollowing(author)"
            @click.stop="handleUnfollow(author)"
            class="following-button"
          >
            <i class="fas fa-user-check"></i> Following
          </button>
          <button
            v-else-if="hasPendingRequest(author)"
            @click.stop="handlePendingRequest(author)"
            class="pending-button"
          >
            <i class="fas fa-clock"></i> Request Pending
          </button>
          <button
            v-else
            @click.stop="sendFollowRequest(author.id)"
            class="follow-button"
          >
            <i class="fas fa-user-plus"></i> Follow
          </button>
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
// import Cookies from 'js-cookie';


export default {
  name: "ExploreAuthors",
  data() {
    return {
      authors: [],
      pendingRequests: [],
      following: [],
      relationships: {},
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
  async mounted() {
    if (this.token) {
      await this.fetchAuthors();
      await this.fetchAllRelationships();
      this.startPolling();
      this.setupWebSocket();
    }
  },
  methods: {
    navigateToProfile(authorId) {
      this.$router.push({ name: "PublicProfile", params: { authorId } });
    },
    async fetchAuthors() {
      if (!this.token) {
        this.showNotification("Authentication required", "error", "fas fa-lock");
        this.$router.push("/login");
        return;
      }

      try {
        const response = await axios.get("/authors/", {
          headers: {
            Authorization: `Token ${this.token}`,
            "Content-Type": "application/json",
          },
        });

        console.log(response.data); // This will help you understand the response format

        // Handling different formats of response
        if (Array.isArray(response.data)) {
          this.authors = response.data.map((author) => ({
            ...author,
            username: author.id.split("/").pop(),
          }));
        } else if (response.data.authors && Array.isArray(response.data.authors)) {
          this.authors = response.data.authors.map((author) => ({
            ...author,
            username: author.id.split("/").pop(),
          }));
        } else {
          console.error("Unexpected data format:", response.data);
          this.authors = [];
        }

        await this.fetchPendingRequests();
      } catch (error) {
        console.error("Error fetching authors:", error);
        if (error.response?.status === 401) {
          this.showNotification("Session expired. Please login again", "error", "fas fa-lock");
          this.$router.push("/login");
        } else {
          this.showNotification("Failed to load authors", "error", "fas fa-exclamation-circle");
        }
      }
    },

    goBack() {
      this.$router.push("/stream");
    },
    async fetchPendingRequests() {
      if (!this.token) return;

      try {
        const response = await axios.get("/authors/pending_requests/", {
          headers: {
            Authorization: `Token ${this.token}`,
            "Content-Type": "application/json",
          },
        });
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
  console.log("This is the authorID: ", authorId);
  try {
    const targetUuid = authorId.split("/").pop();
    const targethost = authorId.split('/authors/')[0];
    console.log("This is the host: ", targethost);

    // Fetch the list of connected nodes
    const response = await axios.get('/connected-nodes/', {
      headers: { Authorization: `Token ${this.token}` },
    });
    const connectedNodes = response.data;
    console.log(connectedNodes);

    const targetNode = connectedNodes.find(node => node.url === targethost);
    console.log("This is the target node: ", targetNode);

    const user = JSON.parse(localStorage.getItem("user"));
    console.log("This is the user: ", user);

    // Get the target author's full data from the authors array
    const targetAuthor = this.authors.find(author => author.id === authorId);

    const followActivity = {
      type: "Follow",
      summary: `${user.displayName} wants to follow ${targetAuthor.displayName}`,
      actor: {
        type: "author",
        id: user.id,
        host: user.host,
        displayName: user.displayName,
        github: user.github || "",
        profileImage: user.profileImage || "",
        url: user.url || user.page
      },
      object: targetAuthor // The target author already has all required fields
    };

    if (targetNode) {
      // Define the endpoint on your server
      const endpoint = `/authors/${targetUuid}/sendRemoteRequest/`;
      // const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies

      // Send the follow request to your server's sendRemoteRequest endpoint
      await axios.post(
        endpoint,
        followActivity,
        {
          headers: {
            Authorization: `Token ${this.token}`,
            'Content-Type': 'application/json',
            
          }
        }
      );

      this.showNotification(
        "Follow request sent successfully!",
        "success",
        "fas fa-user-plus"
      );
    } else {
      // For local authors, use your own endpoint
      // const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies
      await axios.post(
        `/authors/${targetUuid}/send_follow_request/`,
        followActivity,
        {
          headers: { Authorization: `Token ${this.token}`},
          
        }
      );

      this.showNotification(
        "Follow request sent successfully!",
        "success",
        "fas fa-user-plus"
      );
    }

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
            headers: { Authorization: `Token ${this.token}` },
          }
        );
        this.relationships[author.id] = response.data;
      } catch (error) {
        console.error("Error fetching relationship status:", error);
      }
    },
    async fetchAllRelationships() {
      for (const author of this.authors) {
        await this.fetchRelationshipStatus(author);
      }
    },
    isFriend(author) {
      return this.relationships[author.id]?.is_friend || false;
    },
    isFollowing(author) {
      return this.relationships[author.id]?.is_following || false;
    },
    hasPendingRequest(author) {
      return this.pendingRequests.includes(author.id);
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
        console.log("No UUID found, skipping WebSocket setup");
        return;
      }

      // Check if we're in production
      const isProduction = window.location.hostname.includes("herokuapp.com");

      // Set up the WebSocket URL based on environment
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsHost = isProduction 
        ? window.location.hostname                   // Production host
        : 'localhost:8000';                          // Development host
      
      const wsUrl = `${wsProtocol}://${wsHost}/ws/notifications/${uuid}/`;

      console.log("Setting up WebSocket connection to:", wsUrl);

      const ws = new WebSocket(wsUrl);

      // WebSocket event handlers
      ws.onopen = () => {
        console.log("WebSocket connected successfully");
      };

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Received WebSocket message:", data);

          if (data.type === "follow_request_notification") {
            await this.fetchAuthors();
            await this.fetchAllRelationships();
            await this.fetchPendingRequests();

            if (data.message) {
              this.showNotification(data.message, "info", "fas fa-bell");
            }
          }
        } catch (error) {
          console.error("Error processing WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      ws.onclose = () => {
        console.log(
          "WebSocket connection closed, attempting to reconnect..."
        );
        setTimeout(() => this.setupWebSocket(), 1000);
      };

      this.ws = ws;
    },
    beforeUnmount() {
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
        const authorId = this.selectedAuthor.id;
        const targetUuid = authorId.split("/").pop();
        const targethost = authorId.split('/authors/')[0];

        // Fetch the list of connected nodes
        const response = await axios.get('/connected-nodes/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        const connectedNodes = response.data;

        const targetNode = connectedNodes.find(node => node.url === targethost);
        if (targetNode) {
          // For remote nodes, send to their inbox
          const inboxEndpoint = `${targethost}/api/authors/${targetUuid}/inbox/`;
          console.log('Sending unfollow request to remote inbox:', {
            endpoint: inboxEndpoint,
            credentials: {
              username: targetNode.username,
              password: '********' // masked for security
            }
          });

          // Prepare the unfollow activity object
          const unfollowActivity = {
            type: "unfollow",
            actor: {
              id: localStorage.getItem("id"),
              host: window.location.origin,
              displayName: localStorage.getItem("displayName"),
            },
            object: {
              id: authorId
            }
          };
          // const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies
          await axios.post(inboxEndpoint, unfollowActivity, {
            headers: {
              'node-username': targetNode.username,
              'node-password': targetNode.password,
            },
          });
        } else {
          // For local authors, use the existing endpoint
          await axios.delete(
            `/authors/${targetUuid}/unfollow/`,
            {
              headers: { Authorization: `Token ${this.token}` },
            }
          );
        }

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
    showNotification(
      message,
      type = "success",
      icon = "fas fa-check-circle"
    ) {
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