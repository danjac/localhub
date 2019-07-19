import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);
// Routes we'll need:
// Home/activity stream
// Search
// Tag detail
// Community about page/not found/permission required
// Authentication: login/signup/recover password
// Posts: list/submit/edit/detail
// Photos: list/submit/edit/detail
// Events: list/submit/edit/detail
// Notifications
// Direct messages: inbox/outbox/create/reply/detail
// Comments: detail/edit
// Favorites: posts/comments
// Following: users/tags
// Profile: about/posts/comments
// Members
// Profile settings: edit/emails/password
// Community settings: edit
// Membership settings: list/edit
// Invites: list/create
// Join requests: list

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () =>
        import(/* webpackChunkName: "about" */ './views/About.vue')
    }
  ]
});
