from bottle import Bottle, run
from rest_api.routes import setup_routes

app = Bottle()

# Setup API routes
setup_routes(app)

if __name__ == "__main__":
    run(app, host="127.0.0.1", port=8888, debug=True, reloader=True)