<template>
  <div class="px-2 md:px-5 flex min-h-full">
    <SideNav />
    <div class="lg:ml-2 w-full lg:w-5/6 lg:block">
      <slot />
    </div>
  </div>
</template>

<script>
import SideNav from '@/components/SideNav.vue';

export default {
  components: {
    SideNav,
  },
};
</script>
