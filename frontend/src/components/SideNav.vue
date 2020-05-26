<template>
  <nav class="hidden lg:block text-sm w-full lg:w-1/6">
    <button class="btn btn-block lg:hidden mb-3 text-base">
      Close Menu
    </button>

    <ul class="sidebar-menu">
      <li class="mb-1">
        <a href="/" class="sidebar-menu-item">Activity Stream</a>
      </li>
      <li class="mb-1">
        <a href="/messages/inbox/" class="sidebar-menu-item">
          <span>Messages</span>
        </a>
      </li>
      <li class="mb-1">
        <a href="/notifications/" class="sidebar-menu-item">
          <span>Notifications</span>
        </a>
      </li>
      <li class="mb-1">
        <a href="/comments/" class="sidebar-menu-item">Comments</a>
      </li>
      <li class="mb-1">
        <a href="/private/" class="sidebar-menu-item">Private Stash</a>
      </li>
      <li class="mb-1">
        <a href="/bookmarks/" class="sidebar-menu-item">Bookmarks</a>
      </li>
      <li class="mb-1">
        <a href="/photos/gallery/" class="sidebar-menu-item">Gallery</a>
      </li>
      <li class="mb-1">
        <a href="/events/calendar/" class="sidebar-menu-item">Calendar</a>
      </li>
      <li class="mb-1 md:mb-0">
        <a href="/account/~update" class="sidebar-menu-item">Settings</a>
      </li>
      <li class="mb-1 md:hidden">
        <a href="/account/logout/" class="sidebar-menu-item">Logout</a>
      </li>
    </ul>

    <ul class="sidebar-menu mt-4">
      <li class="sidebar-menu-header mb-3">Actions</li>

      <li class="mb-1">
        <a href="/posts/~create" class="sidebar-menu-item">Submit Post</a>
      </li>
      <li class="mb-1">
        <a href="/events/~create" class="sidebar-menu-item">Submit Event</a>
      </li>
      <li class="mb-1">
        <a href="/photos/~create" class="sidebar-menu-item">Submit Photo</a>
      </li>
      <li class="mb-1">
        <a href="/polls/~create" class="sidebar-menu-item">Submit Poll</a>
      </li>

      <li>
        <a href="/messages/send/" class="sidebar-menu-item">Send Message</a>
      </li>
    </ul>

    <ul class="sidebar-menu mt-4">
      <li class="sidebar-menu-header mb-3">Content</li>
      <li class="mb-1">
        <a class="sidebar-menu-item" href="/tags/">
          Tags
        </a>
      </li>
      <li class="mb-1">
        <a class="sidebar-menu-item" href="/timeline/">Timeline </a>
      </li>
      <li class="mb-1">
        <a class="sidebar-menu-item" href="/favorites/">
          Favorites
        </a>
      </li>
      <li class="mb-1">
        <a class="sidebar-menu-item" href="/people/danjac/likes/">Likes </a>
      </li>
      <li class="mb-1">
        <a
          data-controller="active-link"
          class="sidebar-menu-item"
          href="/people/danjac/mentions/"
          >Mentions
        </a>
      </li>
    </ul>

    <ul class="sidebar-menu mt-4">
      <li class="sidebar-menu-header mb-3">People</li>
      <li class="mb-1">
        <a href="/people/members/" class="sidebar-menu-item">Members</a>
      </li>
      <li class="mb-1">
        <a href="/people/following/" class="sidebar-menu-item">Following</a>
      </li>
      <li class="mb-1">
        <a href="/people/followers/" class="sidebar-menu-item">Followers</a>
      </li>
      <li class="mb-1">
        <a href="/people/blocked/" class="sidebar-menu-item">Blocked</a>
      </li>
    </ul>

    <ul class="sidebar-menu mt-4">
      <li class="sidebar-menu-header mb-3">Community</li>

      <li class="mb-1">
        <a href="/community/about/" class="sidebar-menu-item">
          About Kotiseutu
        </a>
      </li>

      <li class="mb-1">
        <a href="/community/~update/" class="sidebar-menu-item">Settings</a>
      </li>

      <li class="mb-1">
        <a href="/community/memberships/" class="sidebar-menu-item">Members</a>
      </li>

      <li class="mb-1">
        <a href="/invites/" class="sidebar-menu-item">Invites</a>
      </li>

      <li class="mb-1">
        <a href="/join-requests/" class="sidebar-menu-item">
          <span>Join Requests</span>
        </a>
      </li>

      <li>
        <a href="/communities/" class="sidebar-menu-item">
          <span>Communities</span>
        </a>
      </li>
    </ul>
  </nav>
</template>
