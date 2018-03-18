echo Hello world!

CONFIG_PATH=/data/options.json

SOCKET_SERVER="$(jq --raw-output '.socket_server' $CONFIG_PATH)"
TOKEN="$(jq --raw-output '.token' $CONFIG_PATH)"

echo READ CONFIG!
echo $TOKEN
echo $SOCKET_SERVER

echo READ CONFIG END!

python3 app.py
python3 -m http.server