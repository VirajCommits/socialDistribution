<!-- src/components/AuthorPosts.vue -->
<template>
  <div class="author-posts-container">
    <h2>Your Public Posts</h2>

    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading posts...
    </div>

    <div v-else-if="filteredPosts.length === 0" class="no-posts">
      <p>
        No public posts found.
        <router-link to="/posts/create" class="create-link"
          >Create your first post!</router-link
        >
      </p>
    </div>

    <div v-else class="posts-grid">
      <div class="post-card" v-for="post in filteredPosts" :key="post.id">
        <div class="post-content">
          {{ console.log(post) }}
          <h3>{{ post.title }}</h3>
          <p>{{ post.description }}</p>
          <div v-if="post.content && post.content.includes('data:image')">
            <img :src="post.content" alt="Post Image" width="300" />
          </div>

          <p>
            <strong>Visibility:</strong>
            <span :class="`visibility-${post.visibility.toLowerCase()}`">{{
              post.visibility
            }}</span>
          </p>
        </div>
        <div class="post-actions">
          <router-link
            :to="{ name: 'EditPost', params: { id: post.id } }"
            class="edit-button"
          >
            <i class="fas fa-edit"></i> Edit
          </router-link>
          <button @click="setPostInvisible(post)" class="delete-button">
            <i class="fas fa-trash-alt"></i> Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Selected post details (if any) -->
    <div v-if="selectedPost" class="selected-post-details">
      <h3>Selected Post Details</h3>
      <p><strong>Title:</strong> {{ selectedPost.title }}</p>
      <p><strong>Description:</strong> {{ selectedPost.description }}</p>
      <p><strong>Content:</strong> {{ selectedPost.content }}</p>
      <p><strong>Content Type:</strong> {{ selectedPost.contentType }}</p>
      <p><strong>Visibility:</strong> {{ selectedPost.visibility }}</p>
    </div>

    <!-- Display error messages -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AuthorPosts",
  props: {
    authorId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      posts: [],
      selectedPost: null,
      loading: true,
      errorMessage: "",
    };
  },
  computed: {
    filteredPosts() {
      return this.posts.filter(
        (post) => post.visibility === "PUBLIC" && post.visibility !== null
      );
    },
  },
  mounted() {
    this.fetchPosts();
    this.user = JSON.parse(localStorage.getItem("user"));
    this.authID = this.user.id.split("/").pop();
  },
  methods: {
    async fetchPosts() {
      this.user = JSON.parse(localStorage.getItem("user"));
      this.authID = this.user.id.split("/").pop();
      console.log("))))))))", this.user, this.authID);
      try {
        const apiUrl = `${
          process.env.VUE_APP_API_BASE_URL
        }/authors/${encodeURIComponent(this.authID)}/posts/all/`;

        const response = await axios.get(apiUrl);
        // Adjust based on your actual API response structure
        this.posts = response.data.results.items || [];
        this.loading = false;
      } catch (error) {
        console.error("Error fetching posts:", error.response || error);
        this.errorMessage = "An error occurred while fetching posts.";
        this.loading = false;
      }
    },

    async setPostInvisible(post) {
      const authorId = this.authID; // Ensure correct author ID path
      const postId = post.id;

      console.log(" ------------- ", authorId);

      const updateUrl = `${process.env.VUE_APP_API_BASE_URL}/authors/${authorId}/posts/${postId}`;

      if (
        confirm(
          `Are you sure you want to make the post titled "${post.title}" invisible?`
        )
      ) {
        try {
          const updatedPost = { visibility: "INVISIBLE" };

          await axios.put(updateUrl, updatedPost, {
            headers: {
              "Content-Type": "application/json",
            },
          });

          // Update the post visibility in the list
          this.posts = this.posts.map((p) =>
            p.id === post.id ? { ...p, visibility: "INVISIBLE" } : p
          );
          alert("Post visibility updated successfully.");
        } catch (error) {
          console.error(
            "Error updating post visibility:",
            error.response || error
          );
          this.errorMessage =
            "An error occurred while updating post visibility.";
        }
      }
    },

    selectPost(post) {
      this.selectedPost = post;
    },
  },
};
</script>

<style scoped>
.author-posts-container {
  padding: 20px;
  max-width: 800px; /* Adjusted for better vertical layout */
  margin: 0 auto;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.loading {
  text-align: center;
  font-size: 1.2em;
  color: #3498db;
}

.no-posts {
  text-align: center;
  font-size: 1.1em;
  color: #7f8c8d;
}

.create-link {
  color: #e67e22;
  font-weight: bold;
}

.create-link:hover {
  text-decoration: underline;
}

.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  background-color: #ffffff;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.post-card:hover {
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.post-content {
  padding: 20px;
}

.post-content h3 {
  margin-top: 0;
  color: #2980b9;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.post-content p {
  color: #34495e;
  line-height: 1.6;
}

.visibility-public {
  color: #27ae60;
  font-weight: bold;
}

.visibility-friends {
  color: #f1c40f;
  font-weight: bold;
}

.visibility-private,
.visibility-invisible {
  color: #c0392b;
  font-weight: bold;
}

.post-actions {
  display: flex;
  justify-content: flex-start;
  padding: 15px 20px;
  border-top: 1px solid #ecf0f1;
  background-color: #f9f9f9;
  gap: 10px;
}

.edit-button,
.delete-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.9em;
  transition: background-color 0.2s ease;
}

.edit-button {
  background-color: #3498db;
  color: #ffffff;
}

.edit-button:hover {
  background-color: #2980b9;
}

.delete-button {
  background-color: #e74c3c;
  color: #ffffff;
}

.delete-button:hover {
  background-color: #c0392b;
}

.selected-post-details {
  margin-top: 40px;
  padding: 20px;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  background-color: #fdfefe;
}

.selected-post-details h3 {
  margin-top: 0;
  color: #8e44ad;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  background-color: #f2dede;
  color: #a94442;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message i {
  font-size: 1.2em;
}

/* Responsive Design */
@media (max-width: 600px) {
  .author-posts-container {
    padding: 15px;
  }

  .post-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .edit-button,
  .delete-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
