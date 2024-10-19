<template>
  <div>
    <h2>Create a New Post</h2>
    <form @submit.prevent="createPost">
      <div>
        <label>Title:</label>
        <input v-model="form.title" required />
      </div>
      <div>
        <label>Description:</label>
        <input v-model="form.description" />
      </div>
      <div>
        <label>Content Type:</label>
        <select v-model="form.contentType">
          <option value="text/plain">Plain Text</option>
          <option value="text/markdown">Markdown</option>
          <option value="image/png;base64">PNG Image (Base64)</option>
          <option value="image/jpeg;base64">JPEG Image (Base64)</option>
        </select>
      </div>
      <div>
        <label>Content:</label>
        <textarea v-model="form.content"></textarea>
      </div>
      <div>
        <label>Visibility:</label>
        <select v-model="form.visibility">
          <option value="PUBLIC">Public</option>
          <option value="FRIENDS">Friends</option>
          <option value="PRIVATE">Private</option>
        </select>
      </div>
      <button type="submit">Create Post</button>
    </form>

    <div v-if="response">
      <h3>Post Created Successfully!</h3>
      <pre>{{ response }}</pre>
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
        visibility: "PUBLIC",
      },
      response: null,
    };
  },
  methods: {
    async createPost() {
      try {
        // TODO - replace authorId with actual authorID
        const authorId = "http://www.github.com"; // Replace with the actual author ID
        const apiUrl = `http://localhost:8000/project/service/api/authors/${encodeURIComponent(
          authorId
        )}/posts/`;

        const response = await axios.post(apiUrl, this.form, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        this.response = response.data;
        console.log(" -- +", this.reponse);
      } catch (error) {
        console.error("Error creating post:", error.response || error);
        alert("An error occurred while creating the post.");
      }
    },
  },
};
</script>

<style scoped>
/* Add your styles here */
</style>
