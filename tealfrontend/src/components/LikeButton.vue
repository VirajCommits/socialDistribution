<template>
  <div class="like-button">
    <button @click="toggleLike" :class="{ liked: liked }" :aria-pressed="liked">
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-spinner fa-spin"></i>
    </div>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
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
      likeCount: 0,
      loading: true,
      errorMessage: "",
    };
  },
  mounted() {
    this.fetchLikes();
  },
  methods: {
    async fetchLikes() {
      try {
        this.loading = true;
        const apiUrl = this.commentId
      ? `/posts/${encodeURIComponent(this.postId)}/comments/`
      : `/posts/${encodeURIComponent(this.postId)}/`;

        const response = await axios.get(apiUrl);
        const likesArray = Array.isArray(response.data) ? response.data : response.data.src || [];
        this.likeCount = likesArray.length;

        // Check if the logged-in user has liked the post/comment
        const currentUser = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentUser ? currentUser.id : null;
        if (currentAuthorId) {
          this.liked = likesArray.some((like) => like.author.id === currentAuthorId);
        }
      } catch (error) {
        console.error("Error fetching likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching likes.";
      } finally {
        this.loading = false;
      }
    },
    async toggleLike() {
      try {
        const currentUser = JSON.parse(localStorage.getItem("user"));
        if (!currentUser || !currentUser.id) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        const targetObjectUrl = this.commentId
          ? `/posts/${encodeURIComponent(this.postId)}/comments/`
          : `/posts/${encodeURIComponent(this.postId)}/`;

        // Fetch the post/comment to get the author's details
        const targetResponse = await axios.get(targetObjectUrl);
        const targetAuthor = targetResponse.data.author;

        if (!targetAuthor || !targetAuthor.id || !targetAuthor.host) {
          this.errorMessage = "Unable to identify the target author or their host.";
          return;
        }

        // Extract the target author ID from the full URL (if it's a full URL like /authors/<id>)
        const targetAuthorId = targetAuthor.id.split("/").pop();  // Get the last part of the URL

        // Construct the full inbox URL using the target host and extracted author ID
        const inboxUrl = `${targetAuthor.host}api/authors/${encodeURIComponent(targetAuthorId)}/inbox/`;

        // Prepare the payload for the like action
        const payload = {
          type: this.liked ? "unlike" : "like",
          id: crypto.randomUUID(),
          author: {
            type: "author",
            id: currentUser.id,
            host: currentUser.host,
            displayName: currentUser.displayName,
            page: currentUser.page,
            github: currentUser.github,
            profileImage: currentUser.profileImage,
          },
          object: targetObjectUrl,
          published: new Date().toISOString(),
        };

        // Send the like/unlike action to the inbox
        const response = await axios.get('/connected-nodes/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        const connected_nodes = response.data;
        const csrfToken = Cookies.get("csrftoken");
        const targetNode = connected_nodes.find(node => node.url === targetAuthor.host);
        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);
        await axios.post(inboxUrl, payload, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${credentials}`,
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        });

        // Toggle like state and update the counter
        this.liked = !this.liked;
        this.likeCount += this.liked ? 1 : -1;
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
        this.errorMessage = error.response?.data || "An error occurred while toggling the like.";
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

/* Error Message Styles */
.error-message {
  color: #ff6b6b;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}
</style>
