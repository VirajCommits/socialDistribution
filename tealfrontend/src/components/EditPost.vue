<!-- src/components/EditPost.vue -->
<template>
  <div>
    <h2>Edit Post</h2>
    <div v-if="loading">Loading post...</div>
    <div v-else-if="!post">
      <p>Post not found.</p>
      <router-link to="/posts/all">Go Back</router-link>
    </div>
    <div v-else>
      <form @submit.prevent="savePost">
        <div>
          <label for="title">Title:</label>
          <input v-model="post.title" type="text" id="title" required />
        </div>
        <div>
          <label for="description">Description:</label>
          <input v-model="post.description" type="text" id="description" />
        </div>
        <div>
          <label for="visibility">Visibility:</label>
          <select v-model="post.visibility" id="visibility">
            <option value="PUBLIC">Public</option>
            <option value="FRIENDS">Friends</option>
            <option value="PRIVATE">Private</option>
            <option value="INVISIBLE">Invisible</option>
          </select>
        </div>
        <button type="submit">Save Changes</button>
        <router-link to="/posts/all">Cancel</router-link>
      </form>

      <!-- Display error messages -->
      <div v-if="errorMessage" class="error">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

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
      post: null,
      loading: true,
      errorMessage: "",
    };
  },
  mounted() {
    this.fetchPost();
  },
  methods: {
    async fetchPost() {
      try {
        this.user = JSON.parse(localStorage.getItem("user"));
        this.authID = this.user.id.split("/").pop();
        const authorId = this.authID;
        const apiUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/${encodeURIComponent(this.id)}`;

        const response = await axios.get(apiUrl);
        this.post = response.data;
        this.loading = false;
      } catch (error) {
        console.error("Error fetching post:", error.response || error);
        this.errorMessage = "An error occurred while fetching the post.";
        this.loading = false;
      }
    },

    async savePost() {
      try {
        console.log("Inside save post");
        this.user = JSON.parse(localStorage.getItem("user"));
        this.authID = this.user.id.split("/").pop();
        const authorId = this.authID;
        const apiUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/${encodeURIComponent(this.id)}`;

        await axios.put(apiUrl, this.post, {
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
form {
  max-width: 600px;
  margin: 0 auto;
}

form div {
  margin-bottom: 15px;
}

label {
  display: inline-block;
  width: 100px;
}

input,
select {
  width: calc(100% - 110px);
  padding: 5px;
}

button {
  padding: 5px 10px;
  background-color: green;
  color: white;
  border: none;
  cursor: pointer;
  margin-right: 10px;
}

button:hover {
  background-color: darkgreen;
}

router-link {
  padding: 5px 10px;
  background-color: red;
  color: white;
  text-decoration: none;
  border-radius: 3px;
}

router-link:hover {
  background-color: darkred;
}

.error {
  color: red;
  margin: 10px 0;
}
</style>
