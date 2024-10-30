<template>
  <div class="explore-authors-page">
    <h1>Explore Authors</h1>
    <button class="back-button" @click="goBack">Back</button>

    <!-- List of Authors -->
    <div v-if="authors.length" class="authors-list">
      <div v-for="author in authors" :key="author.id" class="author-item">
        <span>{{ author.displayName }}</span>
        <button v-if="author.is_following" class="follow-button following-button">
          Following
        </button>
        <button v-else class="follow-button" @click="sendFollowRequest(author.id)">
          Send Follow Request
        </button>
      </div>
    </div>
    <div v-else class="no-authors">
      <p>Nobody Else here yet.</p>
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
      followRequestCount: 0,
    };
  },
  created() {
    this.fetchAuthors();
  },
  methods: {
    fetchAuthors() {
      axios
        .get('http://localhost:8000/project/service/api/authors/', {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then((response) => {
          this.authors = response.data;
        })
        .catch((error) => {
          console.error('Error fetching authors:', error);
        });
    },
    goBack() {
      this.$router.push('/stream');
    },
    sendFollowRequest(authorId) {
      const authorUUID = authorId.split('/').pop();
      const token = localStorage.getItem('token');
      
      axios
        .post(
          `http://localhost:8000/project/service/api/authors/${authorUUID}/send_follow_request/`,
          {}, // empty body
          {
            headers: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        .then(() => {
          alert('Follow request sent successfully.');
          this.fetchAuthors();
        })
        .catch((error) => {
          console.error('Error sending follow request:', error);
          alert(error.response?.data?.detail || 'Error sending follow request');
        });
    },
  },
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
  background-color: #777;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 15px;
  cursor: default;
  font-weight: bold;
}

.no-authors {
  margin-top: 20px;
  font-size: 18px;
  color: #666;
}
</style>
