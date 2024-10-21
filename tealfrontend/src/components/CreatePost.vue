<template>
  <div class="create-post-container">
    <h2>Create a New Post</h2>

    <form @submit.prevent="createPost" class="post-form">
      <div class="form-group">
        <label for="title">Title<span class="required">*</span>:</label>
        <input
          v-model="form.title"
          type="text"
          id="title"
          placeholder="Enter post title"
          required
        />
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <input
          v-model="form.description"
          type="text"
          id="description"
          placeholder="Enter post description"
        />
      </div>

      <div class="form-group">
        <label for="contentType">Content Type:</label>
        <select
          v-model="form.contentType"
          id="contentType"
          @change="handleContentTypeChange"
        >
          <option value="text/plain">Plain Text</option>
          <option value="text/markdown">Markdown</option>
          <option value="image/png;base64">PNG Image (Base64)</option>
          <option value="image/jpeg;base64">JPEG Image (Base64)</option>
        </select>
      </div>

      <div class="form-group" v-if="isImageType">
        <label for="image">Image:</label>
        <input type="file" id="image" @change="handleImageUpload" />
      </div>

      <div class="form-group" v-if="!isImageType">
        <label for="content">Content:</label>
        <textarea
          v-model="form.content"
          id="content"
          placeholder="Enter post content"
          rows="5"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="visibility">Visibility:</label>
        <select v-model="form.visibility" id="visibility">
          <option value="PUBLIC">Public</option>
          <option value="FRIENDS">Friends</option>
          <option value="PRIVATE">Private</option>
        </select>
      </div>

      <button type="submit" class="submit-button">Create Post</button>
    </form>

    <div v-if="form.contentType.includes('image') && form.content">
      <h3>Image Preview</h3>
      <img :src="form.content" alt="Image Preview" width="300" />
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <i class="fas fa-check-circle"></i> {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CreatePost",
  data() {
    return {
      form: {
        title: "",
        description: "",
        contentType: "text/plain",
        content: "",
        image: null, // Add image field to hold the uploaded file
        visibility: "PUBLIC",
      },
      isImageType: false, // Track if the selected content type is an image
      response: null,
      successMessage: "",
      errorMessage: "",
    };
  },
  methods: {
    handleContentTypeChange() {
      this.isImageType = this.form.contentType.includes("image");
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          // Convert image to base64 and store it in form.content
          this.form.content = e.target.result;
        };
        reader.readAsDataURL(file); // Convert to base64 string
      }
    },
    async createPost() {
      // Clear previous messages
      this.successMessage = "";
      this.errorMessage = "";

      try {
        
        // Replace with the actual author ID
        const authorId = "45c7cdd3-02be-4f93-9078-5ef5df3e5dbb";
        const apiUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/`;

        // Create form data to handle both text and image uploads
        const formData = new FormData();
        formData.append("title", this.form.title);
        formData.append("description", this.form.description);
        formData.append("contentType", this.form.contentType);
        formData.append("visibility", this.form.visibility);

        if (this.isImageType && this.form.image) {
          formData.append("image", this.form.image); // Attach the image if selected
        } else {
          formData.append("content", this.form.content); // Attach text content if not an image
        }

        const response = await axios.post(apiUrl, formData, {
          headers: {
            "Content-Type": "multipart/form-data", // Ensure proper handling of the file
          },
        });

        this.response = response.data;

        // Display success message
        this.successMessage = "Post created successfully!";
        alert("Post created successfully.");

        // Reset form
        this.form = {
          title: "",
          description: "",
          contentType: "text/plain",
          content: "",
          image: null,
          visibility: "PUBLIC",
        };
        this.isImageType = false; // Reset image type flag

        // Optionally, redirect to another page
        this.$router.push("/posts/all");
      } catch (error) {
        console.error("Error creating post:", error.response || error);
        this.errorMessage = "An error occurred while creating the post.";
      }
    },
  },
};
</script>

<style scoped>
/* Container Styling */
.create-post-container {
  max-width: 700px;
  margin: 40px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Heading Styling */
.create-post-container h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 25px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Form Styling */
.post-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.form-group label {
  margin-bottom: 8px;
  color: #34495e;
  font-weight: 600;
}

.form-group .required {
  color: #e74c3c;
  margin-left: 5px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 15px;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  font-size: 1em;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3498db;
  outline: none;
}

/* Submit Button Styling */
.submit-button {
  padding: 12px 20px;
  background-color: #27ae60;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.3s ease;
  align-self: flex-start;
}

.submit-button:hover {
  background-color: #1e8449;
}

/* Success Message Styling */
.success-message {
  margin-top: 20px;
  padding: 15px 20px;
  background-color: #dff0d8;
  border: 1px solid #d0e9c6;
  border-radius: 5px;
  color: #3c763d;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Error Message Styling */
.error-message {
  margin-top: 20px;
  padding: 15px 20px;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  border-radius: 5px;
  color: #a94442;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Responsive Design */
@media (max-width: 600px) {
  .create-post-container {
    padding: 20px;
    margin: 20px;
  }

  .submit-button {
    width: 100%;
  }
}
</style>
