<template>
  <div>{{ object.title }}</div>
</template>

<script>
export default {
  name: 'Photo',
  props: {
    object: Object,
  },
};
</script>
