<template>
  <HelloWorld />
  <CreatePost />
  <div>
    <AuthorPosts :authorId="authorId" />
  </div>
</template>

<script>
import HelloWorld from "./components/HelloWorld.vue";
import CreatePost from "./components/CreatePost.vue";
import AuthorPosts from "./components/AuthorPosts.vue";

export default {
  name: "App",
  components: {
    HelloWorld,
    CreatePost,
    AuthorPosts,
  },
  data() {
    return {
      authorId: "http://www.github.com", // Replace with the actual author ID
    };
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
