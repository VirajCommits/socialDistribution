import Vue from 'vue';
import Router from 'vue-router';
import AuthorPosts from '@/components/AuthorPosts.vue';
import CreatePost from '@/components/CreatePost.vue';
import EditPost from '@/components/EditPost.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/posts/all',
      name: 'AuthorPosts',  
      component: AuthorPosts,  
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
    },
  ],
});
