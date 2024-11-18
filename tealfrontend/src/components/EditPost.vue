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

          <!-- If content is an image, display it with an option to replace and a text field -->
          <div
            v-if="isImageContent(editablePost.content)"
            class="image-content"
          >
            <img
              :src="extractImageSrc(editablePost.content)"
              alt="Post Image"
              width="300"
              loading="lazy"
            />
            <div class="replace-image">
              <label for="imageUpload">Replace Image:</label>
              <input
                type="file"
                id="imageUpload"
                @change="handleImageUpload"
                accept="image/*"
              />
            </div>
            <div class="replace-text">
              <label for="textContent">Add Text Content:</label>
              <textarea
                v-model="newTextContent"
                id="textContent"
                rows="5"
                placeholder="Enter Markdown content to replace the image"
              ></textarea>
            </div>
          </div>

          <!-- If content is text, display a textarea for Markdown editing and an option to replace with an image -->
          <div v-else class="text-content">
            <textarea
              v-model="editablePost.content"
              id="content"
              rows="5"
              placeholder="Enter Markdown content"
            ></textarea>
            <div class="replace-image">
              <label for="imageUploadText"
                >Replace Content with an Image:</label
              >
              <input
                type="file"
                id="imageUploadText"
                @change="handleImageUpload"
                accept="image/*"
              />
            </div>
          </div>
        </div>

        <!-- Visibility Field -->
        <div class="form-group">
          <label for="visibility">Visibility:</label>
          <select v-model="editablePost.visibility" id="visibility">
            <option value="PUBLIC">Public</option>
            <option value="FRIENDS">Friends</option>
            <option value="UNLISTED">Unlisted</option>
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
      newTextContent: "", // New text content to replace image
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
  watch: {
    newTextContent(newVal) {
      if (newVal.trim() !== "") {
        this.editablePost.content = newVal.trim();
      }
    },
  },
  methods: {
    // Initialize user information from localStorage
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

    // Fetch the post data from the backend
    async fetchPost() {
      try {
        const apiUrl = `/authors/${encodeURIComponent(
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
      return match ? match[0] : "";
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
          this.newTextContent = ""; // Clear the text field if image is uploaded
        };

        reader.readAsDataURL(file);
      }
    },

    // Save the edited post
    async savePost() {
      try {
        const apiUrl = `/authors/${encodeURIComponent(
          this.authID
        )}/posts/${encodeURIComponent(this.id)}`;

        // If content is not an image, convert Markdown to HTML
        if (!this.isImageContent(this.editablePost.content)) {
          this.editablePost.content = marked(this.editablePost.content || "");
        }

        // Similarly, convert title and description back to HTML if needed
        if (!this.isHtml(this.editablePost.title)) {
          this.editablePost.title = marked(this.editablePost.title || "");
        }

        if (!this.isHtml(this.editablePost.description)) {
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
/* Import Google Fonts */
@import url("https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap");

/* General Styles */
.edit-post-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: "Roboto", sans-serif;

  /* Added Properties for Scrollability and Hiding Scrollbar */
  max-height: 90vh; /* Sets the maximum height to 90% of the viewport height */
  overflow-y: auto; /* Enables vertical scrolling when content exceeds max-height */
  padding-right: 10px; /* Adds space for scrollbar to prevent content overlap */
}

/* Hide Scrollbar for Webkit Browsers */
.edit-post-container::-webkit-scrollbar {
  width: 0px;
  background: transparent; /* Optional: just make scrollbar invisible */
}

/* Hide Scrollbar for IE, Edge and Firefox */
.edit-post-container {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

/* Heading Styles */
.edit-post-container h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

/* Edit Form Styling */
.edit-form {
  max-width: 600px;
  margin: 0 auto;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 30px 40px;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* Form Group */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 8px;
  color: #34495e;
}

/* Input, Textarea, Select Styling */
.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="url"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px 20px;
  border: 1px solid #cccccc;
  border-radius: 30px;
  box-sizing: border-box;
  font-size: 16px;
  background-color: #f7f7f7;
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.form-group input[type="text"]:focus,
.form-group input[type="email"]:focus,
.form-group input[type="password"]:focus,
.form-group input[type="url"]:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #66afe9;
  background-color: #ffffff;
  outline: none;
}

/* Replace Image and Text Sections */
.replace-image,
.replace-text {
  margin-top: 15px;
}

.replace-image label,
.replace-text label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #34495e;
}

.replace-image input,
.replace-text textarea {
  width: 100%;
}

.replace-text textarea {
  resize: vertical;
  height: 100px;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-actions button[type="submit"] {
  padding: 12px 25px;
  background-color: #4caf50;
  border: none;
  border-radius: 30px;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 700;
}

.form-actions button[type="submit"]:hover {
  background-color: #45a049;
}

.form-actions .cancel-button {
  padding: 12px 25px;
  background-color: #e74c3c;
  border: none;
  border-radius: 30px;
  color: white;
  font-size: 18px;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 700;
}

.form-actions .cancel-button:hover {
  background-color: #c0392b;
}

/* Error Message */
.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  background-color: #f2dede;
  color: #a94442;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Loading */
.loading {
  text-align: center;
  font-size: 1.2em;
  color: #3498db;
}

/* No Post */
.no-post {
  text-align: center;
  font-size: 1.1em;
  color: #7f8c8d;
}

/* Image Content Styling */
.image-content img {
  border-radius: 8px;
  margin-bottom: 15px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .edit-form {
    padding: 20px 30px;
  }

  .form-actions {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions button[type="submit"],
  .form-actions .cancel-button {
    width: 100%;
  }
}
</style>
