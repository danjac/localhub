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

> ./docker-compose up [-d]

To run Django management commands through docker:

> ./scripts/manage [...]

To run unit tests using pytest:

> ./scripts/runtests [...]

See pytest and pytest-django documentation for more information:

https://docs.pytest.org/en/stable/getting-started.html

https://pytest-django.readthedocs.io/en/latest/

### Deployment

Localhub is currently configured to deploy to Heroku. A PostgreSQL and Redis buildpack are required to run the Heroku instances. Production emails require Mailgun. Assets and user uploaded media share a single S3 bucket.

To set up Heroku containerized deployment:

> heroku stack:set container

Assuming "localhub" is the name of your Heroku instance:

> heroku git:remote -a localhub

Next, copy .env.example to .env and add your AWS, Heroku, and other secret keys.

To deploy master branch to Heroku and S3:

> ./scripts/deploy
