<template>
  <article :role="object.object_type" class="card" v-show="!isDeleted">
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
      <slot name="header"></slot>
    </div>

    <div class="mb-3">
      <Collapsable>
        <slot name="content"></slot>
      </Collapsable>
    </div>

    <div class="card-footer">
      <slot name="stats">
        <Stats :object="object" :is-detail="isDetail" class="mb-3" />
      </slot>

      <div class="flex items-center">
        <slot name="actions">
          <Actions
            :object="object"
            :is-detail="isDetail"
            @delete="isDeleted = true"
            class="mr-2"
          />
        </slot>
        <slot name="links">
          <a
            class="text-sm mr-2"
            href="/posts/2243/were-all-about-to-get-lost-in-a-labyrinth-sequel/"
            >Link</a
          >
        </slot>
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
  data() {
    return {
      isDeleted: false,
    };
  },
};
</script>
