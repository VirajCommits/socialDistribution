<template>
  <div class="public-profile-container">
    <!-- Header Section -->
    <div class="public-profile-header">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
      </button>
      <h1>{{ user.displayName }}</h1>
    </div>

    <!-- Profile Info Section -->
    <div class="profile-info">
      <img
        :src="user.profileImage || defaultProfileImage"
        :alt="`${user.displayName}'s profile image`"
        class="profile-image"
        @error="handleImageError"
      />
      <div class="user-info">
        <p><strong>Username:</strong> {{ user.username }}</p>
        <p v-if="user.github">
          <strong>GitHub:</strong>
          <a :href="user.github" target="_blank">{{ user.github }}</a>
        </p>
        <p v-else><strong>GitHub:</strong> Not Connected</p>
      </div>

      <!-- Stats Section -->
      <div class="stats-container">
        <div class="stat">
          <h2>{{ stats.followers }}</h2>
          <p>Followers</p>
        </div>
        <div class="stat">
          <h2>{{ stats.following }}</h2>
          <p>Following</p>
        </div>
        <div class="stat">
          <h2>{{ stats.friends }}</h2>
          <p>Friends</p>
        </div>
      </div>
    </div>

    <!-- Public Posts Section -->
    <div class="public-posts-section">
      <h2>Public Posts</h2>
      <div v-if="loadingPosts" class="loading">
        <i class="fas fa-spinner fa-spin"></i> Loading posts...
      </div>
      <div v-else-if="!publicPosts.length" class="no-posts">
        <p>No public posts available for this author.</p>
      </div>
      <div v-else class="posts-container">
        <div v-for="post in publicPosts" :key="post.id" class="post-card">
          <div class="post-header">
            <h3 v-if="post.title && post.title.trim()">{{ post.title }}</h3>
            <span v-if="post.visibility === 'PUBLIC'" class="visibility-tag">PUBLIC</span>
          </div>
          <p v-if="post.description && post.description.trim()" class="post-description">
            {{ post.description }}
          </p>
          <div v-if="isImageContent(post.content)" class="post-image">
            <img :src="post.content" alt="Post Content" />
          </div>
          <p v-if="post.content && post.content.trim()" class="post-content">
            {{ post.content }}
          </p>
          <div class="post-footer">
            <span><strong>Author:</strong> {{ user.displayName }}</span>
            <LikeButton :postId="post.id" />
          </div>
          <CommentSection :postId="post.id" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import CommentSection from "./CommentSection.vue";
import LikeButton from "./LikeButton.vue";

export default {
  name: "PublicProfilePage",
  props: ["authorId"], // Accept authorId as a prop
  components: {
    CommentSection,
    LikeButton,
  },
  data() {
    return {
      user: null,
      stats: {
        followers: 0,
        following: 0,
        friends: 0,
      },
      defaultProfileImage: "https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg",
      publicPosts: [],
      loadingPosts: true,
    };
  },
  async mounted() {
    await this.fetchPublicProfile(this.authorId);
    await this.fetchStats(this.authorId);
    await this.fetchPublicPosts(this.authorId);
  },
  methods: {
    async fetchPublicProfile(authorId) {
      try {
        const response = await axios.get(`/authors/${authorId}/public/`);
        this.user = response.data;
      } catch (error) {
        console.error("Error fetching public profile:", error);
      }
    },
    async fetchStats(authorId) {
      try {
        const response = await axios.get(`/authors/${authorId}/stats/public/`);
        this.stats = response.data;
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    },
    async fetchPublicPosts(authorId) {
      try {
        const response = await axios.get(`/authors/${authorId}/post/public/`);
        this.publicPosts = response.data;
      } catch (error) {
        console.error("Error fetching public posts:", error);
      } finally {
        this.loadingPosts = false;
      }
    },
    isImageContent(content) {
      if (!content) return false;
      const regex = /https?:\/\/.*\.(jpg|jpeg|png|gif)$/i; // Check for valid image URLs
      return regex.test(content);
    },

    handleImageError(e) {
      e.target.src = this.defaultProfileImage;
    },
    goBack() {
      this.$router.go(-1);
    },
  },
};
</script>

<style scoped>
/* General Styling */
.public-profile-container {
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.public-profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 20px;
}

.profile-info {
  text-align: center;
  margin-bottom: 2rem;
}

.profile-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  margin-bottom: 1rem;
  border: 3px solid #ccc;
}

.user-info p {
  margin: 0.5rem 0;
  font-size: 1rem;
}

/* Stats Section */
.stats-container {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1rem;
}

.stat {
  text-align: center;
}

.stat h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #2980b9;
}

.stat p {
  margin: 0;
  font-size: 1rem;
  color: #7f8c8d;
}

/* Public Posts Section */
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
