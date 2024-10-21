<template>
  <div>
    <button class="back-button" @click="backToStream">Back to Stream</button>
    <h1>Profile Page</h1>
    <h2>User Details</h2>
    <button @click="makePost">Make Post</button>
    <button @click="showPost">See your posts!</button>
    <div v-if="user">
      <p><strong>ID:</strong> {{ user.id }}</p>
      <p><strong>Host:</strong> {{ user.host }}</p>
      <p><strong>Display Name:</strong> {{ user.displayName }}</p>
      <p>
        <strong>GitHub:</strong> <a :href="user.github">{{ user.github }}</a>
      </p>
      <p>
        <strong>Profile Image:</strong>
        <img :src="user.profileImage" alt="Profile Image" width="100" />
      </p>
      <p>
        <strong>Page:</strong> <a :href="user.page">{{ user.page }}</a>
      </p>
      <p><strong>Username:</strong> {{ user.username }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
    </div>
    <div v-else>
      <p>Loading user details...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfilePage",
  data() {
    return {
      user: null,
    };
  },
  mounted() {
    this.user = JSON.parse(localStorage.getItem("user"));
    console.log(this.user);
  },
  methods: {
    backToStream() {
      this.$router.push("/stream");
    },
    makePost() {
      this.$router.push("/addPost");
    },

    showPost() {
      this.$router.push("/posts/all");
    },
  },
};
</script>

<style scoped>
h1 {
  color: #42b983;
}
.back-button {
  position: absolute;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 50%;
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.back-button {
  top: 20px;
  left: 20px;
}
</style>
