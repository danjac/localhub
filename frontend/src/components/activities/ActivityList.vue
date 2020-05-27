<template>
  <div>
    <component
      v-for="obj in activities"
      :is="getComponent(obj)"
      :key="`${obj.object_type}-${obj.id}`"
      :object="obj"
      class="mb-2"
      @delete="$emit('delete', obj)"
    >
    </component>
  </div>
</template>

<script>
// TBD: move this under /activities subdirector
// import Event from '@/components/Event';
//import Poll from '@/components/Poll';
import Post from '@/components/posts/Post';
import Photo from '@/components/photos/Photo';

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
