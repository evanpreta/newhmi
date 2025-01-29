Run:
1. sudo systemctl stop mosquitto
2. mosquitto -c mosquitto.conf
4. python3 -m http.server 8080
5. python tcp_client.py

Open HTML:
FONTCONFIG_PATH=/etc/fonts chromium-browser --kiosk /home/hevthmi/HMI/frontend/output.html


Test:
MQTT:
mosquitto_pub -h localhost -t hmi/pcm/battery_soc -m "75"

TCP:
python 
