import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/UserLogin.vue';
import UserSignup from '../components/UserSignup.vue';
import StreamPage from '../components/StreamPage.vue';
import ProfilePage from '../components/ProfilePage.vue';
import CreatePost from '../components/CreatePost.vue';
import AuthorPosts from '../components/AuthorPosts.vue';
import EditPost from '../components/EditPost.vue';
import ExploreAuthors from '../components/ExploreAuthors.vue';
// Import your PostDetail component if needed
import PostDetail from '../components/PostDetail.vue';

const routes = [
  { path: '/login', component: UserLogin },
  { path: '/signup', component: UserSignup },
  { path: '/', redirect: '/login' },
  { path: '/stream', component: StreamPage },
  { path: '/profile', component: ProfilePage },
  { path: '/addPost', component: CreatePost },
  { path: '/posts/all', component: AuthorPosts },
  { path: '/posts/create', component: CreatePost },
  { path: '/explore', component: ExploreAuthors },
  {
    path: '/edit-post/:id',
    name: 'EditPost',
    component: EditPost,
    props: true,
  },
  {
    path: '/swagger',
    beforeEnter() {
      window.location.href = 'https://social-distribution-1-3adb84f120d9.herokuapp.com/swagger'; // Redirect to Swagger UI
    },
  },
  {
    path: '/posts/:postId',
    name: 'PostDetail',
    component: PostDetail,
    props: true,
  },
  // Catch-all route to redirect to the main app
  { path: '/:catchAll(.*)', redirect: '/stream' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


export default router;
