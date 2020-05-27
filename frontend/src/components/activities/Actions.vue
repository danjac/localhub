<template>
  <Dropdown label="Actions...">
    <a class="dropdown-menu-item" href="#">Comment</a>

    <a
      class="dropdown-menu-item line-through"
      v-if="isModerator && object.is_pinned"
      @click.prevent="unpin"
      >Pin</a
    >
    <a
      class="dropdown-menu-item"
      v-if="isModerator && !object.is_pinned"
      @click.prevent="pin"
      >Pin</a
    >

    <a
      class="dropdown-menu-item line-through"
      v-if="object.hasBookmarked"
      @click.prevent="removeBookmark"
      >Bookmark</a
    >
    <a
      class="dropdown-menu-item"
      v-if="!object.hasBookmarked"
      @click.prevent="addBookmark"
      >Bookmark</a
    >

    <a class="dropdown-menu-item" v-if="isOwner">Edit</a>

    <a class="dropdown-menu-item" v-if="isOwner || isModerator">Delete</a>

    <a
      class="dropdown-menu-item line-through"
      v-if="object.hasLiked && !isOwner"
      @click.prevent="dislike"
      >Like</a
    >
    <a
      class="dropdown-menu-item"
      v-if="!object.hasLiked && !isOwner"
      @click.prevent="Like"
      >Like</a
    >
    <slot />
  </Dropdown>
</template>

<script>
import Dropdown from '@/components/Dropdown';

export default {
  components: {
    Dropdown,
  },
  props: {
    object: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isOwner() {
      return this.object.owner.id === this.$store.state.user.id;
    },
    isModerator() {
      return this.$store.getters.isModerator;
    },
  },
  methods: {
    pin() {
      // ajax action, toast etc
      this.object.is_pinned = true;
    },
    unpin() {
      this.object.is_pinned = false;
    },
    addBookmark() {
      this.object.has_bookmarked = true;
    },
    removeBookmark() {
      this.object.has_bookmarked = false;
    },
    like() {
      this.object.has_liked = true;
    },
    dislike() {
      this.object.has_liked = false;
    },
  },
};
</script>
