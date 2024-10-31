<template>
  <div class="stream-container">
    <h2>Your Stream</h2>

    <!-- Buttons Container -->
    <div class="buttons-container">
      <button class="logout-button" @click="logoutNode">Logout</button>
      <button class="profile-button" @click="goToProfile">Profile</button>
      <button class="follow-requests-button" @click="toggleFollowRequests">
        Follow Requests
        <span v-if="followRequestCount > 0" class="badge">{{
          followRequestCount
        }}</span>
      </button>
      <button class="explore-authors-button" @click="goToExploreAuthors">
        Explore Authors
      </button>
    </div>

    <!-- Follow Requests Section -->
    <div v-if="followRequestsVisible" class="follow-requests-section">
      <h2>Follow Requests</h2>
      <div v-if="followRequests.length">
        <div
          v-for="request in followRequests"
          :key="request.uuid"
          class="follow-request-item"
        >
          <span>{{ request.actor.displayName }}</span>
          <button @click="acceptFollowRequest(request.actor.uuid)">
            Accept
          </button>
          <button @click="declineFollowRequest(request.actor.uuid)">
            Decline
          </button>
        </div>
      </div>
      <div v-else>
        <p>No follow requests</p>
      </div>
    </div>

    <!-- Posts Section -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading posts...
    </div>

    <div v-else-if="visiblePosts.length === 0" class="no-posts">
      <p>No posts found in your stream.</p>
    </div>

    <div v-else class="posts-grid">
      <div class="post-card" v-for="post in visiblePosts" :key="post.id">
        <div class="post-content">
          <h3 v-html="post.title"></h3>
          <p v-html="post.description"></p>

          <!-- Render image or text content -->
          <div v-if="isImageContent(post.content)">
            <img
              :src="extractImageSrc(post.content)"
              alt="Post Image"
              width="300"
            />
          </div>
          <div v-else>
            <p v-html="post.content"></p>
          </div>

          <p><strong>Author:</strong> {{ post.author.displayName }}</p>
          <p>
            <strong>Visibility:</strong>
            <span :class="`visibility-${post.visibility.toLowerCase()}`">
              {{ post.visibility }}
            </span>
          </p>

          <!-- Include LikeButton and CommentSection if applicable -->
          <!-- <LikeButton :postId="post.id" :authorId="authID" />
          <CommentSection :postId="post.id" :authorId="authID" /> -->
        </div>
      </div>
    </div>

    <!-- Error messages -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
// Import LikeButton and CommentSection if you have them
// import LikeButton from "./LikeButton.vue";
// import CommentSection from "./CommentSection.vue";

export default {
  name: "StreamPage",
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
    };
  },
  // Uncomment components if you use them
  // components: {
  //   LikeButton,
  //   CommentSection,
  // },
  computed: {
    visiblePosts() {
      return this.posts.filter((post) => post.visibility !== "INVISIBLE");
    },
  },
  mounted() {
    this.initializeUser();
    this.fetchStreamPosts();
  },
  methods: {
    initializeUser() {
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
    async fetchStreamPosts() {
      try {
        const apiUrl = `http://localhost:8000/project/service/api/authors/${encodeURIComponent(
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
    goToProfile() {
      this.$router.push("/profile");
    },
    goToExploreAuthors() {
      this.$router.push("/explore");
    },
    logoutNode() {
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
          `http://localhost:8000/project/service/api/authors/follow_requests/`,
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
          `http://localhost:8000/project/service/api/authors/${uuid}/accept_follow_request/`,
          null,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then(() => {
          console.log("Follow request accepted");
          this.fetchFollowRequests();
        })
        .catch((error) => {
          console.error("Error accepting follow request:", error);
        });
    },
    declineFollowRequest(uuid) {
      axios
        .post(
          `http://localhost:8000/project/service/api/authors/${uuid}/decline_follow_request/`,
          null,
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then(() => {
          console.log("Follow request declined");
          this.fetchFollowRequests();
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
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.buttons-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.buttons-container button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin: 0 10px; /* Add space between buttons */
  position: relative; /* Position relative for badge */
}

.buttons-container button:hover {
  background-color: #2c8a6a;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

.loading {
  text-align: center;
  font-size: 1.2em;
  color: #3498db;
}

.no-posts {
  text-align: center;
  font-size: 1.1em;
  color: #7f8c8d;
}

.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  background-color: #ffffff;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.post-card:hover {
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.post-content {
  padding: 20px;
}

.post-content h3 {
  margin-top: 0;
  color: #2980b9;
}

.post-content p {
  color: #34495e;
  line-height: 1.6;
}

.visibility-public {
  color: #27ae60;
  font-weight: bold;
}

.visibility-friends {
  color: #f1c40f;
  font-weight: bold;
}

.visibility-private,
.visibility-invisible {
  color: #c0392b;
  font-weight: bold;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  background-color: #f2dede;
  color: #a94442;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message i {
  font-size: 1.2em;
}

/* Follow Requests Section */
.follow-requests-section {
  margin-top: 40px;
  text-align: center;
}

.follow-request-item {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px auto;
  gap: 10px;
}

.follow-request-item button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}

.follow-request-item button:hover {
  background-color: #2c8a6a;
}

.badge {
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 5px 10px;
  font-size: 12px;
  margin-left: 5px;
  position: absolute;
  top: -10px;
  right: -10px;
}

/* Responsive Design */
@media (max-width: 600px) {
  .buttons-container {
    flex-direction: column;
    align-items: center;
  }

  .buttons-container button {
    margin: 10px 0;
    width: 80%;
  }
}
</style>
