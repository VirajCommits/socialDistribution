<template>
  <div>
    <h1>Stream/Author-feed Page</h1>

    <!-- Buttons Container -->
    <div class="buttons-container">
      <button class="logout-button" @click="logoutNode">Logout</button>
      <button class="profile-button" @click="goToProfile">Profile</button>
      <button class="follow-requests-button" @click="toggleFollowRequests">
        Follow Requests
        <span v-if="followRequestCount > 0" class="notification-badge">{{ followRequestCount }}</span>
      </button>
      <button class="explore-authors-button" @click="goToExploreAuthors">Explore Authors</button>
    </div>

    <!-- Follow Requests Section -->
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
      followRequestsVisible: false,
      followRequests: [],
      followRequestCount: 0,
      socket: null,
    };
  },
  mounted() {
    if (localStorage.getItem('token')) {
      this.initializeWebSocket();
      this.fetchInitialCount();
    } else {
      console.error('No authentication token found');
      this.$router.push('/login');
    }
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  },
  methods: {
    initializeWebSocket() {
      const uuid = localStorage.getItem('uuid');
      const token = localStorage.getItem('token');
      
      if (!uuid || !token) {
        console.error('Missing authentication information');
        return;
      }

      try {
        this.socket = new WebSocket(`ws://localhost:8000/ws/notifications/${uuid}/`);
        
        this.socket.onopen = () => {
          console.log('WebSocket connected successfully');
          // Send authentication message
          this.socket.send(JSON.stringify({
            type: 'authenticate',
            token: token
          }));
        };

        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === 'follow_request') {
            this.followRequestCount = data.count;
            if (this.followRequestsVisible) {
              this.fetchFollowRequests();
            }
          }
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason);
          // Only attempt to reconnect if the component is still mounted
          setTimeout(() => {
            if (this.$el && document.body.contains(this.$el)) {
              this.initializeWebSocket();
            }
          }, 5000);
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Error initializing WebSocket:', error);
      }
    },
    async fetchInitialCount() {
      try {
        const response = await axios.get(
          'http://localhost:8000/project/service/api/authors/follow_requests/',
          {
            headers: { Authorization: `Token ${localStorage.getItem('token')}` },
          }
        );
        this.followRequestCount = response.data.length;
      } catch (error) {
        console.error('Error fetching initial count:', error);
      }
    },
    goToProfile() {
      this.$router.push('/profile');
    },
    goToExploreAuthors() {
      this.$router.push('/explore');
    },
    logoutNode() {
      if (this.socket) {
        this.socket.close();
      }
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('uuid');
      this.$router.push('/login');
    },
    toggleFollowRequests() {
      this.followRequestsVisible = !this.followRequestsVisible;
      if (this.followRequestsVisible) {
        this.fetchFollowRequests();
        this.followRequestCount = 0;
      }
    },
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
    acceptFollowRequest(uuid) {
      axios
        .post(`http://localhost:8000/project/service/api/authors/${uuid}/accept_follow_request/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          this.fetchFollowRequests();
          this.followRequestCount = Math.max(0, this.followRequestCount - 1);
        })
        .catch((error) => {
          console.error('Error accepting follow request:', error);
        });
    },
    declineFollowRequest(uuid) {
      axios
        .post(`http://localhost:8000/project/service/api/authors/${uuid}/decline_follow_request/`, null, {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then(() => {
          this.fetchFollowRequests();
          this.followRequestCount = Math.max(0, this.followRequestCount - 1);
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
  position: relative; /* Position relative for badge */
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

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #ff4444;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  min-width: 18px;
  text-align: center;
}
</style>
