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
    this.token = localStorage.getItem("token"); // Retrieve the JWT token
    this.user = JSON.parse(localStorage.getItem("user")); // Retrieve the user object
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
      console.log("Like button clicked");

      try {
        console.log("Liked state before action:", this.liked);

        const jwtToken = localStorage.getItem("token"); // Fetch token from localStorage
        const csrfToken = Cookies.get("csrftoken"); // CSRF token from cookies

        console.log("JWT token:", jwtToken); // Debug token
        console.log("User object:", this.user);

        // Ensure the user is authenticated
        if (!this.user || !jwtToken) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        console.log("User authenticated:", this.user); // Debug user

        if (this.liked) {
          console.warn("Unliking is not implemented.");
          return;
        }

        console.log("Preparing like action...");

        // Check whether we are liking a post or a comment
        if (this.commentId) {
          // Handle comment likes
          await this.likeComment(jwtToken, csrfToken);
        } else if (this.postId) {
          // Handle post likes
          await this.likePost(jwtToken, csrfToken);
        } else {
          console.error("Invalid state: No postId or commentId provided.");
        }
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
        this.errorMessage = "An error occurred while toggling the like.";
      }
    },

    async likePost(jwtToken, csrfToken) {
      try {
        console.log("Liking a post...");

        const likePayload = {
          type: "like",
          id: crypto.randomUUID(),
          author: {
            type: "author",
            id: this.user.id,
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage,
          },
          object: `/posts/${this.postId}/`,
          published: new Date().toISOString(),
        };

        const targetItemUrl = `posts/${this.postId}/`;
        console.log("Target item URL for post:", targetItemUrl);

        const targetResponse = await axios.get(targetItemUrl, {
          headers: {
            Authorization: `Token ${jwtToken}`,
          },
        });
        console.log("Target post response:", targetResponse.data);

        const targetAuthor = targetResponse.data.author;
        if (targetAuthor.host === this.user.host) {
          // Same-node handling
          console.log("Same-node request for post. Handling like locally.");
          const likeApiUrl = `posts/${this.postId}/like/`;

          await axios.post(likeApiUrl, likePayload, {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Token ${jwtToken}`,
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          });

          this.liked = true;
          this.postLikeCount += 1;
        } else {
          // Handle remote-node requests
          console.log("Remote-node request for post. Sending to inbox.");
          await this.sendToInbox(targetAuthor, likePayload, jwtToken);
        }
      } catch (error) {
        console.error("Error liking post:", error.response || error);
        this.errorMessage = "An error occurred while liking the post.";
      }
    },

    async likeComment(jwtToken, csrfToken) {
      try {
        console.log("Liking a comment...");

        const likePayload = {
          type: "like",
          id: crypto.randomUUID(),
          author: {
            type: "author",
            id: this.user.id,
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage,
          },
          object: `/comments/${this.commentId}/`,
          published: new Date().toISOString(),
        };

        const targetItemUrl = `comments/${this.commentId}/`;
        console.log("Target item URL for comment:", targetItemUrl);

        const targetResponse = await axios.get(targetItemUrl, {
          headers: {
            Authorization: `Token ${jwtToken}`,
          },
        });
        console.log("Target comment response:", targetResponse.data);

        const targetAuthor = targetResponse.data.author;
        if (targetAuthor.host === this.user.host) {
          // Same-node handling
          console.log("Same-node request for comment. Handling like locally.");
          const likeApiUrl = `comments/${this.commentId}/like/`;

          await axios.post(likeApiUrl, likePayload, {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Token ${jwtToken}`,
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          });

          this.liked = true;
          this.commentLikeCount += 1;
        } else {
          // Handle remote-node requests
          console.log("Remote-node request for comment. Sending to inbox.");
          await this.sendToInbox(targetAuthor, likePayload, jwtToken);
        }
      } catch (error) {
        console.error("Error liking comment:", error.response || error);
        this.errorMessage = "An error occurred while liking the comment.";
      }
    },

    async sendToInbox(targetAuthor, likePayload, jwtToken) {
      try {
        const inboxUrl = `${targetAuthor.host}api/authors/${targetAuthor.id.split("/").pop()}/inbox`;
        console.log("Inbox URL:", inboxUrl);

        const response = await axios.get("/connected-nodes/", {
          headers: {
            Authorization: `Token ${jwtToken}`,
          },
        });
        console.log("Target author host:", targetAuthor.host);
        const connectedNodes = response.data;
        console.log("Connected nodes:", connectedNodes);
        const targetauthorHost = targetauthorHost.split('/api')[0];
        console.log("Target author host:", targetauthorHost);
        const targetNode = connectedNodes.find((node) => node.url === targetauthorHost);
        console.log("Target node:", targetNode);
        if (!targetNode) {
          console.error(`No connected node matches the target host: ${targetAuthor.host}`);
          this.errorMessage = "Unable to find a connected node for the target host.";
          return;
        }

        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);
        await axios.post(inboxUrl, likePayload, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${credentials}`,
          },
        });

        console.log("Like sent to inbox successfully.");
      } catch (error) {
        console.error("Error sending like to inbox:", error.response || error);
        this.errorMessage = "An error occurred while sending the like to the inbox.";
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