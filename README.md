Run:
1. sudo systemctl stop mosquitto
2. mosquitto -c mosquitto.conf
4. python3 -m http.server 8080
5. python tcp_client.py

Test:
MQTT:
mosquitto_pub -h localhost -t hmi/pcm/battery_soc -m "75"

TCP:
python 
