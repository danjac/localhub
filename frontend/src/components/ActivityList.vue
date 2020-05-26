<template>
  <div>
    <component
      v-for="obj in activities"
      :is="getComponent(obj)"
      :key="`${obj.object_type}-${obj.id}`"
      :object="obj"
      class="mb-2"
    >
      {{ obj.object_type }}
    </component>
  </div>
</template>

<script>
// import Event from '@/components/Event';
//import Poll from '@/components/Poll';
import Post from '@/components/Post';
import Photo from '@/components/Photo';

export default {
  name: 'ActivityList',
  props: {
    activities: {
      type: Array,
      default: () => new Array(),
    },
  },
  methods: {
    getComponent(obj) {
      return {
        // event: Event,
        photo: Photo,
        post: Post,
      }[obj.object_type];
    },
  },
};
</script>
