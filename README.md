Description
-----------

Communikit is short for Community Toolkit. It is an experimental project aiming to provide secure, localized, private social media for small to medium sized communities. This is of particular interest to people who don't like big, centralized private-data sucking entities such as Twitter or Facebook.


What about the Fediverse/Activity Pub/etc?
------------------------------------------

At the moment each Communikit instance is isolated on each server/database instance. This is absolutely fine for a single community where people just want to hang out in a small group, or if we want to host a "neighbourhood" of friendly communities. However it's not so good if the ambition is to take part in the larger universe of open communities with solutions such as Mastodon or Diaspora.

Future versions of Communikit will likely include optional means to join via various open protocols such as Activity Pub, so that communities - if they so wish - can take part in the larger Fediverse. Right now our focus is on making tools for small, friendly communities who just want to do their own thing apart from the greater Internet (or "isolated echo chambers", if you wish).

We will also be investigating different ways to interact with Communikit instances through an API.

Technology
----------

Communikit is built with Python, Django and PostgreSQL. These are solid "boring" open source technologies that are easy to work with and have large, vibrant communities. Rather than use a Single Page Application (SPA) approach with a JavaScript-heavy front end, we've used the Turbolinks library with the lightweight Stimulus framework to provide much of the benefits of an SPA such as quick page loading and interactivity, while keeping much of the advantages of a traditional server-side rendered application, such as a smaller code base, a more robust and accessible user interface, and better search engine discoverability.

Installation
------------

Development installation requires Docker and Docker-Compose. Assuming both are installed and running you should be able to just do:


`docker-compose up -d --build`


Deployment
----------

__Please note that Communikit is in the early development stage and should not be trusted to run in a serious production environment.__

At present, Communikit is optimized to deploy to Heroku, although we hope to provide more options later. A _heroku.yml_ file is provided along with Docker configuration to get started. You will have to set the following environment variables in your Heroku account:

- DATABASE_URL
- REDIS_URL
- DJANGO_SECRET_KEY
- DJANGO_EMAIL_HOST
- DJANGO_EMAIL_PORT
- DJANGO_ALLOWED_HOSTS _(Set your domain)_

In addition the production instance requires AWS/S3: add the following settings to point to your account:

- DJANGO_AWS_ACCESS_KEY_ID
- DJANGO_AWS_SECRET_ACCESS_KEY
- DJANGO_AWS_STORAGE_BUCKET_NAME

Finally for email we use Mailgun, which requires these settings:

- DJANGO_MAILGUN_API_KEY
- DJANGO_MAILGUN_SENDER_DOMAIN

Again, we hope to improve the production deployment situation to remove any hard dependencies on third parties such as Heroku, Mailgun or AWS.

Licensing
---------

This project is open source and licensed under AGPL.
