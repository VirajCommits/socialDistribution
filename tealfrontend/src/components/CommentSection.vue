<template>
  <div class="comment-section">
    <h4 class="section-title">Comments ({{ comments.length }})</h4>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>Loading comments...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="comments.length === 0" class="empty-state">
      <i class="fas fa-comment-slash"></i>
      <p>No comments yet. Be the first to comment!</p>
    </div>

    <!-- Comments List -->
    <div v-else class="comments-list">
      <ul>
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <!-- Avatar and Author Name Container -->
          <div class="avatar-and-author">
            <img
              :src="comment.author.profileImage || defaultAvatar"
              alt="Commenter Avatar"
              class="comment-avatar"
            />
            <span class="comment-author">{{ comment.author.displayName }}</span>
          </div>

          <!-- Comment Text and Time -->
          <div class="comment-details">
            <p class="comment-text">{{ comment.content }}</p>
          </div>
        </li>
      </ul>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>

    <!-- Comment Form -->
    <div class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="Write a comment..."
        rows="3"
        @keydown.enter.prevent="submitComment"
      ></textarea>
      <button @click="submitComment" :disabled="!newComment.trim()">
        <i class="fas fa-paper-plane"></i> Comment
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CommentSection",
  props: {
    postId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      comments: [],
      newComment: "",
      loading: true,
      errorMessage: "",
      // Default avatar in case the commenter hasn't set one
      defaultAvatar:
        "https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg",
    };
  },
  mounted() {
    this.fetchComments();
  },
  methods: {
    async fetchComments() {
      try {
        const apiUrl = `/posts/${this.postId}/comments/`;
        const response = await axios.get(apiUrl);
        this.comments = response.data || [];
        this.loading = false;
      } catch (error) {
        console.error("Error fetching comments:", error.response || error);
        this.errorMessage = "An error occurred while fetching comments.";
        this.loading = false;
      }
    },
    async submitComment() {
      if (!this.newComment.trim()) return;

      try {
        // Retrieve the author ID of the logged-in user from local storage
        const currentAuthor = JSON.parse(localStorage.getItem("user"));
        const currentAuthorId = currentAuthor ? currentAuthor.id : null;

        if (!currentAuthorId) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        const apiUrl = `/posts/${this.postId}/comment/`;
        const payload = {
          content: this.newComment,
          contentType: "text/plain",
          author_id: currentAuthorId, // Include the author ID
        };

        // Make the POST request to submit the comment
        await axios.post(apiUrl, payload, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${localStorage.getItem("token")}`, // Include the authentication token
          },
        });

        this.newComment = ""; // Clear the input field
        this.fetchComments(); // Refresh comments after submission
      } catch (error) {
        console.error("Error submitting comment:", error.response || error);
        this.errorMessage = "An error occurred while submitting the comment.";
      }
    },
    /**
     * Formats the timestamp to a more readable format.
     * @param {String} timestamp - The original timestamp.
     * @returns {String} - The formatted timestamp.
     */
  },
};
</script>



<style scoped>
/* Comment Section Container */
.comment-section {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  max-width: 600px;
  margin: 0 auto;
}

/* Section Title */
.section-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #333333;
  margin-bottom: 1rem;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #888888;
  margin-bottom: 1rem;
}

.loading-state i,
.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

/* Comments List */
.comments-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Individual Comment Item */
.comment-item {
  display: flex;
  align-items: center; /* Vertically centers avatar and author */
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

/* Avatar and Author Name Container */
.avatar-and-author {
  display: flex;
  align-items: center; /* Vertically centers the author name with the avatar */
  margin-right: 1rem;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 0.75rem;
}

.comment-author {
  font-weight: bold;
  color: #333333;
  text-align: left; /* Ensures left alignment */
}

/* Comment Details (Text and Time) */
.comment-details {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center-aligns the comment text and time */
  width: 100%;
}

.comment-text {
  font-size: 0.95rem;
  color: #333333;
  margin: 0.5rem 0;
  text-align: center; /* Center-aligns the comment text */
  max-width: 400px; /* Limits the width for better readability */
  width: 100%; /* Ensures the text takes the available width */
}

.comment-time {
  font-size: 0.75rem;
  color: #999999;
  text-align: center;
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  background-color: #ffe5e5;
  color: #cc0000;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.error-message i {
  margin-right: 0.5rem;
}

/* Comment Form */
.comment-form {
  display: flex;
  flex-direction: column;
  margin-top: 1.5rem;
}

.comment-form textarea {
  resize: vertical;
  min-height: 60px;
  padding: 0.75rem;
  border: 1px solid #dddddd;
  border-radius: 8px;
  font-size: 1rem;
  color: #333333;
  margin-bottom: 0.75rem;
  transition: border-color 0.2s;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 5px rgba(74, 144, 226, 0.5);
}

.comment-form button {
  align-self: flex-end;
  background-color: #4a90e2;
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.comment-form button:hover {
  background-color: #357abd;
}

.comment-form button:disabled {
  background-color: #a0c4e8;
  cursor: not-allowed;
}

/* Responsive Design for Smaller Screens */
@media (max-width: 600px) {
  .comment-section {
    padding: 1rem;
  }

  .comment-avatar {
    width: 35px;
    height: 35px;
  }

  .comment-author {
    font-size: 0.95rem;
  }

  .comment-text {
    max-width: 100%; /* Allow full width on small screens */
    padding: 0 1rem; /* Add some padding for better appearance */
  }

  .comment-form button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
