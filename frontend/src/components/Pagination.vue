<template>
  <div class="text-sm flex justify-between" v-if="next || previous">
    <a
      :class="getPaginationClass(previous)"
      href="#"
      @click.prevent="$emit('previousPage')"
    >
      Previous
    </a>
    <a :class="getPaginationClass(next)" href="#" @click.prevent="$emit('nextPage')">
      Next
    </a>
  </div>
</template>

<script>
export default {
  props: {
    next: {
      type: String,
      required: false,
    },
    previous: {
      type: String,
      required: false,
    },
  },
  methods: {
    getPaginationClass(value) {
      return value
        ? 'text-indigo-900 hover:text-indigo-700'
        : 'text-gray-500 pointer-events-none';
    },
  },
};
</script>
