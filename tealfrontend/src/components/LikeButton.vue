<template>
  <div class="like-button">
    <button @click="toggleLike" :class="{ liked: liked }" :aria-pressed="liked">
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
      required: false, // Optional for comments
    },
    commentId: {
      type: String,
      required: false, // Optional for posts
    },
  },
  data() {
    return {
      liked: false,
      postLikeCount: 0, // Separate counter for post likes
      commentLikeCount: 0, // Separate counter for comment likes
      loading: true,
      errorMessage: "",
    };
  },
  computed: {
    likeCount() {
      return this.commentId ? this.commentLikeCount : this.postLikeCount;
    },
  },
  mounted() {
    this.commentId ? this.fetchCommentLikes() : this.fetchPostLikes();
  },
  methods: {
    async fetchPostLikes() {
      try {
        const response = await axios.get(`/posts/${this.postId}/likes/`);
        this.postLikeCount = response.data.length;
        this.liked = response.data.some(
          (like) => like.author.id === JSON.parse(localStorage.getItem("user")).id
        );
        this.loading = false;
      } catch (error) {
        console.error("Error fetching post likes:", error);
        this.errorMessage = "Unable to fetch post likes.";
        this.loading = false;
      }
    },
    async fetchCommentLikes() {
      try {
        const response = await axios.get(`/comments/${this.commentId}/likes/`);
        this.commentLikeCount = response.data.length;
        this.liked = response.data.some(
          (like) => like.author.id === JSON.parse(localStorage.getItem("user")).id
        );
        this.loading = false;
      } catch (error) {
        console.error("Error fetching comment likes:", error);
        this.errorMessage = "Unable to fetch comment likes.";
        this.loading = false;
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

        if (this.liked) {
          await this.unlike();
          return;
        }

        // Prepare the "like" object
        const targetObjectUrl = this.commentId
          ? `/comments/${this.commentId}`
          : `/posts/${this.postId}`;

        const likePayload = {
          type: "like",
          author: {
            type: "author",
            id: currentUser.id,
            page: currentUser.page,
            host: currentUser.host,
            displayName: currentUser.displayName,
            github: currentUser.github,
            profileImage: currentUser.profileImage,
          },
          published: new Date().toISOString(),
          id: `${currentUser.host}/liked/${crypto.randomUUID()}`,
          object: targetObjectUrl,
        };

        // Determine the target author's inbox URL
        const targetResponse = await axios.get(targetObjectUrl);
        const targetAuthor = targetResponse.data.author;
        const targetInboxUrl = `${targetAuthor.host}api/authors/${targetAuthor.id.split(
          "/"
        ).pop()}/inbox/`;

        // Fetch connected nodes for credentials
        const connectedNodesResponse = await axios.get("/connected-nodes/", {
          headers: { Authorization: `Token ${localStorage.getItem("token")}` },
        });
        const connectedNodes = connectedNodesResponse.data;
        const targetNode = connectedNodes.find(
          (node) => node.url === targetAuthor.host
        );

        if (!targetNode) {
          throw new Error(`Host ${targetAuthor.host} not in connected nodes.`);
        }

        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);
        const csrfToken = Cookies.get("csrftoken");

        // Send the like to the target inbox
        await axios.post(targetInboxUrl, likePayload, {
          headers: {
            Authorization: `Basic ${credentials}`,
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        });

        // Update local state
        this.liked = true;
        this.commentId
          ? (this.commentLikeCount += 1)
          : (this.postLikeCount += 1);
      } catch (error) {
        console.error("Error toggling like:", error);
        this.errorMessage = "An error occurred while toggling the like.";
      }
    },
    async unlike() {
      try {
        const apiUrl = this.commentId
          ? `/comments/${this.commentId}/likes/`
          : `/posts/${this.postId}/likes/`;

        await axios.delete(apiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });

        this.liked = false;
        this.commentId
          ? (this.commentLikeCount -= 1)
          : (this.postLikeCount -= 1);
      } catch (error) {
        console.error("Error unliking:", error);
        this.errorMessage = "An error occurred while unliking.";
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

@media (max-width: 600px) {
  .like-button button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .like-button button i {
    font-size: 1rem;
  }
}

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
