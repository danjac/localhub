<template>
  <div class="home">
    <LoadingBar v-if="loading" />
    {{ pageObj }}
  </div>
</template>

<script>
import axios from 'axios';
import LoadingBar from '@/components/LoadingBar.vue';

export default {
  name: 'Home',
  components: {
    LoadingBar,
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
  async created() {
    this.loading = true;
    this.error = false;
    try {
      const response = await axios.get('/api/streams/default/');
      this.pageObj = response.data;
    } catch (e) {
      this.error = true;
    } finally {
      this.loading = false;
    }
  },
};
</script>
