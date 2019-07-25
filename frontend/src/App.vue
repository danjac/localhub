<template>
  <div id="app" class="container">
    <component :is="layout">
      <router-view />
    </component>
  </div>
</template>

<script>
export default {
  computed: {
    layout() {
      // in routes: { meta: { layout: 'no-sidebar-layout' } }
      return this.$route.meta.layout || 'default-layout';
    }
  }
};
</script>

<style lang="scss">
.conversation-input {
  height: 2rem;
}
</style>
