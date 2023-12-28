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