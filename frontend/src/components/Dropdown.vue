<template>
  <div class="text-sm">
    <button class="btn btn-dropdown" @click.prevent.stop="toggle">
      {{ label }}
    </button>
    <div class="dropdown-menu mt-1 z-50" ref="menu" v-show="active">
      <slot />
    </div>
  </div>
</template>

<script>
import { fitIntoViewport } from '@/utils';

export default {
  props: {
    label: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      active: false,
    };
  },
  mounted() {
    document.addEventListener('click', this.close);
    document.addEventListener('keydown', this.close);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.close);
    document.removeEventListener('keydown', this.close);
  },
  methods: {
    close() {
      this.active = false;
    },
    toggle() {
      this.active = !this.active;
      this.$nextTick(() => {
        if (this.active) {
          fitIntoViewport(this.$refs.menu);
        }
      });
    },
  },
};
</script>
