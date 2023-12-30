# Auth

![logo_transparent](https://github.com/Nyan-Doggo/PyAuth/assets/70441087/731afe91-139d-4f58-89e4-126518006699)

WIP

A simple service that aims to implement OAuth from different providers and function
as a universal gateway for user identification. swapping out the complexity
of managing multiple OAuth providers with a simple three-step process

# Hosting your own version

## .ENV
The service requires a .env file in the root directory to function,
this file should at the bare minimum hold information about the hosted url,
the provider information, and the database file location

an example could look like this:
```
ENVIRONMENT=DEV
DB_PATH=./dev.db
SERVER_URL=http://localhost:3000
SERVER_SECRET=xxxxyyyyzzzz
GITHUB_CLIENT_ID=xxxxyyyyzzzz
GITHUB_CLIENT_SECRET=xxxxyyyyzzzz
DISCORD_CLIENT_ID=xxxxyyyyzzzz
DISCORD_CLIENT_SECRET=xxxxyyyyzzzz
```

## .PEM
The server needs access to a public and private RSA key,
these should be stored in the project root as `priv.pem` and
`pub.pem`, for development purposes you can make a set of test-keys
using [this generator](https://cryptotools.net/rsagen)

## Running the service
before running the service, make sure the DB exists,
if one has not been made you can use the `db_push.py`
file to create one. take note that this action will remove all
pre-existing data and will hard reset any existing database.

any existing data **WILL BE LOST**

# Auth Process:

The PyAuth Process aims to simplify the process of logging in with OAuth Providers
by giving developers a layer of abstraction that removes the need to register
applications in advance.

the process has 3 (4) steps to it that must be taken in order to complete authentication,
the authentication process relies on having a backend and frontend for your
service.

## step 1: assign a state
the backend generates a unique string and gives it to the client BEFORE
logging in. this state will help verify the users identity

## step 2: forward the client
the frontend, or client, is forwarded to PyAuth, the URL MUST include three
parameters, these are:

* `redirect`, the address the client will be returned to after OAuth completion
* `callback`, the address PyAuth will send the user-data to
* `state`, the generated unique state that associates a client with the relevant user-data

a optional `from` parameter can be included, and will be showcased on the "log in" page if
included.

the base url is `https://pyauth.com/login` and a full url should look like
`https://pyauth.com/login?redirect=your_redirect&callback=your_callback%2Fapi%2Fcallback&state=generated_state`

## step 3A: client is returned
the client gets returned to the `redirect` address once the OAuth process is complete

## step 3B: PyAuth Posts to callback
PyAuth sends a POST request to the callback, providing the following information

```json
{
	"user_id": 1,
	"user_pfp": "https://cdn.provider.com/pfp/1",
	"user_username": "provider-username",
	"user_created_at": "2000-01-01 00:00:00.000000",
	"user_email": "user@email.com",
	"user_provider": "provider",
	"session_hash": "session_hash",
	"session_signature": "signature_of_session_hash",
	"session_expires_at": "2000-01-01 00:00:00.000000",
	"session_created_at": "2000-01-01 00:00:00.000000",
	"state": "provided_state"
}
```

using NextJS, the POST route for receiving user information could be set up
like this:

```ts
// app/api/callback/route.ts

import { LogIn } from "@/actions/login";
import { PyAuthUserData } from "@/types/PyAuthUserData";

export async function POST(req: Request){
	const userData = await req.json() as PyAuthUserData;
	LogIn(userData); // implement "LogIn" however best fits your application
	return new Response("received");
}
```

the PyAuth user data can be typed as follows:

```ts
// types/PyAuthUserData.ts

export type PyAuthUserData = {
	user_id: number,
	user_pfp: string,
	user_username: string,
	user_created_at: string,
	user_email: string,
	session_hash: string,
	user_provider: string,
	session_signature: string,
	session_expires_at: string,
	session_created_at: string,
	state: string
}
```

it is the application developers responsibility to verify the state, hash and signature,
and associate this with the correct client.

# (Optional, but recommended) Verifying the information

Verifying the information is a relatively simple process, and works in the following way:
1. double check that the state does indeed originate from your service
2. ensure that the hash is correct
3. get the public key from PyAuth
4. verify using the public key that the signature is accurate

how developers wish to verify the state is up to them. but it is recommended that
the state is stored both in a location accessible to the Backend and in a separate
location tied to the frontend, typically the state would be set as a cookie
for the client, and stored separately in a database for future reference.

## Verifying the hash
the hash is a hex-digest of a SHA-256 hash, its input is a continuous string
made from joining `user_email`, `user_pfp`, `user_provider`, `user_username` and `state`.

**note:** order matters for creating the hash. the string must be constructed in
this specific order to have the right value

validating the hash is done by combining the returned values into a single string,
then hashing them and comparing the hash to the `session_hash` posted by PyAuth.

following is an example function written in TS for NextJS that illustrates this process:

```ts
import { createHash } from "crypto";

export async function VerifyHash(userData: PyAuthUserData){
	// construct the basis for the hash_string
	let user_hash = `${userData.user_id}`;
	user_hash = user_hash + `${userData.user_email}`;
	user_hash = user_hash + `${userData.user_pfp}`;
	user_hash = user_hash + `${userData.user_provider}`;
	user_hash = user_hash + `${userData.user_username}`;
	user_hash = user_hash + `${userData.state}`
	// get the hexdigest
	const hash = createHash("sha256");
	hash.update(user_hash);
	const hash_digest = hash.digest("hex");
	// compare to the submitted user data
	const isValid = hash_digest == userData.session_hash;
	return isValid;
}
```

## Get the public key and verify the signature:

Getting and verifying the public key is a similarly straightforward process.
first a GET request is sent to `https://pyauth.com/key`, the KEY is returned
as base64 encoded text. the key can then be parsed and used to verify the signature,

following is an example function written in TS for NextJS that illustrates this process:

```ts
import { createVerify } from "crypto";

export async function VerifySignature(userData: PyAuthUserData) {
	// get and decode the public key
	const publicKeyResponse = await fetch("https://pyauth.com/key");
	const publicKeyB64 = await publicKeyResponse.text();
	const publicKeyBuffer = Buffer.from(publicKeyB64, "base64");
	// decode the signature
	const signature = Buffer.from(userData.session_signature, "base64");
	// actual verification
	const verify = createVerify("RSA-SHA256");
	verify.update(userData.session_hash);
	const isValid = verify.verify(publicKeyBuffer, signature);
	return isValid;
}
```
