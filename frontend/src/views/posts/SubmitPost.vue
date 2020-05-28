<template>
  <div>
    <form class="p-1 md:p-3 border border-gray-500" @submit.prevent="submit" novalidate>
      <input type="hidden" name="opengraph_image" id="id_opengraph_image" />
      <input type="hidden" name="opengraph_description" id="id_opengraph_description" />

      <div class="mb-3">
        <label for="id_title" class="block font-semibold mb-3 text-sm">Title</label>
        <input
          type="text"
          v-model.trim="$v.title.$model"
          autocomplete="off"
          class="form-input"
          :class="{ 'form-input-error': $v.title.$error }"
        />

        <div v-if="$v.title.$error">
          <div v-if="!$v.title.required" class="text-red-600 mb-3 text-sm">
            You must provide a title
          </div>
        </div>
      </div>
      <div class="mb-3">
        <label for="id_url" class="block font-semibold mb-3 text-sm">URL</label>

        <div>
          <div data-target="opengraph-preview.container"></div>

          <div class="flex items-center">
            <div class="flex-grow">
              <input
                type="url"
                name="url"
                v-model.trim="$v.url.$model"
                class="form-input"
                :class="{ 'form-input-error': $v.url.$error }"
              />
            </div>
            <button
              type="button"
              class="btn btn-input-addon"
              title="Fetch content from URL"
              disabled="true"
              data-target="opengraph-preview.fetchButton"
              data-action="opengraph-preview#fetch"
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                focusable="false"
                role="img"
                class="text-black"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M4 16L4 17C4 18.6569 5.34315 20 7 20L17 20C18.6569 20 20 18.6569 20 17L20 16M16 12L12 16M12 16L8 12M12 16L12 4"
                  stroke="black"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                ></path>
              </svg>
            </button>
            <button
              type="button"
              class="btn btn-input-addon"
              title="Remove content from URL"
              disabled=""
              data-target="opengraph-preview.clearButton"
              data-action="opengraph-preview#clear"
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                focusable="false"
                role="img"
                class="text-black"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M6 18L18 6M6 6L18 18"
                  stroke="black"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                ></path>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="$v.url.$error">
          <div v-if="!$v.url.url" class="text-red-600 mb-3 text-sm">
            You must provide a valid URL
          </div>
        </div>

        <p class="text-gray-700 mb-3 text-sm">
          You can attach an image and/or description from the webpage to this post by
          clicking the Download button on the right.
        </p>
      </div>

      <div class="mb-3">
        <label for="id_hashtags" class="block font-semibold mb-3 text-sm">#tags</label>

        <div
          data-controller="typeahead"
          data-typeahead-selected-class="bg-gray-500 text-white"
          data-typeahead-config='[{"key": "#", "url": "/tags/autocomplete/"}]'
        >
          <ul
            class="hidden typeahead-menu mt-1 text-sm"
            data-target="typeahead.selector"
          ></ul>
          <input
            type="text"
            name="hashtags"
            data-target="typeahead.input"
            data-action="keyup->typeahead#keyup keydown->typeahead#keydown"
            autocomplete="off"
            maxlength="300"
            placeholder=""
            class="form-input"
            id="id_hashtags"
          />
        </div>

        <p class="text-gray-700 mb-3 text-sm">
          #tags can also be added to title and description.
        </p>
      </div>

      <div class="mb-3">
        <label for="id_mentions" class="block font-semibold mb-3 text-sm"
          >@mentions</label
        >

        <div
          data-controller="typeahead"
          data-typeahead-selected-class="bg-gray-500 text-white"
          data-typeahead-config='[{"key": "@", "url": "/people/autocomplete/"}]'
        >
          <ul
            class="hidden typeahead-menu mt-1 text-sm"
            data-target="typeahead.selector"
          ></ul>
          <input
            type="text"
            name="mentions"
            data-target="typeahead.input"
            data-action="keyup->typeahead#keyup keydown->typeahead#keydown"
            autocomplete="off"
            maxlength="300"
            placeholder=""
            class="form-input"
            id="id_mentions"
          />
        </div>

        <p class="text-gray-700 mb-3 text-sm">
          @mentions can also be added to title and description.
        </p>
      </div>

      <div class="mb-3">
        <label for="id_description" class="block font-semibold mb-3 text-sm"
          >Description</label
        >

        <div
          class="markdownx"
          data-controller="tabs typeahead markdown"
          data-typeahead-selected-class="bg-gray-500 text-white"
          data-typeahead-config='[{"key": "#", "url": "/tags/autocomplete/"}, {"key": "@", "url": "/people/autocomplete/"}]'
        >
          <div class="tabs mb-3 text-sm">
            <button
              class="tab-item active"
              type="button"
              data-target="tabs.tab"
              data-action="tabs#select"
              data-tab="editor"
            >
              Edit
            </button>
            <button
              class="tab-item"
              type="button"
              disabled="true"
              data-target="tabs.tab markdown.previewTab"
              data-action="tabs#select"
              data-tab="preview"
            >
              Preview
            </button>
            <button
              class="tab-item"
              type="button"
              data-target="tabs.tab"
              data-action="tabs#select"
              data-tab="guide"
            >
              Help
            </button>
          </div>
          <div class="-mb-px mb-3" data-target="tabs.pane" data-tab="editor">
            <div class="text-xs flex flex-wrap items-center mb-3">
              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="**[SELECTION]**"
                >Bold</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="_[SELECTION]_"
                >Italic</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="[[SELECTION]](url)"
                >Link</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="![]([SELECTION])"
                >Image</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="> [SELECTION]"
                >Quote</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-markdown="`[SELECTION]`"
                >Code</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-multiline=""
                data-markdown="* [SELECTION]"
                >List (Bullets)</a
              >

              <a
                href="#"
                class="inline-block mr-2"
                data-action="markdown#select"
                data-multiline=""
                data-markdown="1. [SELECTION]"
                >List (Numbers)</a
              >

              <div
                class=""
                data-controller="dropdown"
                data-dropdown-toggle-class="hidden"
                data-action="click@window->dropdown#close keydown@window->dropdown#close"
              >
                <button
                  class="btn btn-dropdowbtn btn-dropdown"
                  type="button"
                  data-action="dropdown#toggle"
                >
                  Emoji...
                </button>
                <ul
                  class="hidden dropdown-menu mt-3 overflow-y-scroll h-32"
                  data-target="dropdown.menu"
                >
                  <li class="border-b border-gray-800 pb-1 font-semibold">People</li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :thumbsup: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/thumbsup.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Thumbs Up
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :thumbsdown: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/thumbsdown.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Thumbs Down
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :heart: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/heart.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Heart
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :clap: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/clap.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Clap
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :smile: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/smile.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Smile
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :wink: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/wink.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Wink
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :joy: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/joy.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Joy
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :laughing: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/laughing.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Laughing
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :thinking: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/thinking.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Thinking
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :sob: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/sob.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Sob
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :heart_eyes: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/heart_eyes.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Heart Eyes
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :smirk: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/smirk.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Smirk
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :blush: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/blush.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Blush
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :confused: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/confused.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Confused
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :disappointed: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/disappointed.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Disappointed
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :no_mouth: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/no_mouth.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        No Mouth
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :innocent: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/innocent.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Innocent
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :neutral_face: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/neutral_face.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Neutral Face
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :fearful: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/fearful.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Fearful
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :sweat: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/sweat.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Sweat
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :angry: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/angry.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Angry
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :rage: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/rage.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Rage
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :astonished: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/astonished.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Astonished
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :stuck_out_tongue: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/stuck_out_tongue.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Stuck Out Tongue
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :open_mouth: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/open_mouth.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Open Mouth
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :satisfied: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/satisfied.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Satisfied
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :scream: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/scream.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Scream
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :sunglasses: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/sunglasses.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Sunglasses
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :fire: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/fire.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Fire
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :tada: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/tada.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Tada
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :see_no_evil: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/see_no_evil.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        See No Evil
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :point_up: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/point_up.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Point Up
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :wave: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/wave.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Wave
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :raised_hands: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/raised_hands.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Raised Hands
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :pray: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/pray.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Pray
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :metal: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/metal.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Metal
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :alien: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/alien.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Alien
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :angel: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/angel.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Angel
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :man: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/man.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Man
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :woman: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/woman.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Woman
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :baby: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/baby.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Baby
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :detective: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/detective.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Detective
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :mask: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/mask.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Mask
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :poop: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/poop.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Poop
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :skull: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/skull.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Skull
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :zap: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/zap.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Zap
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :zzz: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/zzz.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        ZZZ
                      </span>
                    </a>
                  </li>

                  <li class="border-b border-gray-800 pb-1 mt-3 font-semibold">
                    Objects
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :airplane: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/airplane.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Airplane
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :bomb: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/bomb.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Bomb
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :bulb: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/bulb.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Bulb
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :bus: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/bus.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Bus
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :blue_car: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/car.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Car
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :rocket: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/rocket.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Rocket
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :taxi: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/taxi.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Taxi
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :train: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/train.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Train
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :checkered_flag: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/checkered_flag.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Checkered Flag
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :banana: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/banana.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Banana
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :cake: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/cake.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Cake
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :beer: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/beer.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Beer
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :wine_glass: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/wine_glass.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Wine Glass
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :coffee: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/coffee.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Coffee
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :tea: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/tea.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Tea
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :cookie: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/cookie.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Cookie
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :eggplant: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/eggplant.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Eggplant
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :calendar: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/calendar.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Calendar
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :watch: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/watch.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Watch
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :hourglass: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/hourglass.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Hourglass
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :computer: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/computer.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Computer
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :headphones: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/headphones.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Headphones
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :microphone: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/microphone.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Microphone
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :violin: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/violin.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Violin
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :birthday: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/birthday.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Birthday
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :gift: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/gift.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Gift
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :santa: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/santa.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Santa
                      </span>
                    </a>
                  </li>

                  <li class="border-b border-gray-800 pb-1 mt-3 font-semibold">
                    Places
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :fi: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/finland.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Finland
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :jp: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/jp.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Japan
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :gb: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/uk.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        UK
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :us: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/us.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        USA
                      </span>
                    </a>
                  </li>

                  <li class="border-b border-gray-800 pb-1 mt-3 font-semibold">
                    Nature
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :cat: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/cat.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Cat
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :dog: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/dog.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Dog
                      </span>
                    </a>
                  </li>

                  <li class="my-1">
                    <a
                      href="#"
                      class="flex items-center"
                      data-action="markdown#select"
                      data-markdown="[SELECTION] :rainbow: "
                    >
                      <img
                        src="https://d1hfgy95btx02f.cloudfront.net/static/images/emojis/rainbow.png"
                        loading="lazy"
                        class="inline-block mr-2"
                        width="16"
                        height="16"
                      />
                      <span class="inline-block">
                        Rainbow
                      </span>
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <ul
              class="hidden typeahead-menu text-sm"
              data-target="typeahead.selector"
            ></ul>

            <textarea
              data-controller="autoresize"
              data-target="markdown.textarea typeahead.input"
              data-action="keyup->autoresize#resize keyup->typeahead#keyup keydown->typeahead#keydown keyup->markdown#togglePreviewTab"
              name="description"
              cols="40"
              rows="10"
              autocomplete="off"
              placeholder=""
              class="form-input markdownx-editor markdownx-editor"
              id="id_description"
              data-markdownx-editor-resizable=""
              data-markdownx-urls-path="/markdownx/markdownify/"
              data-markdownx-upload-urls-path="/markdownx/upload/"
              data-markdownx-latency="500"
              style="height: 256px; overflow-y: hidden; transition: opacity 1s ease 0s;"
              data-markdownx-init=""
            ></textarea>
            <p class="text-sm text-gray-700">
              You can use
              <a
                target="_blank"
                rel="nofollow"
                href="https://www.markdownguide.org/basic-syntax"
                >Markdown</a
              >
              to format your content.
            </p>
          </div>
          <div
            class="hidden markdownx-preview"
            data-target="tabs.pane"
            data-tab="preview"
          ></div>
          <div class="hidden" data-target="tabs.pane" data-tab="guide">
            <table
              class="table-fixed text-sm block whitespace-no-wrap overflow-x-scroll md:w-full md:whitespace-normal md:overflox-x-auto md:table"
            >
              <thead>
                <tr>
                  <th class="border px-4 py-2 text-left bg-gray-200">You type:</th>
                  <th class="border px-4 py-2 text-left bg-gray-200">You see:</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="border px-4 py-2"># Header</td>
                  <td class="border px-4 py-2">
                    <h1 class="text-2xl">Header (h1)</h1>
                  </td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">## Header</td>
                  <td class="border px-4 py-2">
                    <h2 class="text-xl">Header (h2)</h2>
                  </td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">### Header</td>
                  <td class="border px-4 py-2">
                    <h3 class="text-lg">Header (h3)</h3>
                  </td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">*Bold*</td>
                  <td class="border px-4 py-2"><strong>Bold</strong></td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">_Italic_</td>
                  <td class="border px-4 py-2"><em>Italic</em></td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">[Link text](http://example.com)</td>
                  <td class="border px-4 py-2"><a href="#">Link</a></td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">![alt](https://example.com)</td>
                  <td class="border px-4 py-2">
                    Image
                    <br />
                    <b
                      >Note: only safe images (starting with https://) will be shown.</b
                    >
                  </td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">@mention</td>
                  <td class="border px-4 py-2">
                    <a href="#">@mention</a> (link to profile)
                  </td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">#hashtag</td>
                  <td class="border px-4 py-2">
                    <a href="#">#hashtag</a> (link to hashtag)
                  </td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">`Code`</td>
                  <td class="border px-4 py-2"><code>Code</code></td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">&gt; Quote</td>
                  <td class="border px-4 py-2">
                    <blockquote>Quote</blockquote>
                  </td>
                </tr>
                <tr class="bg-gray-100">
                  <td class="border px-4 py-2">
                    * List item 1 <br />
                    * List item 2
                  </td>
                  <td class="border px-4 py-2">
                    <ul>
                      <li>List item 1</li>
                      <li>List item 2</li>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="border px-4 py-2">
                    1. List item 1 <br />
                    1. List item 2
                  </td>
                  <td class="border px-4 py-2">
                    <ol>
                      <li>List item 1</li>
                      <li>List item 2</li>
                    </ol>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="mt-4 py-2 text-sm flex flex-wrap items-center">
              <a
                class="inline-block mr-2"
                target="_blank"
                rel="nofollow"
                href="https://www.markdownguide.org/basic-syntax"
                >Markdown Guide</a
              >
              <a
                target="_blank"
                class="inline-block"
                rel="nofollow"
                href="https://gist.github.com/rxaviers/7360908"
                >More Emojis...</a
              >
            </div>
          </div>
        </div>
      </div>

      <div class="mb-3">
        <label class="flex flex-wrap items-center">
          <div class="inline-block mr-2">
            <input
              type="checkbox"
              name="allow_comments"
              id="id_allow_comments"
              checked=""
            />
          </div>
          <div class="inline-block font-semibold text-sm">
            Allow comments
          </div>
        </label>
      </div>

      <div class="flex text-center mt-2 pt-2 border-t">
        <button type="submit" name="submit" class="btn btn-primary mr-2">
          Publish
        </button>
        <button
          type="submit"
          name="save_private"
          value="true"
          class="btn btn-secondary"
        >
          Save Private
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { required, url } from 'vuelidate/lib/validators';

export default {
  data() {
    return {
      title: '',
      url: '',
    };
  },
  validations: {
    title: {
      required,
    },
    url: {
      url,
    },
  },
  methods: {
    submit() {
      this.$v.$touch();
      if (this.$v.$invalid) {
        window.scrollTo(0, 0);
      } else {
        console.log(this.$v.title.$model, this.title);
      }
    },
  },
};
</script>
