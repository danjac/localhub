<template>
  <div class="flex rounded-full items-center text-sm pr-3 bg-gray-300 mr-2">
    <img
      v-if="user.avatar"
      :src="user.avatar"
      :alt="user.name"
      class="rounded-full bg-transparent mr-2 h-4 w-4 text-xs"
      width="16"
      height="16"
    />
    <div
      v-else
      class="font-bold align-middle rounded-full text-center bg-indigo-800 text-white text-xs h-4 w-4 mr-2"
    >
      {{ initial }}
    </div>

    <a :title="user.full_name" class="truncate text-gray-900" href="#">
      {{ user.username }}
    </a>
  </div>
</template>

<script>
export default {
  name: 'Chip',
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      initial: this.user.full_name.charAt(0).toUpperCase(),
    };
  },
};
</script>
