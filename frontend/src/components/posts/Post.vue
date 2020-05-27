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
            {{ object.object_type }}
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
      <div class="flex flex-wrap items-center text-xs text-muted mb-3">
        <div class="mr-2">
          <a
            href="/posts/2243/were-all-about-to-get-lost-in-a-labyrinth-sequel/#comments"
          >
            1 Comment
          </a>
        </div>
      </div>

      <div class="flex items-center">
        <div
          class="text-sm mr-2"
          data-controller="dropdown"
          data-action="click@window->dropdown#close keydown@window->dropdown#close"
        >
          <button class="btn btn-dropdown" data-action="dropdown#toggle">
            Actions...
          </button>
          <div class="dropdown-menu mt-1 hidden" data-target="dropdown.menu">
            <a
              class="dropdown-menu-item"
              href="/posts/2243/~pin/"
              data-turbolinks="false"
              data-controller="ajax"
              data-action="ajax#post"
              >Pin</a
            >

            <a class="dropdown-menu-item" href="/posts/2243/~comment/#comment-form">
              Comment
            </a>

            <div data-controller="ajax">
              <a
                class="dropdown-menu-item line-through hidden"
                href="/posts/2243/~bookmark/remove/"
                data-turbolinks="false"
                data-target="ajax.toggle ajax.button"
                data-action="ajax#post"
                >Bookmark</a
              >
              <a
                class="dropdown-menu-item"
                href="/posts/2243/~bookmark/"
                data-turbolinks="false"
                data-target="ajax.toggle ajax.button"
                data-action="ajax#post"
                >Bookmark</a
              >
            </div>

            <a class="dropdown-menu-item" href="/posts/2243/~update/">Edit</a>

            <a
              class="dropdown-menu-item"
              href="/posts/2243/~delete/"
              data-turbolinks="false"
              data-controller="ajax"
              data-action="ajax#post"
              data-ajax-redirect="/"
              data-ajax-confirm-header="Delete"
              data-ajax-confirm-body="Are you sure you want to delete this post?"
            >
              Delete</a
            >
          </div>
        </div>

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
import Collapsable from '@/components/Collapsable';
import Timesince from '@/components/Timesince';

export default {
  name: 'Post',
  props: {
    object: Object,
  },
  components: {
    Collapsable,
    Timesince,
  },
};
</script>
