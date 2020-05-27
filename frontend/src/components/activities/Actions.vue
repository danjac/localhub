<template>
  <div>
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

      <a
        class="dropdown-menu-item"
        v-if="isOwner || isModerator"
        @click.prevent="$refs.deleteConfirm.open()"
        >Delete</a
      >

      <a
        class="dropdown-menu-item line-through"
        v-if="object.has_liked && !isOwner"
        @click.prevent="dislike"
        >Like</a
      >
      <a
        class="dropdown-menu-item"
        v-if="!object.has_liked && !isOwner"
        @click.prevent="like"
        >Like</a
      >
      <slot />
    </Dropdown>
    <ConfirmDialog ref="deleteConfirm" @confirm="handleDelete" header="Delete">
      Are you sure you want to delete this item?
    </ConfirmDialog>
  </div>
</template>

<script>
import axios from 'axios';

import ConfirmDialog from '@/components/ConfirmDialog';
import Dropdown from '@/components/Dropdown';

export default {
  components: {
    Dropdown,
    ConfirmDialog,
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
    async like() {
      try {
        await axios.post(this.object.endpoints.like);
        this.successMessage('You have liked this item');
        this.object.has_liked = true;
      } catch (e) {
        this.serverErrorMessage(e);
      }
    },
    async dislike() {
      try {
        await axios.delete(this.object.endpoints.dislike);
        this.successMessage('You have stopped liking this item');
        this.object.has_liked = false;
      } catch (e) {
        this.serverErrorMessage(e);
      }
    },
    async handleDelete() {
      try {
        await axios.delete(this.object.endpoints.base);
        this.$emit('delete');
        this.successMessage('This item has been deleted');
      } catch (e) {
        this.serverErrorMessage(e);
      }
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
