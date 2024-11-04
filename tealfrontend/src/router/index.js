import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/UserLogin.vue';
import UserSignup from '../components/UserSignup.vue';
import StreamPage from '../components/StreamPage.vue';
import ProfilePage from '../components/ProfilePage.vue';
import CreatePost from '../components/CreatePost.vue';
import AuthorPosts from '../components/AuthorPosts.vue';
import EditPost from '../components/EditPost.vue';
import ExploreAuthors from '../components/ExploreAuthors.vue';
import PostDetail from '../components/PostDetail.vue';

const routes = [
  { path: '/login', component: UserLogin },
  { path: '/signup', component: UserSignup },
  { path: '/', redirect: '/login' }, 
  { path: '/stream', component: StreamPage }, 
  {path: '/profile', component: ProfilePage},
  {path: '/addPost', component: CreatePost},
  {path: '/posts/all', component: AuthorPosts},
  {path: '/posts/create', component: CreatePost},
  {path: '/explore', component: ExploreAuthors},
  {
    path: '/edit-post/:id',  // Ensure this path matches the structure you're using
    name: 'EditPost',
    component: EditPost,
    props: true,  // Enable route params to be passed as props
  },
  {
    path: '/posts/:postId',  // Path for viewing a specific post by ID
    name: 'PostDetail',
    component: PostDetail,
    props: true,  // Pass route params as props
  },

];

const router = createRouter({
  history: createWebHistory('/project'),
  routes,
});

export default router;
