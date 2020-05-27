<template>
  <Activity :object="object" :is-detail="isDetail">
    <template v-slot:header>
      <div class="flex flex-wrap items-center text-sm">
        <div class="mr-2">
          <a
            v-if="object.domain"
            :href="object.base_url"
            rel="nofollow noopener noreferrer"
            target="_blank"
            >{{ object.domain }}</a
          >
        </div>
      </div>
    </template>

    <template v-slot:content>
      <div class="lg:flex">
        <a
          v-if="object.opengraph_image"
          href="#"
          class="block lg:inline-block mb-3 lg:mb-0 lg:w-1/3 h-auto lg:mr-2"
        >
          <img :src="object.opengraph_image" :alt="object.tile" loading="lazy" />
        </a>

        <blockquote
          class="block lg:inline-block text-sm lg:w-2/3"
          v-if="object.opengraph_description"
        >
          {{ object.opengraph_description }}
        </blockquote>
      </div>
    </template>
  </Activity>
</template>

<script>
import Activity from '@/components/activities/Activity';

export default {
  name: 'Post',
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
  components: {
    Activity,
  },
};
</script>
