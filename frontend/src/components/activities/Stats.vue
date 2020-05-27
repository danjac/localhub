<template>
  <div class="flex flex-wrap items-center text-xs text-muted">
    <div class="mr-2">
      <a href="#">
        1 Comment
      </a>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    object: {
      type: Object,
      required: true,
    },
  },
};
</script>
