# Concept

Open source, small footprint social network platform.

# Tech

Python/Django, Docker, PostgreSQL, Turbolinks, Stimulus, Tailwind.

# License

Localhub is licensed under the **GNU Affero Public License**. A copy of the license is provided in this repository.

# Credits

Favicon: https://www.iconfinder.com/3ab2ou (Creative Commons Attribution)

# Development

You should have docker and docker-compose installed on your development machine.

This script should (re)build your docker environment as needed and start up the containers in a detached mode:

> ./scripts/start-docker

To run Django commands through docker:

> ./scripts/manage [command...]

To run unit tests:

> ./scripts/runtests [options...]

# Deployment

TBD
