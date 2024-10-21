// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import AuthorPosts from '../components/AuthorPosts.vue';
import CreatePost from '../components/CreatePost.vue';
import EditPost from '../components/EditPost.vue';

const routes = [
  {
    path: '/posts/all',
    name: 'AuthorPosts',
    component: AuthorPosts,
    props: () => {
      return { authorId: 
      '45c7cdd3-02be-4f93-9078-5ef5df3e5dbb' };
    }, // Removed 'route'
  },
  
  {
    path: '/posts/create',
    name: 'CreatePost',
    component: CreatePost,
  },
  {
    path: '/posts/edit/:id',
    name: 'EditPost',
    component: EditPost,
    props: true, // Allows route params to be passed as props to the component
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});


export default router;
