<template>
  <div>
    <h1>Stream/Author-feed Page</h1>

    <!-- Buttons Container -->
    <div class="buttons-container">
      <button class="logout-button" @click="logoutNode">Logout</button>
      <button class="profile-button" @click="goToProfile">Profile</button>
      <button class="follow-requests-button" @click="toggleFollowRequests">Follow Requests</button>
      <button class="explore-authors-button" @click="goToExploreAuthors">Explore Authors</button>
    </div>

    <!-- Follow Requests Section (Shown when followRequestsVisible is true) -->
    <div v-if="followRequestsVisible" class="follow-requests-section">
      <h2>Follow Requests</h2>
      <div v-if="followRequests.length">
        <div v-for="request in followRequests" :key="request.uuid" class="follow-request-item">
          <span>{{ request.actor.displayName }}</span>
          <button @click="acceptFollowRequest(request.actor.uuid)">Accept</button>
          <button @click="declineFollowRequest(request.actor.uuid)">Decline</button>
        </div>
      </div>
      <div v-else>
        <p>No follow requests</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'; 

export default {
  name: 'StreamPage',
  data() {
    return {
      followRequestsVisible: false, // Toggle follow requests section
      followRequests: [], // List of follow requests
    };
  },
  methods: {
    // Navigate to Profile
    goToProfile() {
      this.$router.push('/profile');
    },
    // Navigate to Explore Authors
    goToExploreAuthors() {
      this.$router.push('/explore');
    },
    // Logout function
    logoutNode() {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('uuid');
      this.$router.push('/login');
    },
    // Toggle follow requests section
    toggleFollowRequests() {
      this.followRequestsVisible = !this.followRequestsVisible;
      if (this.followRequestsVisible) {
        this.fetchFollowRequests(); // Only fetch requests when the section is opened
      }
    },
    // Fetch follow requests
    fetchFollowRequests() {
      axios
        .get(`http://localhost:8000/project/service/api/authors/follow_requests/`, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then((response) => {
          this.followRequests = response.data;
        })
        .catch((error) => {
          console.error('Error fetching follow requests:', error);
        });
    },
    // Accept a follow request
    acceptFollowRequest(uuid) {
      axios
        .post(`http://localhost:8000/project/service/api/authors/${uuid}/accept_follow_request/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          console.log("Follow request accepted");
          this.fetchFollowRequests(); // Refresh follow requests after accepting
        })
        .catch((error) => {
          console.error('Error accepting follow request:', error);
        });
    },
    // Decline a follow request
    declineFollowRequest(uuid) {
      axios
        .post(`http://localhost:8000/project/service/api/authors/${uuid}/decline_follow_request/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          console.log("Follow request declined");
          this.fetchFollowRequests(); // Refresh follow requests after declining
        })
        .catch((error) => {
          console.error('Error declining follow request:', error);
        });
    },
  },
};
</script>

<style scoped>
h1 {
  color: #42b983;
  text-align: center;
}

.buttons-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.logout-button, .profile-button, .follow-requests-button, .explore-authors-button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin: 0 10px; /* Add space between buttons */
}

.profile-button:hover, .logout-button:hover, .follow-requests-button:hover, .explore-authors-button:hover {
  background-color: #2c8a6a;
}

.follow-requests-section {
  margin-top: 80px;
  text-align: center;
}

.follow-request-item {
  display: flex;
  justify-content: space-between;
  margin: 10px auto;
  width: 300px; /* Width to keep the item centrally aligned */
}

.follow-request-item button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  margin-left: 10px;
}

.follow-request-item button:hover {
  background-color: #2c8a6a;
}
</style>
