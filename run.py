from app import app
from config import BASEDIR, Server
import ssl

if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile=BASEDIR+"/SSL/fullchain.pem", keyfile=BASEDIR+"/SSL/privkey.pem", password="csserver8403598*")
    app.run(host=Server.SERVER_DOMAIN, port=Server.SERVER_PORT, ssl_context=ssl_context, debug=True)