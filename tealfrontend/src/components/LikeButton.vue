<template>
  <div class="like-button">
    <button
      @click="toggleLike"
      :class="{ liked: liked }"
      :aria-pressed="liked"
      :disabled="loading"
    >
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-spinner fa-spin"></i>
    </div>
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Cookies from "js-cookie";

export default {
  name: "LikeButton",
  props: {
    postId: {
      type: String,
      required: false,
    },
    commentId: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      liked: false,
      postLikeCount: 0,
      commentLikeCount: 0,
      loading: false,
      errorMessage: "",
    };
  },
  computed: {
    likeCount() {
      return this.commentId ? this.commentLikeCount : this.postLikeCount;
    },
  },
  mounted() {
    this.fetchLikes();
  },
  methods: {
    async fetchLikes() {
      this.loading = true;
      const apiUrl = this.commentId
        ? `/comments/${this.commentId}/likes/`
        : `/posts/${this.postId}/likes/`;
      try {
        const response = await axios.get(apiUrl);
        const likes = response.data || [];
        this.liked = likes.some(
          (like) => like.author.id === JSON.parse(localStorage.getItem("user"))?.id
        );
        if (this.commentId) {
          this.commentLikeCount = likes.length;
        } else {
          this.postLikeCount = likes.length;
        }
      } catch (error) {
        console.error("Error fetching likes:", error);
        this.errorMessage = "Failed to load likes.";
      } finally {
        this.loading = false;
      }
    },
    async toggleLike() {
      if (this.loading) return;
      this.loading = true;

      try {
        const currentUser = JSON.parse(localStorage.getItem("user"));
        if (!currentUser) {
          this.errorMessage = "You need to be logged in to like this.";
          return;
        }

        if (this.liked) {
          await this.unlike();
        } else {
          await this.like(currentUser);
        }
      } catch (error) {
        console.error("Error toggling like:", error);
        this.errorMessage = "An error occurred while toggling the like.";
      } finally {
        this.loading = false;
      }
    },
    async like(currentUser) {
      const apiUrl = this.commentId
        ? `/comments/${this.commentId}/`
        : `/posts/${this.postId}/`;

      const response = await axios.get(apiUrl);
      const targetItem = response.data;

      const likePayload = {
        type: "like",
        id: crypto.randomUUID(),
        author: {
          id: currentUser.id,
          host: currentUser.host,
          displayName: currentUser.displayName,
          profileImage: currentUser.profileImage,
        },
        object: this.commentId ? `/comments/${this.commentId}` : `/posts/${this.postId}`,
        published: new Date().toISOString(),
      };

      const inboxUrl = `${targetItem.author.host}/api/authors/${targetItem.author.uuid}/inbox/`;
      const csrfToken = Cookies.get("csrftoken");

      await axios.post(inboxUrl, likePayload, {
        headers: {
          Authorization: `Basic ${btoa(
            `${targetItem.author.username}:${targetItem.author.password}`
          )}`,
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
        withCredentials: true,
      });

      this.liked = true;
      if (this.commentId) {
        this.commentLikeCount += 1;
      } else {
        this.postLikeCount += 1;
      }
    },
    async unlike() {
      const apiUrl = this.commentId
        ? `/comments/${this.commentId}/likes/`
        : `/posts/${this.postId}/likes/`;

      await axios.delete(apiUrl, {
        headers: {
          Authorization: `Token ${localStorage.getItem("token")}`,
        },
      });

      this.liked = false;
      if (this.commentId) {
        this.commentLikeCount -= 1;
      } else {
        this.postLikeCount -= 1;
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
}

/* Button Styles */
.like-button button {
  position: relative;
  background: linear-gradient(45deg, #ff6b6b, #f06595);
  border: none;
  border-radius: 50px;
  color: white;
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
  font-size: 1.2rem;
}

.like-button button .like-count {
  font-weight: bold;
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
  0%, 100% {
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

/* Loading Spinner */
.loading-spinner {
  margin-top: 0.5rem;
}

/* Error Message */
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
