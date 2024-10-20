<template>
  <div v-if="author">
    <h2>{{ author.displayName }}</h2>
    <p><strong>Host:</strong> {{ author.host }}</p>
    <p>
      <strong>GitHub:</strong>
      <a :href="author.github" target="_blank">{{ author.github }}</a>
    </p>
    <div v-if="isFollowing">
      <button @click="unfollowAuthor">Unfollow</button>
    </div>
    <div v-else>
      <button @click="followAuthor">Follow</button>
    </div>
    <button @click="$router.go(-1)">Back</button>
  </div>
  <div v-else-if="loading">
    <p>Loading author data...</p>
  </div>
  <div v-else>
    <p>Error loading author data.</p>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  props: ['uuid'],
  data() {
    return {
      author: null,    // The author data
      isFollowing: false,   // Whether the current user is following this author
      loading: true,    // Loading state to show loading message
      error: false,     // Error state to handle API failures
    };
  },
  created() {
    console.log("UUID passed to component:", this.uuid);
    this.fetchAuthor();
  },
  methods: {
    fetchAuthor() {
      this.loading = true;   // Set loading to true while fetching the author
      axios
        .get(`/authors/${this.uuid}/`, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then((response) => {
          this.author = response.data;  // Set the author data
          this.loading = false;         // Set loading to false once data is fetched
          this.checkFollowing();        // Check if current user is following the author
        })
        .catch((error) => {
          console.error("Error fetching author:", error);
          this.loading = false;
          this.error = true;            // Set error state if API call fails
        });
    },
    checkFollowing() {
      axios
        .get('/authors/me/', {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then((response) => {
          const following = response.data.following;
          if (this.author) {
            this.isFollowing = following.includes(this.author.uuid);
          }
        })
        .catch((error) => {
          console.error("Error checking following status:", error);
        });
    },
    followAuthor() {
      axios
        .post(`/authors/${this.uuid}/follow/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          this.isFollowing = true;   // Update the follow state
        })
        .catch((error) => {
          console.error("Error following author:", error);
        });
    },
    unfollowAuthor() {
      axios
        .post(`/authors/${this.uuid}/unfollow/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          this.isFollowing = false;  // Update the follow state
        })
        .catch((error) => {
          console.error("Error unfollowing author:", error);
        });
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
</style>
