<template>
  <div>
    login goes here
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      invalidLogin: false,
    };
  },
  methods: {
    async authenticate() {
      this.invalidLogin = false;
      const data = new URLSearchParams();
      data.append('login', this.username);
      data.append('password', this.password);
      try {
        const response = await axios({
          data,
          url: '/api/auth/login/',
          method: 'POST',
        });
        if (response.status === 200) {
          window.location.href = '/';
        } else if (response.status === 400) {
          this.invalidLogin = true;
        }
      } catch (e) {
        this.invalidLogin = true;
      }
    },
  },
};
</script>
