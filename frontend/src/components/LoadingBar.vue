<template>
  <div class="shadow w-full bg-gray-100">
    <div
      class="bg-blue-900 text-xs leading-none py-2 my:auto text-center text-white"
      :style="{ width: `${loadingState}%` }"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'LoadingBar',
  data() {
    return {
      loadingState: 0,
    };
  },
  mounted() {
    setInterval(() => {
      this.loadingState += 5;
      if (this.loadingState > 100) {
        this.loadingState = 0;
      }
    }, 50);
  },
};
</script>
