<template>
  <div>
    <nav-bar />
    <div class="columns">
      <!-- sidebar would be slot, passed in as component prop -->
      <div class="column col-3 col-lg-12 hide-lg bg-gray p-2">
        <div class="show-lg hide-xl mb-2">
          <a href="#" class="btn btn-sm btn-link btn-block">Close Sidebar</a>
        </div>
        <ul class="menu">
          <li class="menu-item">
            <a
              data-controller="active-link"
              data-active-link-exact=""
              href="/"
              class="active"
              >Home
            </a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/notifications/">
              <span>
                Notifications
              </span>
            </a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/messages/">
              <span>
                Direct Messages
              </span>
            </a>
          </li>
        </ul>

        <ul class="menu mt-2">
          <li class="divider" data-content="Actions"></li>

          <li class="menu-item">
            <a data-controller="active-link" href="/posts/~create"
              >Submit Post</a
            >
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/events/~create"
              >Submit Event</a
            >
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/photos/~create"
              >Submit Photo</a
            >
          </li>
        </ul>

        <ul class="menu mt-2">
          <li class="divider" data-content="People"></li>
          <li class="menu-item">
            <a data-controller="active-link" href="/people/danjac/"
              >My Profile</a
            >
          </li>
          <li class="menu-item">
            <a
              data-controller="active-link"
              data-active-link-exact=""
              href="/people/"
              >Members</a
            >
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/following/users/">
              Following
            </a>
          </li>
        </ul>

        <ul class="menu mt-2">
          <li class="divider" data-content="Activity"></li>
          <li class="menu-item">
            <a data-controller="active-link" href="/likes/">
              Favorites
            </a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/following/tags/">
              Tags
            </a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/posts/">Posts</a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/events/">Events</a>
          </li>
          <li class="menu-item">
            <a data-controller="active-link" href="/photos/">Photos</a>
          </li>
        </ul>

        <ul class="menu mt-2">
          <li class="divider" data-content="Settings"></li>
          <li class="menu-item"><a href="/account/~update">My Settings</a></li>

          <li class="menu-item">
            <a href="/community/~update/">Community Settings</a>
          </li>
        </ul>
        <div class="panel mt-2 p-1">
          <div class="panel-header">
            <div class="panel-title">
              About LocalHub
            </div>
          </div>
          <div class="panel-body">
            <p></p>
            <p>
              Demo site for
              <a href="https://gitlab.com/danjac/localhub/">LocalHub</a>
            </p>
            <p></p>
            <a href="/community/">More Details</a>
          </div>
        </div>
      </div>
      <div class="column col-9 col-lg-12" data-target="sidebar.main">
        <div class="show-lg hide-xl float-right mb-2">
          <a href="#" class="btn btn-sm btn-link" data-action="sidebar#toggle">
            <span>
              Sidebar
            </span>
          </a>
        </div>
        <div class="clearfix"></div>
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
// tbd: change name of component: maybe SiteHeader and SiteFooter?
import NavBar from '@/components/NavBar';
export default {
  components: {
    NavBar
  }
};
</script>
