<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HelloWorld',
  data() {
    return {
      message: ''
    }
  },
  created() {
    axios.get('api/test/')
      .then(response => {
        this.message = response.data.message;
      })
      .catch(error => {
        console.error(error);
      });
  }
}
</script>

<style>
h1 {
  color: #42b983;
}
</style>
