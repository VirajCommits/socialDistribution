<template>
  <div class="like-button">
    <button @click="handleLike" :class="{ liked: liked }" :aria-pressed="liked">
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
    commentId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      liked: false,
      likeCount: 0,
      loading: false,
      errorMessage: '',
    };
  },
  mounted() {
    this.initializeUser();
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
     * Handles the like button click event.
     * Toggles the like status and sends like notification to the inbox.
     */
     async handleLike(postId, likeData, postData, targethost) {
      if (!this.authID) {
        this.errorMessage = "User not authenticated.";
        return;
      }

      // Toggle like status
      this.liked = !this.liked;

      const likeData = {
        id: crypto.randomUUID(), // Generate a unique UUID for the Like object
        author: {
            id: this.authID, // The authenticated user's ID (from the frontend state)
            displayName: this.authDisplayName, // The authenticated user's display name
        },
        post: postId || null, // The ID of the post being liked (set to null if it's a comment)
        comment: commentId || null, // The ID of the comment being liked (set to null if it's a post)
        published: new Date().toISOString(), // The current timestamp in ISO format
      };

      // Log for debugging
      console.log("Created likeData object:", likeData);

      try {
        // Call the function to send like to the inbox with the necessary parameters
        await this.sendLikeToInbox(postId, likeData, postData, targethost);
      } catch (error) {
        console.error("Error sending like to inbox:", error);
        this.errorMessage = "An error occurred while sending like to inbox.";
      }
    },

    /**
     * Sends the like action to the relevant author's inbox.
     */
     async sendLikeToInbox(authorId, likeData, postData, targethost) {
      try {
        console.log("SENDING LIKE TO INBOX IN LIKEBUTTON:", authorId, likeData, postData, targethost);
        
        const inboxUrl = `${targethost}/api/authors/${authorId}/inbox/`;

        console.log("GRRRRRRRR", this.user.host);
        console.log("GRRRRRRRR", this.user.id);
        console.log("GRRRRRRRR", this.likeData);

        // Create the payload for the like action
        const payload = {
          type: "like",
          author: {
            type: "author",
            id: this.user.id,  // Use the current logged-in user's ID
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage,
          },
          
          published: new Date().toISOString(), // Current timestamp
          id: `${this.user.host}/api/authors/${this.user.id}/liked/${likeData.id}`,  // Like ID (usually a UUID)
          object: postData.id,  // The post or comment that was liked
        };

        console.log(`Sending like to inbox of author ${authorId}:`, payload);

        // Get connected nodes (similar to how you did for comments)
        const response = await axios.get('/connected-nodes/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        const connectedNodes = response.data;

        // Find the target node based on the host
        const targetNode = connectedNodes.find(node => node.url === targethost);
        if (!targetNode) {
          throw new Error(`Target host ${targethost} not found among connected nodes.`);
        }

        // Basic Authentication credentials
        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);

        // CSRF Token
        const csrfToken = Cookies.get("csrftoken");

        // Send the like payload to the author's inbox
        await axios.post(inboxUrl, payload, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${credentials}`,
            "X-CSRFToken": csrfToken,
          },
        });
      } catch (error) {
        console.error(`Error sending like to author ${authorId}'s inbox:`, error);
        throw error;  // Re-throw to handle in distributeLike or elsewhere if needed
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