<template>
  <div id="app">
    <nav>
      <ul>
        <li>
          <RouterLink to="/posts/all">All Posts</RouterLink>
        </li>
        <li>
          <RouterLink to="/posts/create">Create Post</RouterLink>
        </li>
      </ul>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}

nav ul {
  list-style-type: none;
  padding: 0;
  display: flex;
  gap: 20px;
  justify-content: center;
}

nav ul li {
  display: inline;
}

router-link {
  text-decoration: none;
  color: #42b983;
  font-weight: bold;
}

router-link:hover {
  text-decoration: underline;
}
</style>
