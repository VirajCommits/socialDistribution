import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/Login.vue';
import UserFeed from '../components/Feed.vue';
import AuthorProfile from '../components/AuthorProfile.vue';
import FollowRequest from '../components/FollowRequest.vue';

const routes = [
  {
    path: '/',
    name: 'Login',
    component: UserLogin,
  },
  {
    path: '/feed',
    name: 'Feed',
    component: UserFeed,
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
    meta: {requiresAuth: true},
    props: true,  // Ensure props are passed
    beforeEnter: (to, from, next) => {
      if (!localStorage.getItem('token')) {
        next({ name: 'Login' });
      } else {
        next();
      }
    },
  },
  {
    path: '/author/:uuid/follow_requests',
    name: 'FollowRequests',
    component: FollowRequest,
    props: true, 
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

router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('token');
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next({ name: 'Login' });  // Redirect to login if not authenticated
  } else {
    next();
  }
});

export default router;
