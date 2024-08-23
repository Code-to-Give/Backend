# Backend

## Set up instructions

- All dependencies are stored in requirements.txt. Please do create a virtualenv as you are developing on it!
- Copy `.env.example` and input the corresponding environment variables

  _Mac and Linux_

  ```
  cp .env.example .env
  ```

  _Windows_

  ```
  copy .env.example .env
  ```

**Pre-requisties**

- Please have docker installed.

**For development**

1. Change directory to the service you choose to develop in.
1. Create a virtual env, `python -m venv venv`
1. Run `source venv/bin/activate` for Mac or Linux terminal and `./venv/Scripts/activate`

**Starting the services**

1. Enter the root directory of `Backend` folder
1. Run `docker compose up -d --build && docker compose logs -f` or how you may wish to start it up

## Ports

- `8000`: Authentication service
- `8001`: Algorithm service
