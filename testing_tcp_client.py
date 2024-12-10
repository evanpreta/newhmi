import socket
import struct

def send_data(conn):
    while True:
        try:
            # Get identifier and value from the user
            identifier = int(input("Enter identifier (hex, e.g., 0x01): "), 16)
            value = float(input("Enter value (float): "))
            
            # Pack and send data
            data = struct.pack("!Bf", identifier, value)
            conn.sendall(data)
            print(f"Sent: identifier={identifier}, value={value}")
        except (ValueError, struct.error):
            print("Invalid input. Please try again.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break

def main():
    host = "localhost"
    port = 1048
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to {host}:{port}")
        send_data(s)

if __name__ == "__main__":
    main()
