<template>
  <div>{{ object.title }}</div>
</template>

<script>
export default {
  name: 'Event',
  props: {
    object: Object,
  },
};
</script>
