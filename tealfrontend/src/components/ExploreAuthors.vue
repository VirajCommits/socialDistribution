<template>
  <div class="explore-authors-page">
    <h1>Explore Authors</h1>
    <button class="back-button" @click="goBack">Back</button>

    <!-- List of Authors -->
    <div v-if="authors.length" class="authors-list">
      <div v-for="author in authors" :key="author.id" class="author-item">
        <span>{{ author.displayName }}</span>
        <button 
          v-if="isFollowing(author)"
          @click="handleUnfollow(author)"
          class="following-button"
        >
          Following
        </button>
        <button 
          v-else-if="hasPendingRequest(author)"
          @click="handlePendingRequest(author)"
          class="pending-button"
        >
          Request Pending
        </button>
        <button 
          v-else
          @click="sendFollowRequest(author.id)"
          class="follow-button"
        >
          Send Follow Request
        </button>
      </div>
    </div>
    <div v-else class="no-authors">
      <p>Nobody Else here yet.</p>
    </div>

    <!-- Add this modal at the bottom of the template, before closing div -->
    <div v-if="showUnfollowModal" class="modal">
      <div class="modal-content">
        <h3>Confirm Unfollow</h3>
        <p>Are you sure you want to unfollow {{ selectedAuthor?.displayName }}?</p>
        <div class="modal-buttons">
          <button @click="confirmUnfollow" class="unfollow-button">Yes</button>
          <button @click="showUnfollowModal = false" class="cancel-button">No</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ExploreAuthors',
  data() {
    return {
      authors: [],
      pendingRequests: [],
      following: [],
      token: localStorage.getItem('token'),
      showUnfollowModal: false,
      selectedAuthor: null,
    };
  },
  created() {
    // Check if user is authenticated
    if (!this.token) {
      this.$router.push('/login');
      return;
    }
  },
  mounted() {
    if (this.token) {
      this.fetchAuthors();
      this.startPolling();
      this.setupWebSocket();
    }
  },
  methods: {
    fetchAuthors() {
      if (!this.token) return;
      
      axios
        .get('http://localhost:8000/project/service/api/authors/', {
          headers: { 
            'Authorization': `Token ${this.token}`,
            'Content-Type': 'application/json'
          },
        })
        .then((response) => {
          this.authors = response.data;
          this.fetchPendingRequests();
        })
        .catch((error) => {
          console.error('Error fetching authors:', error);
          if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            this.$router.push('/login');
          }
        });
    },
    goBack() {
      this.$router.push('/stream');
    },
    async fetchPendingRequests() {
      if (!this.token) return;

      try {
        const response = await axios.get(
          'http://localhost:8000/project/service/api/authors/pending_requests/',
          {
            headers: { 
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        this.pendingRequests = response.data.map(req => req.object.id);
      } catch (error) {
        console.error('Error fetching pending requests:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          this.$router.push('/login');
        }
      }
    },
    async sendFollowRequest(authorId) {
      const authorUUID = authorId.split('/').pop();
      try {
        await axios.post(
          `http://localhost:8000/project/service/api/authors/${authorUUID}/send_follow_request/`,
          {},
          {
            headers: { Authorization: `Token ${localStorage.getItem('token')}` }
          }
        );
        this.pendingRequests.push(authorId);
        alert('Follow request sent successfully.');
      } catch (error) {
        console.error('Error sending follow request:', error);
        alert(error.response?.data?.detail || 'Error sending follow request');
      }
    },
    async handlePendingRequest(author) {
      const confirmed = confirm('Do you want to remove your follow request?');
      if (confirmed) {
        const authorUUID = author.id.split('/').pop();
        try {
          await axios.delete(
            `http://localhost:8000/project/service/api/authors/${authorUUID}/remove_follow_request/`,
            {
              headers: { Authorization: `Token ${localStorage.getItem('token')}` }
            }
          );
          this.pendingRequests = this.pendingRequests.filter(id => id !== author.id);
          alert('Follow request removed successfully.');
          this.fetchAuthors();
        } catch (error) {
          console.error('Error removing follow request:', error);
          alert(error.response?.data?.detail || 'Error removing follow request');
        }
      }
    },
    isFollowing(author) {
      const currentUserUUID = localStorage.getItem('uuid');
      return author.followers?.some(follower => 
        typeof follower === 'string' 
          ? follower.includes(currentUserUUID)
          : follower.uuid === currentUserUUID
      );
    },
    hasPendingRequest(author) {
      return this.pendingRequests.includes(author.id);
    },
    startPolling() {
      this.pollInterval = setInterval(() => {
        this.fetchAuthors();
      }, 5000); // Poll every 5 seconds
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
      }
    },
    setupWebSocket() {
      const uuid = localStorage.getItem('uuid');
      if (!uuid) return;

      const ws = new WebSocket(`ws://localhost:8000/ws/notifications/${uuid}/`);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'follow_request_notification') {
          // Refresh the data when a follow request is updated
          this.fetchAuthors();
          this.fetchPendingRequests();
          
          // Show notification to user
          if (data.message) {
            alert(data.message);
          }
        }
      };

      ws.onclose = () => {
        // Attempt to reconnect after a delay
        setTimeout(() => this.setupWebSocket(), 1000);
      };

      this.ws = ws;
    },
    beforeDestroy() {
      if (this.ws) {
        this.ws.close();
      }
      this.stopPolling();
    },
    handleUnfollow(author) {
      this.selectedAuthor = author;
      this.showUnfollowModal = true;
    },
    async confirmUnfollow() {
      if (!this.selectedAuthor) return;
      
      const authorUUID = this.selectedAuthor.id.split('/').pop();
      try {
        await axios.delete(
          `http://localhost:8000/project/service/api/authors/${authorUUID}/unfollow/`,
          {
            headers: { Authorization: `Token ${this.token}` }
          }
        );
        
        // Close modal and refresh authors list
        this.showUnfollowModal = false;
        this.selectedAuthor = null;
        this.fetchAuthors();
        alert('Successfully unfollowed author.');
      } catch (error) {
        console.error('Error unfollowing author:', error);
        alert(error.response?.data?.detail || 'Error unfollowing author');
      }
    },
  },
  beforeUnmount() {
    this.stopPolling(); // Clean up when component unmounts
  }
};
</script>


<style scoped>
.explore-authors-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
}

h1 {
  color: #42b983;
  margin-bottom: 20px;
}

.back-button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 50%;
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 20px;
}

.back-button:hover {
  background-color: #2c8a6a;
}

.authors-list {
  width: 60%;
  margin-top: 20px;
  border: 2px solid #42b983;
  border-radius: 10px;
  padding: 10px;
  background-color: #f9f9f9;
}

.author-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

.author-item:last-child {
  border-bottom: none;
}

.follow-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.follow-button:hover {
  background-color: #2c8a6a;
}

.following-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.following-button:hover {
  background-color: #ff4444;
}

.pending-button {
  background-color: #ffa500;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.no-authors {
  margin-top: 20px;
  font-size: 18px;
  color: #666;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  text-align: center;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.unfollow-button {
  background-color: #ff4444;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.unfollow-button:hover {
  background-color: #cc0000;
}

.cancel-button {
  background-color: #666;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: bold;
}

.cancel-button:hover {
  background-color: #444;
}
</style>
