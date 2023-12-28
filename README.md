# Auth

WIP

A simple api that aims to implement oauth from different providers and function
as a universal gateway for user identification

## .ENV
The service requires a .env file in the root directory to function,
this file should at the bare minimum hold information about the hosted url,
the provider information, and the database file location

an example could look like this:
```
ENVIRONMENT=DEV
DB_PATH=./dev.db
SERVER_URL=http://localhost:3000
SERVER_SECRET=xxxxxxxxxxxxx
GITHUB_CLIENT_ID=xxxxxxxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxx
```

## Running the service
before running the service, make sure the DB exists,
if one has not been made you can use the `db_push.py`
file to create one. take note that this action will remove all
pre-existing data and will hard reset any existing database.

any existing data **WILL BE LOST**

## Process
1. the user aquires a session from the service
   1. Forward the user to `service/login?redirect_url=origin`
   2. the user goes through OAuth
   3. the user is returned to origin
2. the user gets its identiy from the service
   1. send a GET request to `service/me` and include credentials
   2. the server responds with a JSON object holding the userdata
-- if you need server validation --
3. the user forwards its information to the server
   1. give the server the `user_id` and `session_hash`
4. the server gets the userdata from the service
   1. the server sends a json POST to `service/me/server`
   2. if a session exists with the right hash and id, the server returns the user data