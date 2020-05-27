<template>
  <div
    class="fixed z-50 w-4/5 lg:w-1/3 flex items-center text-center p-3 message"
    :class="message.tags"
  >
    <div class="mx-auto text-center">{{ message.message }}</div>
    <button @click.prevent="$emit('dismiss')">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        focusable="false"
        role="img"
        class="text-white"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M10 14L12 12M12 12L14 10M12 12L10 10M12 12L14 14M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
          stroke="white"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ToastMessage',
  props: {
    message: Object,
  },
  mounted() {
    setTimeout(() => {
      this.$emit('dismiss');
    }, 5000);
  },
};
</script>
