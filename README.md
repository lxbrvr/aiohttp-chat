## Description

The simple chat backend based on python3.7 and aiohttp.

## Requirements

* docker
* docker-compose

## Run

Run `make dev` command from the root directory.

## Commands

Commands can be run from the root of the directory.

| command | description |
| ------------ | ------------ |
| make dev | Runs the development server on http://0.0.0.0:8000. |
| make clean_db | Cleans the database. |
| make populate_db | Populates the database with fake data. |

## OpenAPI

The OpenAPI specification is available at http://0.0.0.0:8001