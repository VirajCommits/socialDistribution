<!-- <template>
  <div>
    <h1>Your Feed</h1>
    <button @click="logout">Logout</button>
    <div v-if="posts.length">
      <div v-for="post in posts" :key="post.id">
        <h2>{{ post.title }}</h2>
        <p>
          By
          <router-link :to="{ name: 'AuthorProfile', params: { uuid: post.author.uuid } }">
            {{ post.author.displayName }}
          </router-link>
          on {{ post.published }}
        </p>
        <div v-html="post.content"></div>
        <hr />
      </div>
    </div>
    <div v-else>
      <p>No posts to display.</p>
    </div>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  name: 'UserFeed', // Changed to multi-word name
  data() {
    return {
      posts: [],
    };
  },
  created() {
    this.fetchFeed();
  },
  methods: {
    fetchFeed() {
      axios
        .get('/posts/', {
          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
        })
        .then((response) => {
          this.posts = response.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push({ name: 'UserLogin' });
    },
  },
};
</script> -->

<!-- tealFrontend/src/views/Feed.vue -->

<template>
  <div>
    <h1>Your Feed</h1>
    <div v-if="posts.length">
      <div v-for="post in posts" :key="post.id">
        <h2>{{ post.title }}</h2>
        <p>
          By
          <router-link :to="{ name: 'AuthorProfile', params: { uuid: post.author.uuid } }">
            {{ post.author.displayName }}
          </router-link>
          on {{ post.published }}
        </p>
        <div v-html="post.content"></div>
        <hr />
      </div>
    </div>
    <div v-else>
      <p>No posts to display.</p>
    </div>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  name: 'UserFeed',
  data() {
    return {
      posts: [],
    };
  },
  created() {
    this.fetchFeed();
  },
  methods: {
    fetchFeed() {
      axios
        .get('/feed/')
        .then((response) => {
          this.posts = response.data.results;
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
};
</script>
