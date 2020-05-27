<template>
  <article role="post" class="card">
    <div class="mb-3">
      <div class="font-semibold flex flex-wrap items-center mb-3">
        <div class="tracking-tight flex flex-wrap items-center break-words">
          <span class="inline-block mr-2">
            <a
              v-if="object.url"
              :href="object.url"
              rel="nofollow noopener noreferrer"
              target="_blank"
              >{{ object.title }}</a
            >
            <a v-else>
              {{ object.title }}
            </a>
          </span>
          <a class="tag inline-block mr-2 hover:text-gray-300" href="#">
            {{ object.object_type | capitalize }}
          </a>
        </div>
      </div>

      <div class="flex flex-wrap items-center mb-3">
        <Timesince
          :timestamp="object.published || object.created"
          :user="object.owner"
        />
      </div>

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
    </div>

    <div class="mb-3">
      <Collapsable>
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
      </Collapsable>
    </div>

    <div class="card-footer">
      <Stats :object="object" :is-detail="isDetail" class="mb-3" />

      <div class="flex items-center">
        <Actions :object="object" :is-detail="isDetail" class="mr-2" />
        <a
          class="text-sm mr-2"
          href="/posts/2243/were-all-about-to-get-lost-in-a-labyrinth-sequel/"
          >Link</a
        >
      </div>
    </div>
  </article>
</template>

<script>
import { capitalize } from 'lodash';

import Collapsable from '@/components/Collapsable';
import Timesince from '@/components/Timesince';
import Actions from '@/components/activities/Actions';
import Stats from '@/components/activities/Stats';

export default {
  name: 'Post',
  filters: {
    capitalize,
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
  components: {
    Collapsable,
    Stats,
    Actions,
    Timesince,
  },
};
</script>
