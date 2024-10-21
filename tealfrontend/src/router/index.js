import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/UserLogin.vue';
import UserSignup from '../components/UserSignup.vue';
import StreamPage from '../components/StreamPage.vue';
import ProfilePage from '../components/ProfilePage.vue';
import CreatePost from '../components/CreatePost.vue';
import AuthorPosts from '../components/AuthorPosts.vue';

const routes = [
  { path: '/login', component: UserLogin },
  { path: '/signup', component: UserSignup },
  { path: '/', redirect: '/login' }, 
  { path: '/stream', component: StreamPage }, 
  {path: '/profile', component: ProfilePage},
  {path: '/addPost', component: CreatePost},
  {path: '/posts/all', component: AuthorPosts},

];

const router = createRouter({
  history: createWebHistory('/project'),
  routes,
});

export default router;
