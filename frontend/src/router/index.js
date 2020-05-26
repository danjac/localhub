import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';

import store from '../store';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      requireMember: true,
    },
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "login" */ '../views/Login.vue'),
  },
];

const router = new VueRouter({
  mode: 'history',
  linkActiveClass: 'active',
  base: process.env.BASE_URL,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { x: 0, y: 0 };
    }
  },
  routes,
});

router.beforeEach((to, from, next) => {
  // TBD handle different roles...
  if (to.matched.some((record) => record.meta.requireMember)) {
    if (store.getters.isMember) {
      next();
    } else {
      // logged in ? show "welcome" page
      // otherwise redirect to login
      next(
        store.state.user
          ? { path: '/welcome' }
          : { path: '/login', params: { nextUrl: to.fullPath } }
      );
    }
  } else if (to.matched.some((record) => record.meta.requireAuth)) {
    if (store.state.user) {
      next();
    } else {
      next({
        path: '/login',
        params: { nextUrl: to.fullPath },
      });
    }
  } else {
    next();
  }
});

export default router;
