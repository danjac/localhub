<template>
  <div>
    <div
      :class="{
        'opacity-75 h-32 md:h-48 lg:h-64 overflow-hidden cursor-pointer': collapsed,
      }"
      ref="container"
      @click="showAll"
    >
      <slot />
    </div>
    <div class="flex justify-center items-center my-3" v-if="collapsed">
      <button class="btn btn-link w-full text-sm" @click="showAll">
        Show More
      </button>
    </div>
  </div>
</template>

<script>
const MAX_HEIGHT = 360;

export default {
  data() {
    return {
      collapsed: false,
      expanded: false,
    };
  },
  mounted() {
    this.observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.height > MAX_HEIGHT && !this.expanded) {
          this.collapsed = true;
        }
      }
    });
    this.observer.observe(this.$refs.container);
  },
  beforeDestroy() {
    this.observer.disconnect(this.$refs.container);
  },
  methods: {
    showAll(event) {
      if (!this.expanded) {
        event.preventDefault();
        this.expanded = true;
        this.collapsed = false;
      }
    },
  },
};
</script>
