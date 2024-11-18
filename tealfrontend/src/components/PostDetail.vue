<template>
  <div class="single-post-container">
    <!-- Loading Spinner -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading post...
    </div>

    <!-- No Post Found Message -->
    <div v-else-if="!post" class="no-post">
      <p>Post not found or not available.</p>
    </div>

    <!-- Post Content -->
    <div v-else class="post-card">
      <div class="post-content">
        <h3 v-html="post.title"></h3>
        <p v-html="post.description"></p>

        <!-- Display Image if Content is an Image -->
        <div v-if="isImageContent(post.content)">
          <img :src="extractImageSrc(post.content)" alt="Post Image" width="300" />
        </div>

        <!-- Display Text Content -->
        <div v-else>
          <p v-html="post.content"></p>
        </div>

        <p><strong>Author:</strong> {{ post.author.displayName }}</p>
        <p><strong>Visibility:</strong> {{ post.visibility }}</p>

        <!-- Like Button Component -->
        <LikeButton :postId="post.id" :authorId="authID" :isUserLoggedIn="!!user" />

        <!-- Comment Section Component -->
        <CommentSection :postId="post.id" :authorId="authID" :isUserLoggedIn="!!user" />

        <!-- Login Message for Guest Users -->
        <div v-if="!user" class="login-message">
          <p>Please <router-link to="/login">log in</router-link> or <router-link to="/signup">sign up</router-link> to like and comment on this post.</p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import CommentSection from "./CommentSection.vue";
import LikeButton from "./LikeButton.vue";

export default {
  name: "SinglePostView",
  props: {
    postId: {
      type: String,
      required: true,
    },
  },
  components: {
    CommentSection,
    LikeButton,
  },
  data() {
    return {
      post: null,
      loading: true,
      errorMessage: "",
      user: null,
      authID: "",
    };
  },
  mounted() {
    this.initializeUser();
    this.fetchPost();
  },
  methods: {
    // Method to fetch the post details
    async fetchPost() {
      try {
        console.log("fetching post");
        const apiUrl = `/posts/${this.postId}/`;
        
        const response = await axios.get(apiUrl);
        this.post = response.data;
        this.loading = false;
      } catch (error) {
        console.error("Error fetching post:", error);
        this.errorMessage = "An error occurred while fetching the post.";
        this.loading = false;
      }
    },
    // Method to check if content is an image
    isImageContent(content) {
      if (!content) return false;
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      return regex.test(content);
    },
    // Method to extract image source from content
    extractImageSrc(content) {
      if (!content) return "";
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      return match ? match[0] : "";
    },
    // Method to initialize user
    initializeUser() {
      try {
        this.user = JSON.parse(localStorage.getItem("user"));
        if (this.user && this.user.id) {
          this.authID = this.user.id.split("/").pop();
        } else {
          this.user = null;
        }
      } catch (error) {
        console.error("Error initializing user:", error);
        this.user = null;
      }
    },
  },
};
</script>

<style scoped>
.single-post-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f6fa;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
  padding-right: 10px;
}

h3 {
  color: #2980b9;
}

.loading {
  text-align: center;
  font-size: 1.2em;
  color: #3498db;
}

.no-post {
  text-align: center;
  font-size: 1.1em;
  color: #7f8c8d;
}

.post-card {
  background-color: #ffffff;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.post-content p {
  color: #34495e;
  line-height: 1.6;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  background-color: #f2dede;
  color: #a94442;
}

.login-message {
  text-align: center;
  font-size: 1em;
  color: #7f8c8d;
  margin-top: 20px;
}

.login-message a {
  color: #3498db;
  font-weight: bold;
  text-decoration: none;
}

.login-message a:hover {
  text-decoration: underline;
}
</style>
