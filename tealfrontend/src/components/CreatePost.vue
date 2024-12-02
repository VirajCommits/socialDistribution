<template>
  <div class="create-post-container">
    <!-- Back Button -->
    <button class="back-button" @click="goBack">Back</button>

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
          <option value="FRIENDS">Friends Only</option>
          <option value="UNLISTED">Unlisted</option>
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
import Cookies from 'js-cookie';


export default {
  name: "CreatePost",
  data() {
    return {
      form: {
        title: "",
        description: "",
        contentType: "text/plain",
        content: "",
        image: null, // Holds the uploaded image file
        visibility: "PUBLIC",
      },
      isImageType: false, // Tracks if the selected content type is an image
      response: null,
      successMessage: "",
      errorMessage: "",
      user: null,
      authID: "",
    };
  },
  methods: {
    handleContentTypeChange() {
      this.isImageType = this.form.contentType.includes("image");
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        // Store the image file in form.image
        this.form.image = file;

        const reader = new FileReader();
        reader.onload = (e) => {
          // Convert image to base64 and store it in form.content for preview
          this.form.content = e.target.result;
        };
        reader.readAsDataURL(file); // Convert to base64 string for preview
      }
    },
    async createPost() {
      // Clear previous messages
      this.successMessage = "";
      this.errorMessage = "";

      try {
        // Retrieve user information
        this.user = JSON.parse(localStorage.getItem("user"));
        this.authID = this.user.id.split("/").pop();

        const authorId = this.authID;
        const apiUrl = `/authors/${authorId}/posts/`;

        // Create form data to handle both text and image uploads
        const formData = new FormData();
        formData.append("title", this.form.title);
        formData.append("description", this.form.description);
        formData.append("contentType", this.form.contentType);
        formData.append("visibility", this.form.visibility);

        if (this.isImageType && this.form.image) {
          formData.append("content", this.form.content);
          formData.append("image", this.form.image);
        } else {
          formData.append("content", this.form.content);
        }
        const csrfToken = Cookies.get("csrftoken"); // Get CSRF token from cookies
        // Create the post only once
        const response = await axios.post(apiUrl, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Token ${localStorage.getItem("token")}`,
            "X-CSRFToken": csrfToken,
          },
        });

        this.response = response.data;

        // Only send notifications to other authors' inboxes
        if (this.form.visibility !== "PRIVATE") {
          await this.sendPostToFollowers(this.response);
        }

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
        this.isImageType = false;

        // Redirect to posts list
        this.$router.push("/posts/all");
      } catch (error) {
        console.error("Error creating post:", error.response || error);
        this.errorMessage = "An error occurred while creating the post.";
      }
    },
    async sendPostToFollowers(postData) {
      try {
        const authorsResponse = await axios.get("/authors/", {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        const authors = authorsResponse.data;
        console.log("AUTHORS IN CREATE POST:" , authors , this.user.id)
        const currentAuthorId = this.user.id.split("/").pop();
        console.log("Current auth id:" , currentAuthorId)

        // Track which authors have received the notification
        const processedAuthors = new Set([currentAuthorId]); // Initialize with current author
        console.log(" >>>>>>>>>>>> " , processedAuthors , this.form.visibility)

        switch (this.form.visibility) {
          case "PUBLIC": {
            // Only send notifications to other authors' inboxes

            const followers = await this.getFollowers(currentAuthorId);
            console.log("Followers are:" , followers)
            for (const author of followers) {
              const authorId = author.id.split("/").pop(-1);
              
              if (
                authorId !== currentAuthorId &&
                !processedAuthors.has(authorId)
              ) {
                console.log("auth id:" , authorId)
                await this.sendNotificationToInbox(authorId, postData, author.host);
                processedAuthors.add(authorId);
              }
            }
            break;
          }
          case "FRIENDS": {
                const followers = await this.getFollowers(currentAuthorId);
                console.log("The processed authors:" , processedAuthors)
                for (const follower of followers) {
                    if (!processedAuthors.has(follower.uuid)) {
                        const mutualFollowers = await this.getFollowers(follower.uuid);
                        if (mutualFollowers.some(mf => mf.uuid === currentAuthorId)) {
                            await this.sendNotificationToInbox(follower.uuid, postData);
                            processedAuthors.add(follower.uuid);
                        }
                    }
                }
                break;
            }
            case "UNLISTED": {
                const myFollowers = await this.getFollowers(currentAuthorId);
                for (const follower of myFollowers) {
                    if (!processedAuthors.has(follower.uuid)) {
                        await this.sendNotificationToInbox(follower.uuid, postData);
                        processedAuthors.add(follower.uuid);
                    }
                }
                break;
            }
        }
      } catch (error) {
        console.error("Error distributing post:", error);
      }
    },
    async sendNotificationToInbox(authorId, postData, host) {
      try {
        console.log("This is the host:" , host)
        const inboxUrl = `${host}api/authors/${authorId}/inbox/`;
        console.log("POST DATA:" , postData , inboxUrl)

        const payload = {
          type: "post",
          title: this.form.title,
          id: postData.id,
          page: postData.page,
          description: this.form.description,
          contentType: this.form.contentType,
          content: this.form.content,
          author: {
            type: "author",
            id: this.user.id,
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage,
          },
          author_id: this.authID,
          published: new Date().toISOString(),
          visibility: this.form.visibility,
        };

        let targethost = authorId.split('/authors/')[0];
        if (targethost.includes("/api")) { targethost = targethost.split("/api")[0]; }
        const response = await axios.get('/connected-nodes/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        const connectedNodes = response;
        const connected_nodes = response.data;
        console.log("CONNECTED NODES:" , connectedNodes)
        console.log("CONNECTED NODES DATA:" , connected_nodes)
        console.log("TARGET HOST:" , targethost)

        console.log("HOST:" , host)
        const targetNode = connected_nodes.find(node => node.url+'/' === host);
        console.log("TARGET NODE:" , targetNode)
        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);
        console.log(payload)
        const csrfToken = Cookies.get("csrftoken"); 
        await axios.post(inboxUrl, payload, {
          headers: {
            Authorization: `Basic ${credentials}`,
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        });
      } catch (error) {
        console.error(`Error sending notification to author ${authorId}:`, error);
        throw error;
      }
    },
    async getFollowers(authorId) {
    try {
        const response = await axios.get(`/authors/${authorId}/followers/`);
        console.log("Followers response:" , response.data)
        return response.data;
    } catch (error) {
        console.error(`Error getting followers for author ${authorId}:`, error);
        return [];
    }
},
    goBack() {
      this.$router.push("/posts/all");
    },
  },
};
</script>

<style scoped>
/* Back Button Styling */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 50%;
  padding: 12px 18px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, transform 0.2s ease,
    box-shadow 0.3s ease;
}

.back-button:hover {
  background-color: #3b30d5;
  transform: scale(1.05);
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
}

.back-button:active {
  transform: scale(1);
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.2);
}

/* Container Styling */
.create-post-container {
  position: relative; /* Ensure positioning context for the back button */
  max-width: 700px;
  margin: 40px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

  /* Enable scrolling */
  max-height: 80vh;
  overflow-y: auto;
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