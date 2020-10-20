### Concept

Open source, small footprint social network platform.

### Tech

Python/Django, Docker, PostgreSQL, Redis, Turbolinks, Stimulus, Tailwind.

The architecture and philosophy of the design and implementation are based on the idea of the "web pyramid" outlined for example here: https://docs.tildes.net/philosophy/site-implementation. While Javascript is required for some interactive functionality and a better subjective performance, the site is rendered in plain HTML enhanced with JS and CSS. Turbolinks provides smoother navigation without full page reloads and Stimulus adds discrete Javascript enhancement to the markup without requiring the cognitive and performance load of a full Single Page Application.

### License

Localhub is licensed under the **GNU Affero Public License**. A copy of the license is provided in this repository.

### Credits

Favicon: https://www.iconfinder.com/3ab2ou (Creative Commons Attribution)

### Development

You should have docker and docker-compose installed on your development machine.

Copy the file **.env.sample** to **.env** and edit the values as needed.

To start up the development environment:

> ./docker-compose up [-d]

You should be able to see the site on http://localhost in your browser.

To run Django management commands through docker:

> ./scripts/manage [...]

When starting a new environment you should create a default community. First create a superuser:

> ./scripts/manage createsuperuser

You can then create a new community in the Django admin, or use the command line:

> ./scripts/manage createcommunity localhost MyCommunityName --admin=username

"username" here can be the superuser, a user you have registered in the sign up page, or one you have created in the Django admin. In general it's best to only create a superuser for Django admin access and create a separate user for community management.

To run unit tests using pytest:

> ./scripts/runtests [...]

See pytest and pytest-django documentation for more information:

https://docs.pytest.org/en/stable/getting-started.html

https://pytest-django.readthedocs.io/en/latest/

### Deployment

Localhub is currently configured to deploy to Heroku. A PostgreSQL and Redis buildpack are required to run the Heroku instances. Production emails require Mailgun. Assets and user uploaded media share a single S3 bucket.

You will need to add a number of environment variables in your Heroku dashboard settings panel:

- ADMINS: comma separated in form _my full name <name@mysite.com>,other name <othername@mysite.com>_
- ADMIN_URL: should be something other than "admin/". Must end in forward slash.
- ALLOWED*HOSTS: enter the wildcard domain e.g. \_mysite.com*
- AWS_STORAGE_BUCKET_NAME: see your S3 settings
- AWS_ACCESS_KEY_ID: see your S3 settings
- AWS_S3_CUSTOM_DOMAIN: your cloudfront domain
- CSRF*COOKIE_NAME: should be same as your domain, preceded by "." e.g. *.mysite.com\_
- CSRF_TRUSTED_ORIGINS: should be same as CSRF_COOKIE_NAME
- SESSION_COOKIE_DOMAIN: e.g. \_mysite.com\*
- DATABASE_URL: provided by Heroku PostgreSQL buildpack
- DISABLE_COLLECTSTATIC: set to "1"
- DJANGO_SETTINGS_MODULE: should always be \_localhub.config.settings.heroku\*
- MAILGUN_API_KEY: see your Mailgun settings
- MAILGUN_SENDER_DOMAIN: see your Mailgun settings
- REDIS_URL: provided by Heroku Redis buildpack
- SECRET_KEY: Django secret key. Use e.g. https://miniwebtool.com/django-secret-key-generator/ to create new key.
- VAPID_ADMIN_EMAIL: Your email address
- VAPID_PRIVATE_KEY: See https://d3v.one/vapid-key-generator/
- VAPID_PUBLIC_KEY: See https://d3v.one/vapid-key-generator/
- WEBPUSH_ENABLED: set to "yes" to enable webpush notifications on the site, "no" to disable

To set up Heroku containerized deployment:

> heroku stack:set container

Assuming "localhub" is the name of your Heroku instance:

> heroku git:remote -a localhub

Next, copy .env.example to .env and add your AWS, Heroku, and other secret keys.

To deploy master branch to Heroku and S3:

> ./scripts/deploy

Note that your local .env AWS settings should be the same as in production, so that the deployment script can push static assets to the same S3 bucket.
