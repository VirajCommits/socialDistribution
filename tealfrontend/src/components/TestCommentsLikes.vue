<template>
  <div class="test-comments-likes">
    <h2>Test Comments and Likes</h2>
    <div class="like-section">
      <h3>Like Section</h3>
      <LikeButton :postId="postId" :authorId="authorId" />
    </div>

    <div class="comment-section">
      <h3>Comment Section</h3>
      <CommentSection :postId="postId" :authorId="authorId" />
    </div>
  </div>
</template>

<script>
import CommentSection from "./CommentSection.vue";
import LikeButton from "./LikeButton.vue";

export default {
  name: "TestCommentsLikes",
  components: {
    CommentSection,
    LikeButton,
  },
  data() {
    return {
      postId: "9271ea2f7d184108a0aead1065ede8fc", // Replace with a valid post ID from your backend
      authorId: "19817e9b8af1497fb863e89e10eefe68", // Hardcoded author ID for now
    };
  },
};
</script>

<style scoped>
.test-comments-likes {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.like-section,
.comment-section {
  margin-top: 20px;
}
</style>
