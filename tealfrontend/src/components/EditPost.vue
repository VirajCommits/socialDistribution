<script>
export default {
  name: "EditPost",
  data() {
    return {
      post: null,
      // Other data properties...
    };
  },
  mounted() {
    this.fetchPost();
  },
  methods: {
    fetchPost() {
      const postId = this.$route.params.id;
      const authorId = encodeURIComponent("author-identifier"); // Replace with actual author ID
      const apiUrl = `http://localhost:8000/project/service/api/authors/${authorId}/posts/${encodeURIComponent(
        postId
      )}/`;

      axios
        .get(apiUrl)
        .then((response) => {
          this.post = response.data;
          // Handle the response data...
        })
        .catch((error) => {
          console.error("Error fetching post:", error);
          // Handle the error...
        });
    },
    // Other methods for handling form submission...
  },
};
</script>
