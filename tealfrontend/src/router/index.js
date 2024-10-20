import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/Login.vue';
import Feed from '../components/Feed.vue';
import AuthorProfile from '../components/AuthorProfile.vue';

const routes = [
  {
    path: '/',
    name: 'Login',
    component: UserLogin,
  },
  {
    path: '/feed',
    name: 'Feed',
    component: Feed,
    beforeEnter: (to, from, next) => {
      if (!localStorage.getItem('token')) {
        next({ name: 'Login' });
      } else {
        next();
      }
    },
  },
  {
    path: '/author/:uuid',
    name: 'AuthorProfile',
    component: AuthorProfile,
    props: true,  // Ensure props are passed
    beforeEnter: (to, from, next) => {
      if (!localStorage.getItem('token')) {
        next({ name: 'Login' });
      } else {
        next();
      }
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
