import socket
import struct
import time
import paho.mqtt.client as mqtt

# Map identifiers to parameter names
identifier_mapping = {
    0x01: 'battery_soc',
    0x02: 'temperature',
    0x03: 'front_motor_temp',
    0x04: 'rear_motor_temp',
    0x05: 'drive_mode'
}

# Map parameters to MQTT topics
parameter_to_topic = {
    'battery_soc': 'hmi/pcm/battery_soc',
    'temperature': 'hmi/pcm/hv_battery_pack_temp',
    'front_motor_temp': 'hmi/pcm/front_edu_reported_temp',
    'rear_motor_temp': 'hmi/pcm/back_edu_reported_temp',
    'drive_mode': 'hmi/pcm/drive_mode_active'
}

mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_client = mqtt.Client(client_id="tcp_to_mqtt", protocol=mqtt.MQTTv311)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

def process_message(data):
    print(f"Raw TCP data: {data}")
    if len(data) == 5:
        identifier, value = struct.unpack('!Bf', data)
        print(f"Parsed identifier: {identifier}, value: {value}")
        parameter_name = identifier_mapping.get(identifier, f"Unknown(0x{identifier:02X})")
        if parameter_name in parameter_to_topic:
            mqtt_topic = parameter_to_topic[parameter_name]
            print(f"Publishing to MQTT: {mqtt_topic} -> {value}")
            mqtt_client.publish(mqtt_topic, str(value))
        else:
            print(f"Unrecognized identifier: {identifier}")
    else:
        print("Received data is not 5 bytes. Invalid format.")

def start_tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Listening for TCP connections on {host}:{port}")

        # Wait for a single connection
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        while True:
            try:
                data = conn.recv(5)
                if not data:
                    print("Client disconnected.")
                    break
                process_message(data)
            except ConnectionResetError:
                print("Connection reset by peer.")
                break

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 1048
    start_tcp_server(host, port)
