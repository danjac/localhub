### Concept

Open source, small footprint social network platform.

### Tech

Python/Django, Docker, PostgreSQL, Turbolinks, Stimulus, Tailwind.

### License

Localhub is licensed under the **GNU Affero Public License**. A copy of the license is provided in this repository.

### Credits

Favicon: https://www.iconfinder.com/3ab2ou (Creative Commons Attribution)

### Development

You should have docker and docker-compose installed on your development machine.

> ./docker-compose up [-d]

To run Django management commands through docker:

> ./scripts/manage [...]

To run unit tests:

> ./scripts/runtests [...]

### Deployment

Localhub is currently configured to deploy to Heroku. A PostgreSQL and Redis buildpack are required to run the Heroku instances. Production emails require Mailgun. Assets and user uploaded media share a single S3 bucket.

To set up Heroku containerized deployment:

> heroku stack:set container

Assuming "localhub" is the name of your Heroku instance:

> heroku git:remote -a localhub

Next, copy .env.example to .env and add your AWS, Heroku, and other secret keys.

To deploy master branch to Heroku and S3:

> ./scripts/deploy
