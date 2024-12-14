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

# MQTT settings
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_client = mqtt.Client(client_id="tcp_to_mqtt", protocol=mqtt.MQTTv311)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

def process_message(data):
    """Process and publish received Speedgoat data."""
    if len(data) == 5:
        identifier, value = struct.unpack('!Bf', data)
        parameter_name = identifier_mapping.get(identifier, f"Unknown(0x{identifier:02X})")
        if parameter_name in parameter_to_topic:
            mqtt_topic = parameter_to_topic[parameter_name]
            print(f"Publishing to MQTT: {mqtt_topic} -> {value}")
            mqtt_client.publish(mqtt_topic, str(value))

def connect_to_speedgoat(host, port):
    """Connect to the Speedgoat and process incoming data."""
    while True:  # Reconnect loop
        try:
            print(f"Connecting to Speedgoat at {host}:{port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                print(f"Connected to Speedgoat at {host}:{port}")
                
                while True:
                    data = client_socket.recv(5)
                    if not data:
                        print("Connection closed by Speedgoat.")
                        break
                    process_message(data)
        except (ConnectionRefusedError, ConnectionResetError, socket.timeout) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    # Speedgoat settings
    speedgoat_host = "10.10.10.1"  # Replace with Speedgoat's IP address
    speedgoat_port = 1048         # Replace with Speedgoat's listening port

    connect_to_speedgoat(speedgoat_host, speedgoat_port)
