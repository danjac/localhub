<template>
  <div class="home">
    <LoadingBar v-if="loading" />
    <ActivityList :activities="pageObj.results" @delete="fetchFirstPage" />
    <Pagination
      :next="pageObj.next"
      :previous="pageObj.previous"
      @nextPage="nextPage"
      @previousPage="previousPage"
    />
  </div>
</template>

<script>
import axios from 'axios';

import ActivityList from '@/components/activities/ActivityList';
import LoadingBar from '@/components/LoadingBar';
import Pagination from '@/components/Pagination';

export default {
  name: 'Home',
  components: {
    ActivityList,
    LoadingBar,
    Pagination,
  },
  data() {
    return {
      loading: false,
      error: false,
      loadingState: 0,
      pageObj: {
        results: [],
        next: null,
        prev: null,
      },
    };
  },
  created() {
    this.fetchFirstPage();
  },
  methods: {
    fetchFirstPage() {
      this.fetchPage('/api/streams/default/');
    },
    nextPage() {
      this.fetchPage(this.pageObj.next);
    },
    previousPage() {
      this.fetchPage(this.pageObj.previous);
    },
    async fetchPage(url) {
      if (!url) {
        return;
      }
      this.loading = true;
      this.error = false;
      this.pageObj = {
        results: [],
        next: null,
        previous: null,
      };
      window.scrollTo(0, 0);
      try {
        const response = await axios.get(url);
        this.pageObj = response.data;
      } catch (e) {
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
