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
      v-if="object.has_bookmarked"
      @click.prevent="removeBookmark"
      >Bookmark</a
    >
    <a
      class="dropdown-menu-item"
      v-if="!object.has_bookmarked"
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
import axios from 'axios';
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
      this.object.is_pinned = true;
      axios.post(this.object.endpoints.pin);
      this.$store.dispatch('addMessage', {
        message: 'This item has been pinned to the top of the activity stream',
        tags: 'message-success',
      });
    },
    unpin() {
      this.object.is_pinned = false;
      axios.delete(this.object.endpoints.unpin);
      this.$store.dispatch('addMessage', {
        message: 'This item has been removed from the top of the activity stream',
        tags: 'message-success',
      });
    },
    async addBookmark() {
      try {
        await axios.post(this.object.endpoints.add_bookmark);
        this.successMessage('This item has been added to your bookmarks');
        this.object.has_bookmarked = true;
      } catch (e) {
        this.serverErrorMessage(e);
      }
    },
    async removeBookmark() {
      try {
        await axios.delete(this.object.endpoints.remove_bookmark);
        this.successMessage('This item has been removed from your bookmarks');
        this.object.has_bookmarked = false;
      } catch (e) {
        this.serverErrorMessage(e);
      }
    },
    like() {
      this.object.has_liked = true;
      axios.post(this.object.endpoints.like);
      this.$store.dispatch('addMessage', {
        message: 'You have liked this item',
        tags: 'message-success',
      });
    },
    dislike() {
      this.object.has_liked = false;
      axios.post(this.object.endpoints.dislike);
      this.$store.dispatch('addMessage', {
        message: 'You no longer like this item',
        tags: 'message-success',
      });
    },
    successMessage(message) {
      this.$store.dispatch('addMessage', {
        message,
        tags: 'message-success',
      });
    },
    serverErrorMessage(err) {
      this.$store.dispatch('addMessage', {
        message: 'Sorry, an error occurred: ' + err.response.status,
        tags: 'message-error',
      });
    },
  },
};
</script>
