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

## Endpoints

### Auth

There are two routes in `Auth`:

1. Users
1. Admin

**Users**

Base URL: `http://localhost:8000/users`

---

**POST `/register`**

_Parameters_

| Name           | Required     | Type                        | Description                                        |
| -------------- | ------------ | --------------------------- | -------------------------------------------------- |
| `email`        | required     | string                      | Organisation's email                               |
| `password`     | required     | string                      | Password                                           |
| `company_name` | required     | string                      | Name of the organisation                           |
| `name`         | required     | string                      | Name of the user                                   |
| `phone_number` | required     | string                      | Phone number with country code                     |
| `role`         | not required | Role (Donor or Beneficiary) | This is not required as the user could be an admin |

_Response_

| Name           | Type                        | Description                                           |
| -------------- | --------------------------- | ----------------------------------------------------- |
| `_id`          | UUID                        | Unique identifer to be used across services           |
| `email`        | string                      | Organisation's email                                  |
| `password`     | string                      | Password                                              |
| `company_name` | string                      | Name of the organisation                              |
| `name`         | string                      | Name of the user                                      |
| `phone_number` | string                      | Phone number with country code                        |
| `is_verified`  | Boolean                     | Only for donors, it will be False on first register   |
| `is_superuser` | Boolean                     | If is_superuser, there will be no role                |
| `role`         | Role (Donor or Beneficiary) | This is not required as the user could be a superuser |

---

**POST `/login`**

_Parameters_

| Name       | Required | Type   | Description          |
| ---------- | -------- | ------ | -------------------- |
| `email`    | required | string | Organisation's email |
| `password` | required | string | Password             |

_Response_

| Name           | Type   | Description                       |
| -------------- | ------ | --------------------------------- |
| `access_token` | string | A signed JWT (expires in 30 mins) |
| `token_type`   | string | Always Bearer (can ignore)        |

---

**GET `/me`**

_Authorisation required_: Send with JWT from `/login`

_Parameters_: None

_Response_

| Name           | Type                        | Description                                           |
| -------------- | --------------------------- | ----------------------------------------------------- |
| `_id`          | UUID                        | Unique identifer to be used across services           |
| `email`        | string                      | Organisation's email                                  |
| `password`     | string                      | Password                                              |
| `company_name` | string                      | Name of the organisation                              |
| `name`         | string                      | Name of the user                                      |
| `phone_number` | string                      | Phone number with country code                        |
| `is_verified`  | Boolean                     | Only for donors, it will be False on first register   |
| `is_superuser` | Boolean                     | If is_superuser, there will be no role                |
| `role`         | Role (Donor or Beneficiary) | This is not required as the user could be a superuser |

---

**Admin**

Base URL: `http://localhost:8000/admin`

---

**POST `/promote/:user_id`**

Changes from `is_superuser` of the `:user_id` to True

_Authorisation required_: Send with JWT from `/login` and has to be `is_superuser = True`

_Parameters_: None

_Response_

| Name           | Type                        | Description                                           |
| -------------- | --------------------------- | ----------------------------------------------------- |
| `_id`          | UUID                        | Unique identifer to be used across services           |
| `email`        | string                      | Organisation's email                                  |
| `password`     | string                      | Password                                              |
| `company_name` | string                      | Name of the organisation                              |
| `name`         | string                      | Name of the user                                      |
| `phone_number` | string                      | Phone number with country code                        |
| `is_verified`  | Boolean                     | Only for donors, it will be False on first register   |
| `is_superuser` | Boolean                     | If is_superuser, there will be no role                |
| `role`         | Role (Donor or Beneficiary) | This is not required as the user could be a superuser |

---

**POST `/verify-donor/:user_id`**

Changes from `is_verified` of the `:user_id` to True

_Authorisation required_: Send with JWT from `/login` and has to be `is_superuser = True`

_Parameters_: None

_Response_

| Name           | Type                        | Description                                           |
| -------------- | --------------------------- | ----------------------------------------------------- |
| `_id`          | UUID                        | Unique identifer to be used across services           |
| `email`        | string                      | Organisation's email                                  |
| `password`     | string                      | Password                                              |
| `company_name` | string                      | Name of the organisation                              |
| `name`         | string                      | Name of the user                                      |
| `phone_number` | string                      | Phone number with country code                        |
| `is_verified`  | Boolean                     | Only for donors, it will be False on first register   |
| `is_superuser` | Boolean                     | If is_superuser, there will be no role                |
| `role`         | Role (Donor or Beneficiary) | This is not required as the user could be a superuser |

---
