// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import AuthorPosts from '@/components/AuthorPosts.vue';
import CreatePost from '@/components/CreatePost.vue';
import EditPost from '@/components/EditPost.vue';

const routes = [
  {
    path: '/posts/all',
    name: 'AuthorPosts',
    component: AuthorPosts,
    props: route => ({ authorId: 'http://www.github.com' }), // Replace with dynamic authorId as needed
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
  history: createWebHistory(),
  routes,
});

export default router;
