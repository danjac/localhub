<template>
  <div id="app">
    <HeaderNav />
    <div class="mt-2 px-2 md:px-5 flex min-h-full">
      <router-view />
    </div>
  </div>
</template>

<script>
import HeaderNav from './components/HeaderNav.vue';

export default {
  components: {
    HeaderNav,
  },
};
</script>
