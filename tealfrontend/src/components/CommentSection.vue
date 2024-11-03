<template>
  <div class="comment-section">
    <h4>Comments ({{ comments.length }})</h4>

    <div v-if="loading">Loading comments...</div>
    <div v-else-if="comments.length === 0">No comments yet.</div>
    <div v-else>
      <ul>
        <li v-for="comment in comments" :key="comment.id">
          <p>
            <strong>{{ comment.author.displayName }}:</strong>
            {{ comment.content }}
          </p>
        </li>
      </ul>
    </div>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="Write a comment..."
        rows="3"
      ></textarea>
      <button @click="submitComment">Submit</button>
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
    };
  },
  mounted() {
    this.fetchComments();
  },
  methods: {
    async fetchComments() {
      try {
        const apiUrl = `http://localhost:8000/service/api/posts/${this.postId}/comments/`;
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
        const currentAuthorId = JSON.parse(localStorage.getItem("user")).id;
        const apiUrl = `http://localhost:8000/service/api/posts/${this.postId}/comment/`;
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
  },
};
</script>

<style scoped>
.comment-section {
  margin-top: 20px;
}

.comment-form {
  margin-top: 10px;
}

textarea {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

button {
  padding: 8px 16px;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #2980b9;
}
</style>
