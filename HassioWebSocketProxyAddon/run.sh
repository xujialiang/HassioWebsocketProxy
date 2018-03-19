echo Hello world!

CONFIG_PATH=/data/options.json

SOCKET_SERVER="$(jq --raw-output '.socket_server' $CONFIG_PATH)"
AUTH_TOKEN="$(jq --raw-output '.auth_token' $CONFIG_PATH)"

echo READ CONFIG!
echo $AUTH_TOKEN
echo $SOCKET_SERVER

echo READ CONFIG END!

python3 app.py "$SOCKET_SERVER" "$AUTH_TOKEN"
python3 -m http.server