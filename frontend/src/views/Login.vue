<template>
  <div>
    <h1 class="page-header mb-3">Login</h1>
    <div class="markdown-content leading-normal text-base">
      <p>A private family group.</p>
    </div>

    <p class="mb-3">
      If you have not created an account yet, then please
      <a href="/account/signup/">sign up</a> first.
    </p>

    <form
      @submit.prevent="submit"
      class="p-1 md:p-3 border border-gray-500"
      :disabled="submitting"
    >
      <div
        v-for="(error, counter) in errors"
        :key="counter"
        class="notification bg-red-800 mb-2"
      >
        {{ error }}
      </div>

      <div class="mb-3">
        <label for="login" class="block font-semibold mb-3 text-sm">Login</label>

        <input
          type="text"
          name="login"
          placeholder="Username or e-mail"
          autofocus="autofocus"
          class="form-input"
          id="login"
          v-model="login"
          required
        />
      </div>

      <div class="mb-3">
        <label for="password" class="block font-semibold mb-3 text-sm">Password</label>

        <input
          type="password"
          name="password"
          placeholder="Password"
          class="form-input"
          id="password"
          v-model="password"
          required
        />
      </div>

      <div class="mb-3">
        <label class="flex flex-wrap items-center">
          <div class="inline-block mr-2">
            <input type="checkbox" name="remember" v-model="remember" />
          </div>
          <div class="inline-block font-semibold text-sm">
            Remember Me
          </div>
        </label>
      </div>

      <div class="flex text-center mt-2 pt-2 border-t">
        <button class="btn btn-primary" type="submit">Sign in</button>
        <a class="btn btn-link" href="#">Forgot your password?</a>
      </div>
    </form>

    <p class="mt-3">
      Login or signup through
      <a href="#">Google</a>
    </p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      login: '',
      password: '',
      remember: false,
      errors: [],
      submitting: false,
    };
  },
  methods: {
    async submit() {
      this.errors = [];
      this.submitting = true;

      const data = new URLSearchParams();

      data.append('login', this.login);
      data.append('password', this.password);
      data.append('remember', this.remember);

      try {
        const response = await axios({
          data,
          url: '/auth/login/',
          method: 'POST',
        });
        if (response.status === 200) {
          window.location.href = '/';
        }
      } catch (e) {
        if (e.response && e.response.data.form.errors) {
          this.errors = e.response.data.form.errors;
        }
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>
