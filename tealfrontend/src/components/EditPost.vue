<!-- src/components/EditPost.vue -->
<template>
  <div class="edit-post-container">
    <h2>Edit Post</h2>

    <div v-if="loading" class="loading">Loading post...</div>

    <div v-else-if="!post" class="no-post">
      <p>Post not found.</p>
      <router-link to="/posts/all">Go Back</router-link>
    </div>

    <div v-else class="edit-form">
      <form @submit.prevent="savePost">
        <!-- Title Field -->
        <div class="form-group">
          <label for="title">Title:</label>
          <input v-model="editablePost.title" type="text" id="title" required />
        </div>

        <!-- Description Field -->
        <div class="form-group">
          <label for="description">Description:</label>
          <input
            v-model="editablePost.description"
            type="text"
            id="description"
          />
        </div>

        <!-- Content Field -->
        <div class="form-group">
          <label for="content">Content:</label>

          <!-- If content is an image, display it with an option to replace -->
          <div v-if="isImageContent(editablePost.content)">
            <img :src="editablePost.content" alt="Post Image" width="300" />
            <div>
              <label for="imageUpload">Replace Image:</label>
              <input
                type="file"
                id="imageUpload"
                @change="handleImageUpload"
                accept="image/*"
              />
            </div>
          </div>

          <!-- If content is text, display a textarea for Markdown editing -->
          <div v-else>
            <textarea
              v-model="editablePost.content"
              id="content"
              rows="5"
              placeholder="Enter Markdown content"
            ></textarea>
          </div>
        </div>

        <!-- Visibility Field -->
        <div class="form-group">
          <label for="visibility">Visibility:</label>
          <select v-model="editablePost.visibility" id="visibility">
            <option value="PUBLIC">Public</option>
            <option value="FRIENDS">Friends</option>
            <option value="PRIVATE">Private</option>
            <option value="INVISIBLE">Invisible</option>
          </select>
        </div>

        <!-- Submit and Cancel Buttons -->
        <div class="form-actions">
          <button type="submit">Save Changes</button>
          <router-link to="/posts/all" class="cancel-button"
            >Cancel</router-link
          >
        </div>
      </form>

      <!-- Error Messages -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import TurndownService from "turndown";
import { marked } from "marked";

export default {
  name: "EditPost",
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      post: null, // Original post data from the backend
      editablePost: {}, // Editable copy of the post
      loading: true,
      errorMessage: "",
      authID: "",
    };
  },
  mounted() {
    this.initializeUser();
    this.fetchPost();
  },
  methods: {
    // Initialize user information from localStorage
    initializeUser() {
      try {
        const user = JSON.parse(localStorage.getItem("user"));
        if (user && user.id) {
          this.authID = user.id.split("/").pop();
        } else {
          throw new Error("User information not found");
        }
      } catch (error) {
        console.error("Error initializing user:", error);
        this.errorMessage = "Failed to retrieve user information.";
      }
    },

    // Fetch the post data from the backend
    async fetchPost() {
      try {
        const apiUrl = `http://localhost:8000/project/service/api/authors/${encodeURIComponent(
          this.authID
        )}/posts/${encodeURIComponent(this.id)}`;

        const response = await axios.get(apiUrl);
        this.post = response.data;

        // Create an editable copy of the post
        this.editablePost = { ...this.post };

        // Convert HTML fields to Markdown if they are not images
        this.convertHtmlToMarkdown();

        this.loading = false;
      } catch (error) {
        console.error("Error fetching post:", error.response || error);
        this.errorMessage = "An error occurred while fetching the post.";
        this.loading = false;
      }
    },

    // Convert HTML content to Markdown for editing
    convertHtmlToMarkdown() {
      if (this.editablePost) {
        const turndownService = new TurndownService();

        // Convert title if it's HTML
        if (this.isHtml(this.editablePost.title)) {
          this.editablePost.title = turndownService.turndown(
            this.editablePost.title
          );
        }

        // Convert description if it's HTML
        if (this.isHtml(this.editablePost.description)) {
          this.editablePost.description = turndownService.turndown(
            this.editablePost.description
          );
        }

        // Convert content if it's HTML and not an image
        if (
          this.isHtml(this.editablePost.content) &&
          !this.isImageContent(this.editablePost.content)
        ) {
          this.editablePost.content = turndownService.turndown(
            this.editablePost.content
          );
        }
      }
    },

    // Check if a string contains HTML tags
    isHtml(text) {
      const htmlRegex = /<\/?[a-z][\s\S]*>/i;
      return htmlRegex.test(text);
    },

    // Check if the content is image data
    isImageContent(content) {
      if (!content) return false;

      // Use regex to check if content contains a base64 image data URI
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      const isImage = match !== null;

      return isImage;
    },

    // Extract the base64 image data from the content
    extractImageSrc(content) {
      if (!content) return "";

      // Extract the data URI using regex
      const regex = /data:image\/[a-zA-Z]+;base64,[^\s<]+/;
      const match = content.match(regex);
      const src = match ? match[0] : "";

      return src;
    },

    // Strip HTML tags from content
    stripHtmlTags(content) {
      if (!content) return "";
      return content.replace(/<\/?[^>]+(>|$)/g, "").trim();
    },

    // Handle image upload and convert to base64
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();

        reader.onload = (e) => {
          this.editablePost.content = e.target.result;
        };

        reader.readAsDataURL(file);
      }
    },

    // Save the edited post
    async savePost() {
      try {
        const apiUrl = `http://localhost:8000/project/service/api/authors/${encodeURIComponent(
          this.authID
        )}/posts/${encodeURIComponent(this.id)}`;

        // If content is not an image, convert Markdown to HTML
        if (!this.isImageContent(this.editablePost.content)) {
          this.editablePost.content = marked(this.editablePost.content || "");
        }

        // Similarly, convert title and description back to HTML if needed
        if (this.isHtml(this.editablePost.title) === false) {
          this.editablePost.title = marked(this.editablePost.title || "");
        }

        if (this.isHtml(this.editablePost.description) === false) {
          this.editablePost.description = marked(
            this.editablePost.description || ""
          );
        }

        await axios.put(apiUrl, this.editablePost, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        alert("Post updated successfully.");
        this.$router.push("/posts/all"); // Redirect to All Posts
      } catch (error) {
        console.error("Error updating post:", error.response || error);
        this.errorMessage = "An error occurred while updating the post.";
      }
    },
  },
};
</script>

<style scoped>
.edit-post-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.edit-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

input[type="text"],
textarea,
select {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

button[type="submit"] {
  padding: 10px 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
  margin-right: 10px;
}

button[type="submit"]:hover {
  background-color: #45a049;
}

.cancel-button {
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.cancel-button:hover {
  background-color: #c0392b;
}

.loading,
.no-post {
  text-align: center;
  font-size: 1.2em;
  color: #7f8c8d;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  background-color: #f2dede;
  color: #a94442;
}
</style>
