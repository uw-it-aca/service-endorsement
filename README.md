# Service Endorsement

A web application enabling UW employees to provision non-employees to selected UW-IT services.

[![Build Status](https://github.com/uw-it-aca/service-endorsement/workflows/Build%2C%20Test%20and%20Deploy/badge.svg?branch=main)](https://github.com/uw-it-aca/service-endorsement/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/service-endorsement/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/service-endorsement?branch=main)

# Testing

Use [this ENDORSEMENT_PROVISIONING setting](https://github.com/uw-it-aca/service-endorsement/blob/b8fba8df7ef2280421d7481d847e9c6693130c05/docker/test-values.yml#L115) to control what is visible on test.provision

# Installation and Evaluation

After cloning, with docker and docker-compose installed, evaluation should be a simple matter of running `docker-compose up --build` from the repository's root directory to start the app locally on port 8080.

If you get `devtools    | Watchpack Error (watcher): Error: EMFILE: too many open files, watch ...` you might resolve it by [increasing your open file limit](https://stackoverflow.com/a/75308695/1943429).
