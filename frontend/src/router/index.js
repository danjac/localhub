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
      requiresMember: true,
    },
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
    meta: {
      requiresMember: true,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "login" */ '../views/Login.vue'),
  },
  {
    path: '/posts',
    name: 'PostList',
    component: () =>
      import(/* webpackChunkName: "postList" */ '../views/posts/PostList.vue'),
    children: [
      {
        path: '/submit',
        name: 'SubmitPost',
        component: () =>
          import(/* webpackChunkName: "submitPost" */ '../views/posts/SubmitPost.vue'),
      },
    ],
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
  // TBD: handle requiresModerator,  requiresAdmin
  // ensure any sidenav action closes the nav
  store.dispatch('closeNav');
  const loginRoute = { path: '/login', params: { nextUrl: to.fullPath } };
  if (to.matched.some((record) => record.meta.requiresMember)) {
    if (store.getters.isMember) {
      next();
    } else {
      // logged in ? show "welcome" page
      // otherwise redirect to login
      next(store.state.user ? { path: '/welcome' } : loginRoute);
    }
  } else if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (store.state.user) {
      next();
    } else {
      next(loginRoute);
    }
  } else {
    next();
  }
});

export default router;
