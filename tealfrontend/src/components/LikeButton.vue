<template>
  <div class="like-button">
    <button @click="toggleLike" :class="{ liked: liked }" :aria-pressed="liked">
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Cookies from 'js-cookie';


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
      // Dynamically return the correct like count
      return this.commentId ? this.commentLikeCount : this.postLikeCount;
    },
  },
  mounted() {
    this.commentId ? this.fetchCommentLikes() : this.fetchPostLikes();
  },
  methods: {
    async fetchPostLikes() {
      try {
        const apiUrl = `/posts/${this.postId}/likes/`;
        const response = await axios.get(apiUrl);
        const likesArray = Array.isArray(response.data) ? response.data : response.data.src || [];
        this.postLikeCount = likesArray.length;

        // Check if the logged-in user has liked the post
        const currentUser = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentUser ? currentUser.id : null;
        if (currentAuthorId) {
          this.liked = likesArray.some((like) => like.author.id === currentAuthorId);
        }
      } catch (error) {
        console.error("Error fetching post likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching post likes.";
      } finally {
        this.loading = false;
      }
    },
    async fetchCommentLikes() {
      try {
        const apiUrl = `/comments/${this.commentId}/likes/`;
        const response = await axios.get(apiUrl);
        const likesArray = Array.isArray(response.data) ? response.data : response.data.src || [];
        this.commentLikeCount = likesArray.length;

        // Check if the logged-in user has liked the comment
        const currentUser = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentUser ? currentUser.id : null;
        if (currentAuthorId) {
          this.liked = likesArray.some((like) => like.author.id === currentAuthorId);
        }
      } catch (error) {
        console.error("Error fetching comment likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching comment likes.";
      } finally {
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
      console.warn("Unliking is not implemented.");
      return;
    }

    // Get the target item (post or comment) details
    const targetItemUrl = this.commentId
      ? `/comments/${this.commentId}/`
      : `/posts/${this.postId}/`;
    
    const targetResponse = await axios.get(targetItemUrl);
    const targetItem = targetResponse.data;

    // Get the author of the post/comment that is being liked
    const targetAuthor = targetItem.author;
    const targetAuthorId = targetAuthor.uuid;
    const targetHost = targetAuthor.host;

    // Get connected nodes
    const response = await axios.get('/connected-nodes/', {
      headers: { Authorization: `Token ${localStorage.getItem("token")}` },
    });
    const connected_nodes = response.data;
    const targetNode = connected_nodes.find(node => node.url === targetHost);

    if (targetNode) {
      // Prepare the like payload
      const likePayload = {
        type: "like",
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
        object: this.commentId 
          ? `/comments/${this.commentId}` 
          : `/posts/${this.postId}`,
        published: new Date().toISOString()
      };

      // Send to target author's inbox (the author of the post/comment being liked)
      const inboxUrl = `${targetHost}/api/authors/${targetAuthorId}/inbox/`;
      const credentials = btoa(`${targetNode.username}:${targetNode.password}`);
      const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies

      await axios.post(inboxUrl, likePayload, {
        headers: {
          Authorization: `Basic ${credentials}`,
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        withCredentials: true,
      });

      // Update local state
      this.liked = true;
      if (this.commentId) {
        this.commentLikeCount += 1;
      } else {
        this.postLikeCount += 1;
      }
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