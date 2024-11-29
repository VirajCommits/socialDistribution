<template>
  <div class="author-posts-container">
    <!--  Stream Button -->
    <button class="go-back-button" @click="goBackToStream">
      Back to Stream
    </button>

    <h2>Your Public Posts</h2>

    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading posts...
    </div>

    <div v-else-if="filteredPosts.length === 0" class="no-posts">
      <p>
        No public posts found.
        <router-link to="/posts/create" class="create-link">
          Create your first post!
        </router-link>
      </p>
    </div>

    <div v-else class="posts-grid">
      <button class="create-post" @click="makePost">Create another Post</button>

      <div class="post-card" v-for="post in filteredPosts" :key="post.id">
        <div class="post-content">
          <h3 v-html="post.title"></h3>
          <p v-html="post.description"></p>

          <div v-if="isImageContent(post.content)">
            <img
              :src="extractImageSrc(post.content)"
              alt="Post Image"
              width="300"
            />
          </div>

          <div v-else>
            <p v-html="post.content"></p>
          </div>

          <p>
            <strong>Visibility:</strong>
            <span :class="`visibility-${post.visibility.toLowerCase()}`">{{
              post.visibility
            }}</span>
          </p>

          <LikeButton :postId="post.id" :authorId="authID" />

          <CommentSection :postId="post.id" :authorId="authID" />
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

    <!-- Error messages -->
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
  name: "AuthorPosts",
  props: {
    authorId: {
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
      posts: [],
      comments: [], // Initialize as an empty array
      likes: [], // Initialize as an empty array
      selectedPost: null,
      loading: true,
      errorMessage: "",
      user: null,
      authID: "", // Ensure this is properly initialized
    };
  },
  computed: {
    filteredPosts() {
      return this.posts.filter((post) => post.visibility !== "INVISIBLE");
    },
  },
  mounted() {
    this.initializeUser();
    this.fetchPosts();
  },
  methods: {
    isImageContent(content) {
      if (!content) return false;

      // Use regex to extract the data URI
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      const isImage = match !== null;

      return isImage;
    },

    extractImageSrc(content) {
      if (!content) return "";

      // Extract the data URI using regex
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      const src = match ? match[0] : "";

      return src;
    },

    makePost() {
      this.$router.push("/addPost");
    },

    initializeUser() {
      try {
        this.user = JSON.parse(localStorage.getItem("user"));
        if (this.user && this.user.id) {
          this.authID = this.user.id.split("/").pop();
        } else {
          throw new Error("User information not found");
        }
      } catch (error) {
        console.error("Error initializing user:", error);
        this.errorMessage = "Failed to retrieve user information.";
      }
    },
    async fetchPosts() {
      this.user = JSON.parse(localStorage.getItem("user"));
      this.authID = this.user.id.split("/").pop();
      try {
        const apiUrl = `http://localhost:8000/service/api/authors/${encodeURIComponent(
          this.authID
        )}/posts/all/`;

        // try {
        //  const apiUrl = `${process.env.VUE_APP_API_BASE_URL}/authors/${encodeURIComponent(this.authID)}/posts/all/`;

        const response = await axios.get(apiUrl);
        // Safely access the API response structure
        this.posts =
          response.data?.results?.items || response.data?.items || [];
        this.loading = false;
      } catch (error) {
        console.error("Error fetching posts:", error.response || error);
        this.errorMessage = "An error occurred while fetching posts.";
        this.loading = false;
      }
    },
    async setPostInvisible(post) {
      const authorId = this.authID;
      const postId = post.id;

      const updateUrl = `http://localhost:8000/service/api/authors/${authorId}/posts/${postId}`;
      // const updateUrl = `${process.env.VUE_APP_API_BASE_URL}/authors/${authorId}/posts/${postId}`;

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

    // New Method to Redirect to Stream
    goBackToStream() {
      // Alternatively, if you want to use Vue Router for navigation within the app:
      this.$router.push("/stream");
    },
  },
};
</script>

<style scoped>
.author-posts-container {
  padding: 20px;
  max-width: 800px; /* Adjusted for better vertical layout */
  margin: 0 auto;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f6fa;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative; /* To position the go-back-button if needed */

  /* Added Properties for Scrollability */
  max-height: 90vh; /* Sets the maximum height to 90% of the viewport height */
  overflow-y: auto; /* Enables vertical scrolling when content exceeds max-height */
  padding-right: 10px; /* Adds some space for scrollbar to prevent content overlap */
}

/* Go Back to Stream Button */
.go-back-button {
  background-color: #3498db; /* Blue background */
  color: white; /* White text */
  border: none; /* Remove default border */
  border-radius: 25px; /* Rounded corners */
  padding: 10px 20px; /* Padding for size */
  font-size: 16px; /* Font size */
  cursor: pointer; /* Pointer cursor on hover */
  transition: background-color 0.3s ease, transform 0.2s ease; /* Smooth transition */
  display: flex; /* Align icon and text */
  align-items: center; /* Center vertically */
  margin-bottom: 20px; /* Space below the button */
}

.go-back-button i {
  margin-right: 8px; /* Space between icon and text */
}

.go-back-button:hover {
  background-color: #2980b9; /* Darker blue on hover */
  transform: translateY(-2px); /* Slight lift on hover */
}

.go-back-button:active {
  background-color: #1c5980; /* Even darker blue on click */
  transform: translateY(0); /* Reset position */
}

.go-back-button:focus {
  outline: none; /* Remove default outline */
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.5); /* Custom focus outline */
}

/* Create Post Button */
.create-post {
  background-color: #4caf50; /* Green background */
  color: white; /* White text */
  padding: 12px 24px; /* Padding for a balanced button size */
  font-size: 16px; /* Larger font for readability */
  font-weight: bold; /* Bold text */
  border: none; /* Remove default border */
  border-radius: 5px; /* Rounded corners */
  cursor: pointer; /* Pointer cursor on hover */
  transition: background-color 0.3s ease, transform 0.2s ease; /* Smooth transition */
  align-self: flex-start; /* Align button to the start */
}

.create-post:hover {
  background-color: #4f46e5; /* Darker green on hover */
  transform: translateY(-2px); /* Slight lift on hover */
}

.create-post:active {
  background-color: #4f46e5; /* Even darker green when clicked */
  transform: translateY(0px); /* Reset position */
}

.create-post:focus {
  outline: none; /* Remove outline on focus */
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.5); /* Subtle green glow on focus */
}

/* Headings */
h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-size: 2em;
}

/* Loading and No Posts */
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

/* Posts Grid */
.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Post Card */
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

/* Post Content */
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

/* Post Actions */
.post-actions {
  display: flex;
  justify-content: flex-start;
  padding: 15px 20px;
  border-top: 1px solid #ecf0f1;
  background-color: #f9f9f9;
  gap: 10px;
}

/* Edit and Delete Buttons */
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

/* Error Message */
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
  .delete-button,
  .go-back-button {
    width: 100%;
    justify-content: center;
  }

  /* Adjusting padding-right to account for scrollbar on smaller screens */
  .author-posts-container {
    padding-right: 10px;
  }
}
</style>
