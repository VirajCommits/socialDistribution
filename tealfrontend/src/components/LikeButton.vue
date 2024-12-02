
<template>
  <button @click="toggleLike" class="like-button">
    <i v-if="liked" class="fas fa-heart liked"></i>
    <i v-else class="far fa-heart"></i>
    { likeCount }
  </button>
</template>

<script>
export default {
  name: "LikeButton",
  props: {
    initialLikes: {
      type: Number,
      default: 0
    },
    initiallyLiked: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      likeCount: this.initialLikes,
      liked: this.initiallyLiked
    };
  },
  methods: {
    async toggleLike() {
      try {
        // Simulate API call for toggling like
        const newState = !this.liked;
        await this.$emit("like-toggled", newState); // Notify parent
        this.liked = newState;
        this.likeCount += this.liked ? 1 : -1;
      } catch (error) {
        console.error("Error toggling like:", error);
      }
    }
  }
};
</script>

<style scoped>
.like-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.liked {
  color: red;
}
</style>
