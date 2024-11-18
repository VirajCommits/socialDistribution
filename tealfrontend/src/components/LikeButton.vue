<!-- src/components/LikeButton.vue -->
<template>
  <div class="like-button">
    <button
      @click="toggleLike"
      :class="{ liked: liked }"
      :aria-pressed="liked"
      :aria-label="liked ? 'Unlike' : 'Like'"
    >
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <i class="fas fa-check-circle"></i>
      {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LikeButton",
  props: {
    postId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      liked: false,
      likeCount: 0,
      errorMessage: "",
      successMessage: "",
      user: null,
      authID: "",
      postAuthor: null, // To store post author's details
    };
  },
  mounted() {
    this.initializeUser();
    this.fetchPostDetails();
    this.fetchLikes();
  },
  methods: {
    /**
     * Initializes user information from localStorage.
     * Extracts the current user's ID for identifying like actions.
     */
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

    /**
     * Fetches post details to retrieve the post author's information.
     */
    async fetchPostDetails() {
      try {
        const apiUrl = `/posts/${encodeURIComponent(this.postId)}/`;
        const response = await axios.get(apiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        this.postAuthor = response.data.author;
      } catch (error) {
        console.error("Error fetching post details:", error.response || error);
        this.errorMessage = "An error occurred while fetching post details.";
      }
    },

    /**
     * Fetches the current number of likes and determines if the user has already liked the post.
     */
    async fetchLikes() {
      try {
        const apiUrl = `/posts/${encodeURIComponent(this.postId)}/likes/`;
        const response = await axios.get(apiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        this.likeCount = response.data.length || 0;

        // Check if the logged-in author has liked the post
        if (this.authID) {
          this.liked = response.data.some(
            (like) => like.author.id.split("/").pop() === this.authID
          );
        }
      } catch (error) {
        console.error("Error fetching likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching likes.";
      }
    },

    /**
     * Toggles the like state of the post.
     * Handles both liking and unliking actions.
     */
    async toggleLike() {
      try {
        if (!this.authID) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        const token = localStorage.getItem("token");
        const apiUrl = `/posts/${encodeURIComponent(this.postId)}/like/`;

        if (this.liked) {
          // Unlike the post
          const unlikeUrl = `${apiUrl}${this.authID}/`; // Adjust the API endpoint as needed
          await axios.delete(unlikeUrl, {
            headers: {
              Authorization: `Token ${token}`,
            },
          });
          this.liked = false;
          this.likeCount = Math.max(this.likeCount - 1, 0);
          // Optionally, handle unlike notifications if your backend supports it
        } else {
          // Like the post
          const payload = {
            author_id: this.authID, // Include the author ID
            post_id: this.postId,
          };

          const response = await axios.post(apiUrl, payload, {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Token ${token}`, // Include the authentication token
            },
          });

          // Assuming the response contains the created like object
          const likeData = response.data;

          this.liked = true;
          this.likeCount += 1;

          // Send notification to the post author's inbox
          await this.sendLikeNotification(likeData);
        }

        // Clear success message after a short delay
        setTimeout(() => {
          this.successMessage = "";
        }, 3000);
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
        this.errorMessage = "An error occurred while toggling the like.";
        // Clear error message after a short delay
        setTimeout(() => {
          this.errorMessage = "";
        }, 5000);
      }
    },

    /**
     * Sends a like notification to the post author's inbox.
     * @param {Object} likeData - The data of the created like.
     */
    async sendLikeNotification(likeData) {
      try {
        if (!this.postAuthor) {
          console.warn("Post author information is missing. Skipping notification.");
          return;
        }

        const inboxUrl = `/authors/${encodeURIComponent(
          this.postAuthor.id.split("/").pop()
        )}/inbox/`;
        const token = localStorage.getItem("token");

        const payload = {
          type: "like",
          id: likeData.id,
          content: likeData.content || "", // Adjust based on your Like model
          contentType: likeData.contentType || "text/plain", // Adjust as needed
          published: likeData.published || new Date().toISOString(),
          author: {
            type: "author",
            id: this.user.id,
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage || "",
          },
          post: {
            id: this.postId,
            title: this.postAuthor.displayName, // Adjust based on your Post model
            description: "", // Include if available
            contentType: "", // Include if available
            content: "", // Include if available
            published: new Date().toISOString(), // Adjust based on your Post model
            visibility: "", // Include if available
            author: {
              id: this.postAuthor.id,
              host: this.postAuthor.host,
              displayName: this.postAuthor.displayName,
              page: this.postAuthor.page,
              github: this.postAuthor.github,
              profileImage: this.postAuthor.profileImage || "",
            },
          },
          author_id: this.authID,
        };

        await axios.post(inboxUrl, payload, {
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        });
      } catch (error) {
        console.error(
          `Error sending like notification to author ${this.postAuthor.id}:`,
          error.response || error
        );
        // Optionally, set an error message or handle it as needed
      }
    },
  },
};
</script>

<style scoped>
.like-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

/* Like Button Styles */
.like-button button {
  position: relative;
  background: linear-gradient(45deg, #ff6b6b, #f06595);
  border: none;
  border-radius: 50px;
  color: #fff;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: transform 0.2s ease, background 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.like-button button:hover {
  transform: translateY(-2px);
  background: linear-gradient(45deg, #ff4757, #e84393);
}

.like-button button:active {
  transform: scale(0.95);
}

.like-button button.liked {
  background: linear-gradient(45deg, #e84393, #ff4757);
  animation: pulse 0.6s;
}

.like-button button.liked i {
  color: #ffeb3b;
  animation: heartBeat 0.6s;
}

.like-button button i {
  margin-right: 0.5rem;
  transition: color 0.3s ease;
  font-size: 1.2rem;
}

.like-button button .like-count {
  font-weight: bold;
  transition: color 0.3s ease;
}

/* Animations */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(232, 67, 147, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(232, 67, 147, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(232, 67, 147, 0);
  }
}

@keyframes heartBeat {
  0%,
  100% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.2);
  }
  50% {
    transform: scale(0.9);
  }
  75% {
    transform: scale(1.1);
  }
}

/* Success and Error Messages */
.success-message,
.error-message {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: bold;
  width: 100%;
  justify-content: center;
}

.success-message {
  background-color: #dff0d8;
  color: #3c763d;
}

.success-message i {
  margin-right: 0.5rem;
}

.error-message {
  background-color: #ffe5e5;
  color: #cc0000;
}

.error-message i {
  margin-right: 0.5rem;
}

/* Responsive Design */
@media (max-width: 600px) {
  .like-button button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .like-button button i {
    font-size: 1rem;
  }
}
</style>
