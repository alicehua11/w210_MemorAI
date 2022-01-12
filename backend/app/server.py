import uvicorn

# Should there be permission issue do,
# sudo chmod -R 777 /etc/letsencrypt/
if __name__ == '__main__':
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                ssl_keyfile="/etc/letsencrypt/live/www.alexdomain.xyz/privkey.pem",
                ssl_certfile="/etc/letsencrypt/live/www.alexdomain.xyz/fullchain.pem"
                )