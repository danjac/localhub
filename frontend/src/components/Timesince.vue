<template>
  <div class="flex items-center">
    <chip :user="user" />
    <div class="inline-block text-sm text-muted">{{ action }} {{ timeAgo }} ago</div>
  </div>
</template>

<script>
import { parseISO, formatDistanceToNow } from 'date-fns';
import Chip from '@/components/users/Chip';

export default {
  name: 'Timesince',
  components: {
    Chip,
  },
  props: {
    timestamp: {
      type: String,
      required: true,
    },
    user: {
      type: Object,
      required: true,
    },
    action: {
      type: String,
      default: '',
    },
  },
  computed: {
    timeAgo() {
      return formatDistanceToNow(parseISO(this.timestamp));
    },
  },
};
</script>
