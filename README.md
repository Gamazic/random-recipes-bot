# RandomRecipesBot

![Build](https://github.com/Gamazic/random-recipes-bot/actions/workflows/aws.yml/badge.svg?branch=master)

Initially, the bot was created by me for personal purposes. When I didn't know what to cook, I took a random recipe from notes. Then I decided to make this bot for these purposes. But you can use it as a bag in which you can put any items and endlessly pull out recipes without repeating.

## Bot link

https://t.me/RandomRecipesBot

## Preview

![Preview](tg_app_screenshots/random-recipes-bot-alpha-v0.1.jpg)

# About project

## How to manual start localy

### Requirements

* `Python 3.9`
* `poetry`
* `.env` file with following variables:
    ```
    MONGO_ROOT_PASSWORD
    MONGO_ROOT_USERNAME
    MONGO_USER
    MONGO_PASSWORD
    MONGO_HOST
    MONGO_PORT
    MONGO_RECIPE_DB
    TG_TOKEN
    WEBHOOK_HOST
    WEBHOOK_PATH
    WEBHOOK_PORT
    WEBAPP_HOST
    WEBAPP_PORT
    ```

### Install dependencies

To install all dependencies use command:
```bash
poetry install -n
```
You can learn more about `poetry` here:
* Russian [^1]
* English [^2]

To install without dev dependenices (for run project only) use next command:
```bash
poetry install -n --no-dev
```

### Run app with polling

```python
python server.py -e polling
```

### Run tests
```python
pytest -v
```
Testing can be run only with dev dependecies

## Start localy via docker-compose
At first you need to install `docker-compose`.
How to do this you can read here:
* Russian [^3], [^4].
* English [^5], [^6].

After installing `docker-compose` you need to run the following command:
```bash
docker-compose up -d
```

# Useful links

* Гайд по `github actions`: https://youtu.be/Yg5rpke79X4
* Гайд как запустить контейнер на `AWS EC2` через `cli` на сервере: https://github.com/gavrilka/TelegramBot
* Deploy `docker-compose` on `AWS ECS EC2`: https://dev.to/raphaelmansuy/10-minutes-to-deploy-a-docker-compose-stack-on-aws-illustrated-with-hasura-and-postgres-3f6e

# References

* [^1]: Обзор `poetry` от Диджитализируй!: https://youtu.be/KOC0Gbo_0HY
* [^2]: `poetry` official documentation: https://python-poetry.org/docs/
* [^3]: Установка `Docker` для `Ubuntu 18.04`: https://www.digitalocean.com/community/tutorials/docker-ubuntu-18-04-1-ru
* [^4]: Установка `docker-compose` для `Ubuntu 18.04`: https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04-ru
* [^5]: Install `Docker`: https://docs.docker.com/engine/install/
* [^6]: Install `docker-compose`: https://docs.docker.com/compose/install/


`More guides in README comming soon.`
