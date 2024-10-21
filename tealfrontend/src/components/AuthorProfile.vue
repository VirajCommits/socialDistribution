<template>
  <div v-if="author">
    <h2>{{ author.displayName }}</h2>
    <p><strong>Host:</strong> {{ author.host }}</p>
    <p>
      <strong>GitHub:</strong>
      <a :href="author.github" target="_blank">{{ author.github }}</a>
    </p>

    <!-- Show "Send Follow Request" only if viewing someone else's profile -->
    <div v-if="!isOwnProfile && !isFollowing && !hasSentRequest">
      <button @click="sendFollowRequest">Send Follow Request</button>
    </div>

    <!-- Show follow request status if already sent -->
    <div v-if="!isOwnProfile && hasSentRequest">
      <p>Follow request sent.</p>
    </div>

    <!-- Show when already following someone -->
    <div v-if="!isOwnProfile && isFollowing">
      <p>You are following this author.</p>
    </div>

    <!-- Show "View Follow Requests" only if it's your own profile -->
    <div v-if="isOwnProfile">
      <button @click="goToFollowRequests">View Follow Requests</button>
    </div>

    <!-- Fixed "Logout" button -->
    <button class="logout-button" @click="logout">Logout</button>
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
      isOwnProfile: false,
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
          this.checkIfOwnProfile();
        })
        .catch((error) => {
          console.error('Error fetching author:', error);
          this.loading = false;
          this.error = true;
        });
    },
    checkFollowing() {
      axios
        .get(`/authors/${localStorage.getItem('uuid')}/`)
        .then((response) => {
          const following = response.data.following;
          this.isFollowing = following.includes(this.author.id);
          this.checkFollowRequest();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    checkFollowRequest() {
      axios
        .get(`/authors/${this.uuid}/follow_requests/`)
        .then((response) => {
          const requests = response.data;
          this.hasSentRequest = requests.some(
            (req) => req.actor.id === this.author.id
          );
        })
        .catch((error) => {
          console.error(error);
        });
    },
    checkIfOwnProfile() {
      const loggedInUUID = localStorage.getItem('uuid');
      this.isOwnProfile = this.uuid === loggedInUUID;
    },
    sendFollowRequest() {
      axios
        .post(`/authors/${this.uuid}/send_follow_request/`)
        .then(() => {
          this.hasSentRequest = true;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    goToFollowRequests() {
      this.$router.push({ path: `/author/${this.uuid}/follow_requests` });
    },
    logout() {
      // Remove the token and user info from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('uuid');
      // Redirect to login page
      this.$router.push({ name: 'Login' });
    },
  },
};
</script>

<style scoped>
.logout-button {
  position: fixed;
  top: 10px;
  right: 10px;
}
</style>
