## Description

LocalHub is an experimental project aiming to provide secure, localized, private social media for small to medium sized communities. This is of particular interest to people who don't like big, centralized private-data sucking entities such as Twitter or Facebook.

The premise of LocalHub is to create and foster small communities of no greater size than [Dunbar's Number](https://en.m.wikipedia.org/wiki/Dunbar%27s_number) : ""the number of people you would not feel embarrassed about joining uninvited for a drink if you happened to bump into them in a bar". This is the number a community might be comfortably moderated and managed, beyond which you run into the common issues of larger communities such as the Eternal September.

A user may belong to a number of communities under the same domain/host, but the communities themselves are isolated - content you post in one community does not appear in a another; messages you post to a friend inside a community will not "leak" outside that community. A community may allow its content to be public, if the admins so decide, but all communities are invite-only.

## What about the Fediverse/Activity Pub/etc?

At the moment each LocalHub instance is isolated on each server/database instance. This is absolutely fine for a single community where people just want to hang out in a small group, or if we want to host a "neighbourhood" of friendly communities. However it's not so good if the ambition is to take part in the larger universe of open communities with solutions such as Mastodon or Diaspora.

Future versions of LocalHub will likely include optional means to join via various open protocols such as Activity Pub, so that communities - if they so wish - can take part in the larger Fediverse. Right now our focus is on making tools for small, friendly communities who just want to do their own thing apart from the greater Internet (or "isolated echo chambers", if you wish).

We will also be investigating different ways to interact with LocalHub instances through an API.

## Technology

LocalHub is built with Python, Django and PostgreSQL. These are solid "boring" open source technologies that are easy to work with and have large, vibrant communities. Rather than use a Single Page Application (SPA) approach with a JavaScript-heavy front end, we've used the [Turbolinks](https://github.com/turbolinks/turbolinks) library with the lightweight [Stimulus framework](https://stimulusjs.org/) to provide much of the benefits of an SPA such as quick page loading and interactivity, while keeping much of the advantages of a traditional server-side rendered application, such as a smaller code base, a more robust and accessible user interface, and better search engine discoverability.

## Installation

Development installation requires Docker and Docker-Compose. Assuming both are installed and running you should be able to just do:

`docker-compose up -d --build`

## Running tests

`docker-compose exec django pytest`

## Deployment

**Please note that LocalHub is in the early development stage and should not be trusted to run in a serious production environment. Breaking changes will happen until a stable release is officially available.**

At present, LocalHub is optimized to deploy to Heroku, although we hope to provide more options later. A _heroku.yml_ file is provided along with Docker configuration to get started. You will have to set the following environment variables in your Heroku account:

- DATABASE_URL
- REDIS_URL
- DJANGO_SECRET_KEY
- DJANGO_EMAIL_HOST
- DJANGO_EMAIL_PORT
- DJANGO*ALLOWED_HOSTS *(Set your domain)\_

In addition the production instance requires AWS/S3: add the following settings to point to your account:

- DJANGO_AWS_ACCESS_KEY_ID
- DJANGO_AWS_SECRET_ACCESS_KEY
- DJANGO_AWS_STORAGE_BUCKET_NAME

If you are using a Cloudfront or other CDN, set **DJANGO_AWS_CUSTOM_DOMAIN** accordingly e.g. _12345abc.cloudfront.net_.

Finally for email we use Mailgun, which requires these settings:

- DJANGO_MAILGUN_API_KEY
- DJANGO_MAILGUN_SENDER_DOMAIN

Again, we hope to improve the production deployment situation to remove any hard dependencies on third parties such as Heroku, Mailgun or AWS.

## Inspiration

Inspiration came from [Mastodon](https://mastodon.social), [Diaspora\*](https://joindiaspora.com) and other projects exploring the decentralized social media space. The design and architecture was heavily influenced by [Tildes](https://tildes.net).

## Demo

A live demo is available at https://demo.localhub.social. Use the username **demo** password **testpass1** to log in.

## Licensing

This project is open source and licensed under AGPL.
