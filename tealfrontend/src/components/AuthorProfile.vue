<template>
  <div v-if="author">
    <h2>{{ author.displayName }}</h2>
    <p><strong>Host:</strong> {{ author.host }}</p>
    <p>
      <strong>GitHub:</strong>
      <a :href="author.github" target="_blank">{{ author.github }}</a>
    </p>
    <div v-if="hasSentRequest">
      <p>Follow request sent.</p>
    </div>
    <div v-else-if="isFollowing">
      <p>You are following this author.</p>
    </div>
    <div v-else>
      <button @click="sendFollowRequest">Send Follow Request</button>
    </div>

    <!-- Follow Requests button -->
    <div>
      <button @click="goToFollowRequests">View Follow Requests</button>
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
      author: null,
      isFollowing: false,
      hasSentRequest: false,
      loading: true,
      error: false,
    };
  },
  created() {
    this.fetchAuthor();
  },
  methods: {
    fetchAuthor() {
      this.loading = true;
      axios
        .get(`/authors/${this.uuid}/`)
        .then((response) => {
          this.author = response.data;
          this.loading = false;
          this.checkFollowing();
        })
        .catch((error) => {
          console.error("Error fetching author:", error);
          this.loading = false;
          this.error = true;
        });
    },
    checkFollowing() {
      axios
        .get(`/authors/${localStorage.getItem("uuid")}/`)
        .then((response) => {
          const following = response.data.following;
          // Ensure the author object is fetched before checking
          this.isFollowing = following.includes(this.author.id); 
          this.checkFollowRequest(); // Fetch follow requests if user is following
        })
        .catch((error) => {
          console.error(error);
        });
    },
    checkFollowRequest() {
      // Check if the current user has sent a follow request to this author
      axios
        .get(`/authors/${this.uuid}/follow_requests/`)
        .then((response) => {
          const requests = response.data;
          // Check if there's a follow request from this author to the current user
          this.hasSentRequest = requests.some(
            (req) => req.actor.id === this.author.id
          );
        })
        .catch((error) => {
          console.error(error);
        });
    },
    sendFollowRequest() {
      // Send a follow request to this author
      axios
        .post(`/authors/${this.uuid}/send_follow_request/`)
        .then(() => {
          this.hasSentRequest = true; // Update UI after sending request
        })
        .catch((error) => {
          console.error(error);
        });
    },
    goToFollowRequests() {
      // Navigate to the follow requests page for this author
      this.$router.push({ path: `/author/${this.uuid}/follow_requests` });
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
</style>
