<template>
  <Activity :object="object" :is-detail="isDetail">
    <template v-slot:content>
      <img
        class="img-responsive"
        :src="object.large_image_url"
        width=""
        height=""
        loading="lazy"
        :alt="object.title"
      />
    </template>
  </Activity>
</template>

<script>
import Activity from '@/components/activities/Activity';

export default {
  name: 'Photo',
  components: {
    Activity,
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
