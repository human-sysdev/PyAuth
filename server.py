import dotenv
import flask
import os
import waitress
import flask_cors

import routes.auth_routes

dotenv.load_dotenv()

server = flask.Flask(__name__)
cors = flask_cors.CORS(server)

server.register_blueprint(routes.auth_routes.auth_blueprint)

if __name__ == "__main__":
    if os.getenv("ENVIRONMENT") == "DEV":
        server.debug == True
        server.run(port=3000)
    else:
        waitress.serve(server)