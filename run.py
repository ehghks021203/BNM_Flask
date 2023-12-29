import ssl
from app import app
from config import Server

if __name__ == "__main__":
    SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS)
    print(Server.CERT_FILE)
    SSL_CONTEXT.load_cert_chain(
        certfile=Server.CERT_FILE, 
        keyfile=Server.KEY_FILE, 
        password=Server.PASSWORD
    )
    app.run(host=Server.SERVER_DOMAIN, port=Server.SERVER_PORT, ssl_context=SSL_CONTEXT, debug=True)