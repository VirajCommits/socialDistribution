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
    authorId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      liked: false,
      likeCount: 0,
    };
  },
  mounted() {
    this.fetchLikes();
  },
  methods: {
    async fetchLikes() {
      try {
        const apiUrl = `http://localhost:8000/project/service/authors/${this.authorId}/posts/${this.postId}/likes/`;
        const response = await axios.get(apiUrl);
        this.likeCount = response.data.length || 0;

        // Check if the logged-in author has liked the post (for demo purposes, assuming authorId)
        this.liked = response.data.some(
          (like) => like.author.id === this.authorId
        );
      } catch (error) {
        console.error("Error fetching likes:", error.response || error);
      }
    },
    async toggleLike() {
      try {
        const apiUrl = `http://localhost:8000/project/service/authors/${this.authorId}/posts/${this.postId}/like/`;
        if (this.liked) {
          // Unlike logic can be implemented if needed (requires backend support for DELETE like)
          alert("Unliking not implemented yet.");
        } else {
          await axios.post(apiUrl, {
            author_id: this.authorId,
            post_id: this.postId,
          });

          this.liked = true;
          this.likeCount += 1;
        }
      } catch (error) {
        console.error("Error toggling like:", error.response || error);
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
