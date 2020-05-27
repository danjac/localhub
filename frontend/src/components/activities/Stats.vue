<template>
  <div class="flex flex-wrap items-center text-xs text-muted">
    <div v-if="object.num_comments" class="mr-2">
      <a href="#">
        {{ object.num_comments }} {{ 'Comment' | pluralize(object.num_comments) }}
      </a>
    </div>
  </div>
</template>

<script>
import pluralize from 'pluralize';

export default {
  filters: {
    pluralize,
  },
  props: {
    object: {
      type: Object,
      required: true,
    },
    isDetail: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
