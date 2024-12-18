import socket
import struct
import time
import paho.mqtt.client as mqtt

# Map identifiers to parameter names
identifier_mapping = {
    0x01: 'battery_soc',
    0x02: 'temperature',  # Battery temperature
    0x03: 'front_motor_temp',
    0x04: 'rear_motor_temp',
    0x05: 'drive_mode',
    0x06: 'instantaneous_power'
}

# Map parameters to MQTT topics
parameter_to_topic = {
    'battery_soc': 'hmi/pcm/battery_soc',
    'temperature': 'hmi/pcm/hv_battery_pack_temp',
    'front_motor_temp': 'hmi/pcm/front_edu_reported_temp',
    'rear_motor_temp': 'hmi/pcm/back_edu_reported_temp',
    'drive_mode': 'hmi/pcm/drive_mode_active',
    'instantaneous_power': 'hmi/pcm/rear_axle_power'
}

# MQTT settings
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_client = mqtt.Client(client_id="tcp_to_mqtt", protocol=mqtt.MQTTv311)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# Dictionary to store the last valid values for battery SOC and temperatures
last_valid_values = {
    'battery_soc': None,          # Battery SOC
    'temperature': None,          # Battery temperature
    'front_motor_temp': None,
    'rear_motor_temp': None
}

def process_message(data):
    """Process and publish received Speedgoat data."""
    print(f"Raw data received: {data} (Length: {len(data)})")  # Debug raw data

    if len(data) == 3:  # Expecting 3 bytes
        try:
            # Unpack 1 byte (identifier) + 2 bytes (signed integer value)
            identifier, value = struct.unpack('!Bh', data)
            print(f"Parsed Identifier: {identifier}, Value: {value}")  # Debug parsed values
            parameter_name = identifier_mapping.get(identifier, f"Unknown(0x{identifier:02X})")
            
            # Handle battery SOC validation
            if parameter_name == 'battery_soc':
                if value > 100:  # Check if value is within valid range
                    value = last_valid_values.get('battery_soc')  # Use last valid value
                    if value is not None:
                        print(f"Ignoring invalid battery_soc value > 100. Using last valid value: {value}")
                    else:
                        print("Ignoring invalid battery_soc value > 100. No previous valid value available.")
                        return  # Skip publishing if no valid value exists
                else:
                    last_valid_values['battery_soc'] = value  # Update last valid value
                    print(f"Valid battery_soc value: {value}")

            # Handle temperature validation (battery and motor temps)
            if parameter_name in ['temperature', 'front_motor_temp', 'rear_motor_temp']:
                if 15 <= value <= 35:  # Check if value is in the valid range
                    last_valid_values[parameter_name] = value
                    print(f"Valid {parameter_name} value: {value}")
                else:
                    # Use the last valid value if out of range
                    value = last_valid_values.get(parameter_name)
                    if value is not None:
                        print(f"Ignoring invalid {parameter_name} value. Using last valid value: {value}")
                    else:
                        print(f"Ignoring invalid {parameter_name} value. No previous valid value available.")
                        return  # Skip publishing if no valid value exists
            
            if parameter_name in parameter_to_topic:
                mqtt_topic = parameter_to_topic[parameter_name]
                print(f"Publishing to MQTT: {mqtt_topic} -> {value}")  # Debug MQTT publishing
                mqtt_client.publish(mqtt_topic, str(value))
            else:
                print(f"Unknown identifier received: {identifier}")
        except struct.error as e:
            print(f"Error unpacking data: {e}")
    else:
        print("Invalid data length received. Expected 3 bytes.")

def connect_to_speedgoat(host, port):
    """Connect to the Speedgoat and process incoming data."""
    while True:  # Reconnect loop
        try:
            print(f"Connecting to Speedgoat at {host}:{port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                print(f"Connected to Speedgoat at {host}:{port}")
                
                while True:
                    data = client_socket.recv(3)  # Adjusted to receive 3 bytes
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
