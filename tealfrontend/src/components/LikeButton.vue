<template>
  <div class="like-button">
    <button @click="toggleLike">
      <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i> {{ likeCount }}
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
        const apiUrl = `http://localhost:8000/project/service/api/posts/${this.postId}/likes/`;
        const response = await axios.get(apiUrl);
        this.likeCount = response.data.length || 0;

        // Check if the logged-in author has liked the post
        const currentAuthorId = JSON.parse(localStorage.getItem("user")).id;
        this.liked = response.data.some(
          (like) => like.author.id === currentAuthorId
        );
      } catch (error) {
        console.error("Error fetching likes:", error.response || error);
        this.errorMessage = "An error occurred while fetching likes.";
      }
    },
    async toggleLike() {
      try {
        const currentAuthorId = JSON.parse(localStorage.getItem("user")).id;
        const apiUrl = `http://localhost:8000/project/service/api/posts/${this.postId}/like/`;

        if (this.liked) {
          // If unliking is needed, add the logic here
          alert("Unliking is not implemented yet.");
        } else {
          // Post a like
          const payload = {
            author_id: currentAuthorId, // Include the author ID
            post_id: this.postId,
          };

          await axios.post(apiUrl, payload, {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Token ${localStorage.getItem("token")}`, // Include the token for authentication
            },
          });

          this.liked = true; // Mark as liked
          this.likeCount += 1; // Increment the like count
        }
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
        this.errorMessage = "An error occurred while liking the post.";
      }
    },
  },
};
</script>



<style scoped>
button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1em;
  color: #e74c3c;
}

button:hover {
  color: #c0392b;
}
</style>
