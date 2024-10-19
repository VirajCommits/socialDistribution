<template>
  <div>
    <h2>Your Posts</h2>
    <div v-if="loading">Loading posts...</div>
    <div v-else-if="filteredPosts.length === 0">
      <p>No posts found.</p>
    </div>
    <div v-else>
      <ul>
        <li
          v-for="post in filteredPosts"
          :key="post.id"
          @click="selectPost(post)"
        >
          <h3>{{ post.title }}</h3>
          <p>{{ post.description }}</p>
          <p><strong>Visibility:</strong> {{ post.visibility }}</p>

          <button @click.stop="editPost(post)">Edit</button>
          <button @click.stop="setPostInvisible(post)">Delete Post</button>
        </li>
      </ul>
    </div>

    <!-- Edit form for selected post -->
    <div v-if="editingPost">
      <h3>Edit Post</h3>
      <form @submit.prevent="savePost">
        <div>
          <label for="title">Title:</label>
          <input v-model="editingPost.title" type="text" id="title" required />
        </div>
        <div>
          <label for="description">Description:</label>
          <input
            v-model="editingPost.description"
            type="text"
            id="description"
          />
        </div>
        <div>
          <label for="visibility">Visibility:</label>
          <select v-model="editingPost.visibility" id="visibility">
            <option value="PUBLIC">Public</option>
            <option value="FRIENDS">Friends</option>
            <option value="PRIVATE">Private</option>
          </select>
        </div>
        <button type="submit">Save Changes</button>
        <button type="button" @click="cancelEdit">Cancel</button>
      </form>
    </div>

    <div v-if="selectedPost && !editingPost">
      <h3>Selected Post Details</h3>
      <p><strong>Title:</strong> {{ selectedPost.title }}</p>
      <p><strong>Description:</strong> {{ selectedPost.description }}</p>
      <p><strong>Content:</strong> {{ selectedPost.content }}</p>
      <p><strong>Content Type:</strong> {{ selectedPost.contentType }}</p>
      <p><strong>Visibility:</strong> {{ selectedPost.visibility }}</p>
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
      editingPost: null, // Store the post being edited
      loading: true,
    };
  },
  computed: {
    filteredPosts() {
      return this.posts.filter((post) => post.visibility === "PUBLIC");
    },
  },
  mounted() {
    this.fetchPosts();
  },
  methods: {
    async fetchPosts() {
      try {
        const apiUrl = `http://localhost:8000/project/service/api/authors/${encodeURIComponent(
          this.authorId
        )}/posts/all/`;

        const response = await axios.get(apiUrl);
        this.posts = response.data.results.items;
        this.loading = false;
      } catch (error) {
        console.error("Error fetching posts:", error.response || error);
        alert("An error occurred while fetching posts.");
        this.loading = false;
      }
    },

    editPost(post) {
      this.editingPost = { ...post }; // Create a copy of the post to edit
    },

    // Save the edited post
    async savePost() {
      console.log("saving post ... ", this.editingPost);
      const authorId = this.editingPost.author.id; // Assuming the author is an object with an id
      const postId = this.editingPost.id;

      console.log(authorId, " ---- ", postId);

      const updateUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/${postId}`;

      try {
        const response = await axios.put(updateUrl, this.editingPost, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        // Update the posts array with the edited post
        this.posts = this.posts.map((p) =>
          p.id === this.editingPost.id ? { ...response.data } : p
        );
        alert("Post updated successfully.");
        this.editingPost = null; // Clear the editing state
      } catch (error) {
        console.error("Error updating post:", error.response || error);
        alert("An error occurred while updating the post.");
      }
    },

    // Cancel the edit
    cancelEdit() {
      this.editingPost = null; // Clear the editing state
    },

    async setPostInvisible(post) {
      let authorId = post.author.id;
      authorId = encodeURIComponent(authorId);
      const postId = encodeURIComponent(post.id);

      const updateUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/${postId}`;

      if (
        confirm(
          `Are you sure you want to make the post titled "${post.title}" invisible?`
        )
      ) {
        try {
          // Patch the post to set visibility to 'INVISIBLE'
          const updatedPost = { visibility: "INVISIBLE" };

          const response = await axios.put(updateUrl, updatedPost, {
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
          alert("An error occurred while updating the post visibility.");
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
ul {
  list-style-type: none;
  padding: 0;
}

li {
  cursor: pointer;
  padding: 10px;
  border: 1px solid #ccc;
  margin: 5px 0;
  transition: background-color 0.3s ease;
}

li:hover {
  background-color: #f0f0f0;
}
</style>
