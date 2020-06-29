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

This script should (re)build your docker environment as needed and start up the containers in a detached mode:

> ./scripts/start-docker

To run Django commands through docker:

> ./scripts/manage [command...]

To run unit tests:

> ./scripts/runtests [options...]

### Deployment

Localhub is currently configured to deploy to Heroku. A PostgreSQL and Redis buildpack are required to run the Heroku instances. Production emails require Mailgun. Assets and user uploaded media share a single S3 bucket.

A Gitlab CI/CD configuration is provided, which assumes a long-running "release" branch. To deploy, just merge from your master branch into release and push. The pipeline takes care of assets deployment and tests.

Pull requests are welcome for other deployment and production environments.
