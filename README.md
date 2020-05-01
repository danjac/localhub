# Name

_Big Friendly Group_. Or _Big Friendly Giant_ or the [BFG](https://en.wikipedia.org/wiki/BFG_%28weapon%29) of Doom lore, if you prefer. I just needed a nice, short distinctive package name. The full name of the project is **Social-BFG**. The old name of the project was _Localhub_.

# Concept

What BFG is **not**: a Facebook killer, Twitter killer or any other [insert global social network here] killer. That would be clearly tilting at windmills and, in 2020, a waste of time and effort.

# Architecture

BFG is a traditional Django/Python web application. It uses server-rendered pages rather than Rest Framework talking to a React/Vue/Angular frontend. That said, it does include a fair amount of JavaScript mostly based on Turbolinks and the Stimulus framework (borrowed from Rails) and uses Webpack as part of the assets development and deployment process.

The architecture is based on the Web Pyramid: there is JS, but it rests on a bedrock of standard HTML delivered down the pipe. While there are no guarantees of 100% functionality on a browser with JS disabled (or an old browser) a BFG site should still load and be largely accessible. If you are running on a modern browser, with JS enabled, Turbolinks and a few tricks here and there give the impression of a Single Page Application. In fact, pages are loaded from the server and dynamically diffed and inserted into the DOM through Turbolinks. Stimulus provides more discrete client actions. Think of it as a poor man's SPA.

# Deployment

The current out of the box and tested production environment is aimed at Heroku. That is more due to personal experience and time constraints than anything else, and ideally in future we would want to support as many deployment platforms as possible. That said this is a standard 12-factor WSGI application that should run on any standard server platform with some tweaks and adjustments. Pull requests are welcome for things like Docker configurations if you can get this running on a Digital Ocean or other cloud provider.

This project also includes a Gitlab CI configuration, so if you are deploying to Heroku through Gitlab, you should be golden. There are a number of environment varibles you need to set up.
