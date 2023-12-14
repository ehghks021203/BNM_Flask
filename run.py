from app import app
from config import BASEDIR, Server

if __name__ == "__main__":
    app.run(host=Server.SERVER_DOMAIN, port=Server.SERVER_PORT, ssl_context=Server.SSL_CONTEXT, debug=True)