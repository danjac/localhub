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

      <Timesince
        :timestamp="object.published || object.created"
        :user="object.owner"
        class="mb-3"
      />

      <div class="flex flex-wrap items-center text-sm">
        <div class="mr-2">
          <a
            href="https://io9.gizmodo.com"
            rel="nofollow noopener noreferrer"
            target="_blank"
            >io9.gizmodo.com</a
          >
        </div>
      </div>
    </div>

    <div class="mb-3">
      <div
        data-controller="collapsable"
        data-collapsable-class="opacity-75 h-32 md:h-48 lg:h-64 overflow-hidden cursor-pointer"
      >
        <div
          data-target="collapsable.container"
          data-action="click->collapsable#toggle"
          class="opacity-75 h-32 md:h-48 lg:h-64 overflow-hidden cursor-pointer collapsable"
        >
          <div class="lg:flex">
            <a
              href="https://io9.gizmodo.com/were-all-about-to-get-lost-in-a-labyrinth-sequel-1843679643"
              class="block lg:inline-block mb-3 lg:mb-0 lg:w-1/3 h-auto lg:mr-2"
              target="_blank"
            >
              <img
                src="https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_675,pg_1,q_80,w_1200/nhc1hs3umk16qnye98ql.jpg"
                alt="We're All About to Get Lost in a Labyrinth Sequel"
                loading="lazy"
                class=""
              />
            </a>

            <blockquote class="block lg:inline-block text-sm lg:w-2/3">
              Apparently, the glass orbs are on their way back. Perhaps.
            </blockquote>
          </div>
        </div>

        <div
          class="flex justify-center items-center my-3"
          data-target="collapsable.toggle"
        >
          <button class="btn btn-link w-full text-sm" data-action="collapsable#toggle">
            Show More
          </button>
        </div>
      </div>
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
import Timesince from '@/components/Timesince';

export default {
  name: 'Post',
  props: {
    object: Object,
  },
  components: {
    Timesince,
  },
};
</script>
