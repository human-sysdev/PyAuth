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

## .PEM
The server needs access to a public and private RSA key,
these should be stored in the project root as priv.pem and
pub.pem, for development purposes you can make a set of test-keys
using [this generator](https://cryptotools.net/rsagen)

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

this can also be set up as a hook if you're using react/next etc:

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

## Trusting the client
the session is set on the client, that means you have to at least to some
extent trust that the client is honest about who they are.

one way of ensuring that the client is beeing honest is by comparing the signature
of the service, the auth service sends back both a session hash which is randomly
generated, and a RSA signed signature of that hash, by verifying
the signature using the services public key you can confirm that the hash
and by extension the session has not been tampered with.

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