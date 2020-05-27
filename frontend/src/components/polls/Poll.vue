<template>
  <div>{{ object.title }}</div>
</template>

<script>
export default {
  name: 'Poll',
  props: {
    object: Object,
  },
};
</script>
