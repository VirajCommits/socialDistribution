<template>
  <div class="like-button">
    <button @click="toggleLike" :class="{ liked: liked }" :aria-pressed="liked">
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>
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
    };
  },
  mounted() {
    this.fetchLikes();
  },
  methods: {
    async fetchLikes() {
      try {
        const apiUrl = `/posts/${this.postId}/likes/`;
        const response = await axios.get(apiUrl);
        this.likeCount = response.data.length || 0;

        // Check if the logged-in author has liked the post
        const currentUser = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentUser ? currentUser.id : null;
        if (currentAuthorId) {
          this.liked = response.data.some(
            (like) => like.author.id === currentAuthorId
          );
        }
      } catch (error) {
        console.error("Error fetching likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching likes.";
      }
    },
    async toggleLike() {
      try {
        const currentUser = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentUser ? currentUser.id : null;

        if (!currentAuthorId) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        const apiUrl = `posts/${this.postId}/like/`;

        if (this.liked) {
          // If unliking is needed, implement the logic here
          // Example: Send a DELETE request to remove the like
          const unlikeUrl = `${apiUrl}/${currentAuthorId}/`; // Adjust the API endpoint as needed
          await axios.delete(unlikeUrl, {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          });
          this.liked = false;
          this.likeCount -= 1;
        } else {
          // Post a like
          const payload = {
            author_id: currentAuthorId, // Include the author ID
            post_id: this.postId,
          };

          await axios.post(apiUrl, payload, {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Token ${localStorage.getItem("token")}`, // Include the authentication token
            },
          });

          this.liked = true;
          this.likeCount += 1;
        }
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
        this.errorMessage = "An error occurred while toggling the like.";
      }
    },
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
