<template>
  <div class="public-profile-container">
    <!-- Header Section -->
    <div class="public-profile-header">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
      </button>
      <div class="header-bg">
        <div class="profile-image-container">
          <img
            :src="user.profileImage || defaultProfileImage"
            alt="Profile Image"
            class="profile-image"
            @error="handleImageError"
          />
        </div>
      </div>
    </div>

    <!-- Profile Info Section -->
    <div class="profile-info">
      <h2 class="display-name">{{ user.displayName }}</h2>
      <div class="stats-container">
        <div class="stat">
          <h3>{{ stats.following }}</h3>
          <p>Following</p>
        </div>
        <div class="stat">
          <h3>{{ stats.followers }}</h3>
          <p>Followers</p>
        </div>
        <div class="stat">
          <h3>{{ stats.friends }}</h3>
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
        No public posts available for this author.
      </div>
      <div v-else class="posts-container">
        <div v-for="post in publicPosts" :key="post.id" class="post-card">
          <div class="post-content">
            <h3 v-if="post.title && post.title.trim()" v-html="post.title"></h3>
            <p v-if="post.description && post.description.trim()" v-html="post.description"></p>

            <!-- Content Logic -->
            <div v-if="post.content && post.content.trim()">
              <!-- Image Content -->
              <div v-if="isImageContent(post.content)" class="post-image">
                <img :src="extractImageSrc(post.content)" alt="Post Content" />
              </div>
              <!-- Text Content -->
              <p v-else v-html="post.content"></p>
            </div>


            <!-- Fallback for No Description and Content -->
            <div v-else>
              <p class="no-content">No description or content available.</p>
            </div>

            <p><strong>Author:</strong> {{ user.displayName }}</p>
            <p><strong>Visibility:</strong> {{ post.visibility }}</p>

            <!-- Like Button -->
            <LikeButton :postId="post.id" />

            <!-- Comments Section -->
            <CommentSection :postId="post.id" />
          </div>
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
  props: ["authorId"],
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
    const authorUuid = this.extractUuid(this.authorId);
    await this.fetchPublicProfile(authorUuid);
    await this.fetchStats(authorUuid);
    await this.fetchPublicPosts(authorUuid);
  },
  methods: {
    extractUuid(authorId) {
      // Extract UUID from authorId (URL)
      return authorId.split("/").pop();
    },
    async fetchPublicProfile(authorUuid) {
      try {
        const response = await axios.get(`/authors/${authorUuid}/public/`);
        this.user = response.data;
      } catch (error) {
        console.error("Error fetching public profile:", error);
      }
    },
    async fetchStats(authorUuid) {
      try {
        const response = await axios.get(`/authors/${authorUuid}/stats/public/`);
        this.stats = response.data;
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    },
    async fetchPublicPosts(authorUuid) {
      try {
        const response = await axios.get(`/authors/${authorUuid}/post/public/`);
        this.publicPosts = response.data;
      } catch (error) {
        console.error("Error fetching public posts:", error);
      } finally {
        this.loadingPosts = false;
      }
    },
    showNotification(message, type = "success") {
      // Placeholder for notification system (console for now)
      console.log(type.toUpperCase() + ": " + message);
    },
    isImageContent(content) {
      if (!content) return false;
      const regex = /https?:\/\/.*\.(jpg|jpeg|png|gif)$/i;
      return regex.test(content);
    },
    extractImageSrc(content) {
      return content; // Modify this method if you need to parse the content
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
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  background-color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.back-button i {
  font-size: 16px;
  color: #3498db;
}

.public-profile-header {
  background: linear-gradient(90deg, #4facfe, #00f2fe);
  padding: 40px 0;
  text-align: center;
  position: relative;
}

.profile-image-container {
}

.profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid white;
}

.profile-info {
  text-align: center;
  margin-top: 20px;
}

.display-name {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.stats-container {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  gap: 30px;
}

.stat h3 {
  font-size: 1.2rem;
  color: #3498db;
}

.stat p {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.posts-container {
  padding: 20px;
}

.post-card {
  background-color: #ffffff;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.no-content {
  color: #7f8c8d;
  font-style: italic;
  margin-top: 10px;
}
.follow-button {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.3s ease;
}

.follow-button.following {
  background-color: #f44336; /* Red for unfollow */
}

.follow-button.pending {
  background-color: #ffc107; /* Yellow for pending */
  cursor: not-allowed;
}

.follow-button:hover:not(.pending) {
  background-color: #45a049; /* Darker green for hover */
}

.follow-button.following:hover {
  background-color: #d32f2f; /* Darker red for hover */
}

</style>
