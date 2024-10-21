import { createRouter, createWebHistory } from 'vue-router';
import TestCommentsLikes from '../components/TestCommentsLikes.vue'; // Import the test component

const routes = [
  {
    path: '/test/comments-likes',
    name: 'TestCommentsLikes',
    component: TestCommentsLikes,
    props: () => {
      return { authorId: '19817e9b8af1497fb863e89e10eefe68', postId: '9271ea2f7d184108a0aead1065ede8fc' }; // Replace 'your-valid-post-id' with a valid ID
    },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
