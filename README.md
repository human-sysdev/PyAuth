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

## Process - TLDR
*Too long didnt read*

this serves as a refresher, make sure to read the actual implementation description as well

1. the user aquires a PyAuth session from `pyauth.com/login`
2. the user gets its data from `pyauth.com/me`
3. the application compares the session_signature against the key at `pyauth.com/key`

## Process - NATLMISRI
*Not actually that long maybe i should read it*

1. the user aquires a session from the service

the user needs to be redirected to `https://pyauth.com/login`,
at least one additional URL parameter **MUST** be included.

the possible parameters are: `redirect_url` and `behalf_of`,

* `redirect_url` is REQUIRED, and must be a URL encoded string pointing
back to your application, this is where the user will be sent after logging in. 
* `behalf_of` is OPTIONAL and will display on the `/login` page. "log in to {{ behalf_of }}"

a actual URL would look like this `https://pyauth.com/login?redirect_url=https%3A%2F%2Fpyauth.com%2Fme&behalf_of=pyauth`

2. the user gets its identiy from the service

when the user has a valid session, they can send a GET request to `https://pyauth.com/me`
(no parameters are required nor supported) and they will get a JSON object back,
the json object looks like this:

```json
{
    "session_created_at": "Sat, 24 Dec 2023 00:00:00 GMT",
    "session_expires_at": "Sat, 24 Dec 2023 01:00:00 GMT",
    "session_hash": "123abc_this_is_a_string_abc123",
    "session_signature": "123abc_this_is_a_signature_of_the_session_hash_abc123",
    "user_created_at": "Sat, 24 Dec 2023 00:00:00 GMT",
    "user_email": "mail@pyauth.com",
    "user_id": 1,
    "user_pfp": "https://avatars.pyauth.com/1",
    "user_provider": "pyauth",
    "user_username": "user@pyauth"
}
```

3. the service or application can verify the signature

The service or application gets a copy of the current public key from the service
by sending a GET request to `https://pyauth.com/key`, this returns a text-response
with the public RSA key. it then becomes the responsibility of the Application
to use this public RSA key to confirm that the `session_signature` is a valid
signature of the `session_hash`.

## Code Examples
Retrieving user information can be set up as a hook if you're using react/next etc:

```ts
const usePyAuth = (refresh?: any) => {
    const [isLoading, setLoading] = useState(false);
    const [userData, setUserData] = useState<PyAuthUserData | null>(null);
    const [error, setError] = useState<unknown | null>(null);

    useEffect(() => {
        const fetchUser = async () => {
            setLoading(true);
            const response = await fetch("http://localhost:3000/me", {
                credentials: "include"
            });
            try {
                const responseJson = await response.json() as PyAuthUserData;
                setUserData(responseJson);
            } catch (err) { setError(err) }
            setLoading(false);
        }
        fetchUser();
    }, [refresh])

    return { userData, error, isLoading };
}
```

an example of verifying the signature:

```ts
export async function VerifySignature(userData: PyAuthUserData) {
    // get and decode the public key
    const publicKeyResponse = await fetch("http://localhost:3000/key");
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