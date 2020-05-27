<template>
  <div
    class="modal fixed w-full h-full top-0 left-0 flex items-center justify-center"
    :class="{ 'opacity-0 pointer-events-none': !active }"
  >
    <div
      class="modal-overlay absolute w-full h-full bg-gray-900 opacity-50"
      @click.prevent="close"
    ></div>

    <div
      class="modal-container bg-white w-11/12 md:max-w-md mx-auto shadow-lg z-50 overflow-y-auto"
    >
      <div class="modal-content py-4 text-left px-6 z-100 bg-white">
        <div class="flex justify-between items-center">
          <h2 class="font-bold">{{ header }}</h2>
          <button class="modal-close cursor-pointer z-50" @click.prevent="close">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              focusable="false"
              role="img"
              class="text-black"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M10 14L12 12M12 12L14 10M12 12L10 10M12 12L14 14M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                stroke="black"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
        <p class="py-4">
          <slot />
        </p>
        <div class="flex items-center">
          <button class="btn btn-primary mr-2" @click.prevent="confirm">
            Yes, Please
          </button>
          <button class="btn btn-secondary" @click.prevent="close">
            No, Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    header: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      active: false,
    };
  },
  methods: {
    confirm() {
      this.close();
      this.$emit('confirm');
    },
    open() {
      this.active = true;
    },
    close() {
      this.active = false;
    },
  },
};
</script>
