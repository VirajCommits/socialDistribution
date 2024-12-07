<template>
  <div class="like-button">
    <button @click="handleLike" :class="{ liked: liked }" :aria-pressed="liked">
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-spinner fa-spin"></i>
    </div>
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-circle"></i>{{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LikeButton",
  props: {
    commentId: {
      type: String,
      required: false,
    },
    postId: {
      type: String,
      required: false,
    }
  },
  data() {
    return {
      liked: false,
      likeCount: 0,
      loading: false,
      errorMessage: '',
      authID: null,
      user: null,
    };
  },
  mounted() {
    this.initializeUser();
    this.loadInitialLikeCount(); // Fetch the initial like count
  },
  methods: {
    /**
     * Initializes user information from localStorage.
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
     * Loads the initial like count for the post or comment.
     */
    async loadInitialLikeCount() {
      try {
        this.loading = true;

        if (this.postId) {
          // If this is a post, fetch like count for the post
          const likesResponse = await axios.get(`/likes/${this.postId}/stream/`, {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          });
          this.likeCount = likesResponse.data.length;
          this.liked = likesResponse.data.some(like => like.author.id === this.authID);
        } else if (this.commentId) {
          // If this is a comment, fetch like count for the comment
          const likesResponse = await axios.get(`/comments/${this.commentId}/likes/`, {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          });
          this.likeCount = likesResponse.data.size;
          this.liked = likesResponse.data.src.some(like => like.author.id === this.authID);
        }

      } catch (error) {
        console.error("Error fetching initial like count:", error);
        this.errorMessage = "Failed to load like count.";
      } finally {
        this.loading = false;
      }
    },

    /**
     * Handles the like button click event for either post or comment.
     */
    async handleLike() {
      if (!this.authID) {
        this.errorMessage = "User not authenticated.";
        return;
      }

      const previousLikedState = this.liked;
      this.liked = !this.liked;
      this.likeCount += this.liked ? 1 : -1;

      try {
        this.loading = true;

        if (this.postId) {
          // Like/unlike the post
          if (this.liked) {
            await this.likePost();
          } else {
            await this.unlikePost();
          }
        } else if (this.commentId) {
          // Like/unlike the comment
          if (this.liked) {
            await this.likeComment();
          } else {
            await this.unlikeComment();
          }
        }
      } catch (error) {
        console.error("Error toggling like:", error);
        this.errorMessage = "Failed to update like status.";
        // Revert the state if an error occurs
        this.liked = previousLikedState;
        this.likeCount += this.liked ? 1 : -1;
      } finally {
        this.loading = false;
      }
    },

    /**
     * API call to like a post.
     */
    async likePost() {
      try {
        const response = await axios.post(
          `/posts/${this.postId}/like/`,
          {},
          {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          }
        );
        console.log("Post liked successfully:", response.data);
      } catch (error) {
        console.error("Error liking post:", error);
        throw error;
      }
    },

    /**
     * API call to unlike a post.
     */
    async unlikePost() {
      try {
        const response = await axios.delete(
          `/posts/${this.postId}/like/`,
          {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          }
        );
        console.log("Post unliked successfully:", response.data);
      } catch (error) {
        console.error("Error unliking post:", error);
        throw error;
      }
    },

    /**
     * API call to like a comment.
     */
    async likeComment() {
      try {
        const response = await axios.post(
          `/comments/${this.commentId}/like/`,
          {},
          {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          }
        );
        console.log("Comment liked successfully:", response.data);
      } catch (error) {
        console.error("Error liking comment:", error);
        throw error;
      }
    },

    /**
     * API call to unlike a comment.
     */
    async unlikeComment() {
      try {
        const response = await axios.delete(
          `/comments/${this.commentId}/like/`,
          {
            headers: { Authorization: `Token ${localStorage.getItem("token")}` },
          }
        );
        console.log("Comment unliked successfully:", response.data);
      } catch (error) {
        console.error("Error unliking comment:", error);
        throw error;
      }
    }
  },
};
</script>

<style scoped>
.like-button {
  display: flex;
  justify-content: center;
  align-items: center;
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

/* Error Message Styles (Optional Enhancement) */
.error-message {
  color: #ff6b6b;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.error-message i {
  margin-right: 0.3rem;
}
</style>
