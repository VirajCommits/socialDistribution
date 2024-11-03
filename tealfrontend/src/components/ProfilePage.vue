<template>
  <div>
    <button class="back-button" @click="backToStream">Back to Stream</button>
    <h1>Profile Page</h1>
    <h2>User Details</h2>
    <button @click="makePost">Create Post</button>
    <button @click="showPost">See your posts!</button>
    <div v-if="user" class="user-details">
      <p><strong>ID:</strong> {{ user.id }}</p>
      <p><strong>Host:</strong> {{ user.host }}</p>
      <p><strong>Display Name:</strong> {{ user.displayName }}</p>
      <p>
        <strong>GitHub:</strong>
        <a :href="user.github" target="_blank">{{ user.github }}</a>
      </p>
      <p>
        {{ console.log(user) }}
        <strong>Profile Image:</strong>
        <img :src="user.profileImage" />
      </p>
      <p>
        <strong>Page:</strong>
        <a :href="user.page" target="_blank">{{ user.page }}</a>
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
    this.user;
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
/* General Container Styling */
div {
  padding-top: 10px;
  max-width: 800px;
  margin: 0 auto;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f6fa;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative; /* To contain the absolutely positioned back-button */
}

/* Back Button */
.back-button {
  position: absolute;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 50%;
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  top: 20px;
  left: 20px;
}

.back-button:hover {
  background-color: #2c8a6a;
  transform: scale(1.05);
}

/* Headings */
h1 {
  color: #2c3e50;
  text-align: center;
  font-size: 3em;
  margin-bottom: 20px;
}

h2 {
  color: #2c3e50;
  text-align: center;
  font-size: 2em;
  margin-bottom: 30px;
}

/* Action Buttons */
button {
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 12px 25px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin: 10px 5px;
}

button:hover {
  background-color: #2c8a6a;
  transform: translateY(-2px);
}

button:active {
  transform: translateY(0px);
}

/* User Details Container */
.user-details {
  background-color: #ffffff;
  padding: 25px 30px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
}

.user-details p {
  font-size: 1.1em;
  color: #34495e;
  margin: 15px 0;
  display: flex;
  align-items: center;
}

.user-details p strong {
  width: 150px;
  color: #2c3e50;
  flex-shrink: 0;
}

.user-details p a {
  color: #2980b9;
  text-decoration: none;
}

.user-details p a:hover {
  text-decoration: underline;
}

/* Profile Image Styling */
.user-details img {
  border-radius: 50%;
  border: 4px solid #42b983;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100px;
  height: 100px;
  object-fit: cover;
}

/* Responsive Design */
@media (max-width: 768px) {
  h1 {
    font-size: 2.5em;
  }

  h2 {
    font-size: 1.8em;
  }

  .user-details p {
    flex-direction: column;
    align-items: flex-start;
  }

  .user-details p strong {
    width: auto;
    margin-bottom: 5px;
  }

  button {
    width: 100%;
    margin: 10px 0;
  }
}
</style>
