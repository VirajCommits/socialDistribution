<template>
    <div class="explore-authors-page">
      <h1>Explore Authors</h1>
      <button class="back-button" @click="goBack">Back</button>
  
      <!-- List of Authors -->
      <div v-if="authors.length" class="authors-list">
        <div v-for="author in authors" :key="author.id" class="author-item">
          <span>{{ author.displayName }}</span>
          <button class="follow-button" @click="sendFollowRequest(author.id)">Send Follow Request</button>
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
      };
    },
    created() {
      this.fetchAuthors();
    },
    methods: {
      // Fetch all authors except the current user
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
      // Navigate back to the stream page
      goBack() {
        this.$router.push('/stream');
      },
      // Send follow request to a specific author
      sendFollowRequest(authorId) {
        const authorUUID = authorId.split('/').pop();
        axios
          .post(`http://localhost:8000/project/service/api/authors/${authorUUID}/send_follow_request/`, null, {
            headers: { Authorization: `Token ${localStorage.getItem('token')}` },
          })
          .then(() => {
            alert('Follow request sent successfully.');
          })
          .catch((error) => {
            console.error('Error sending follow request:', error);
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
  }
  
  .author-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid #ccc;
  }
  
  .follow-button {
    background-color: #42b983;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .follow-button:hover {
    background-color: #2c8a6a;
  }
  
  .no-authors {
    margin-top: 20px;
    font-size: 18px;
    color: #666;
  }
  </style>
  