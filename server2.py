import socket
import threading
import os
import datetime

# Server settings
HOST = 'localhost'
PORT = 12346

# Dictionary to hold recipient names and their connection details
recipients = {}

# List of other servers (format: (IP, PORT))
other_servers = [('localhost', 12345), ('localhost', 12345)]

# Function to create directory for recipient if it doesn't exist
def ensure_directory(name):
    os.makedirs(name, exist_ok=True)

# Function to query other servers for a recipient
def query_other_servers(recipient , original_sender):
    for server in other_servers:
        if server == original_sender:
            continue # Avoid querying the server that originated the request
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(server)
                sock.sendall(f"query:{recipient}".encode('utf-8'))
                response = sock.recv(1024).decode('utf-8')
                if response == "found":
                    return server
        except (ConnectionError,TimeoutError):
            print(f"Failed to connect to server {server}")
            return None
    return None

# Function to forward a message to another server
def forward_message(server, recipient, sender, subject, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server)
            sock.sendall(f"send_message:{recipient}:{sender}:{subject}:{message}".encode('utf-8'))
    except ConnectionError:
        print(f"Failed to forward message to server {server}")

# Function to handle client connections
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            # Decode the received data
            decoded_data = data.decode('utf-8')
            if ':' in decoded_data:
                command = decoded_data.split(':')[0]

                if command == "register":
                    # Register the client with its unique name
                    command , sender = decoded_data.split(':' , 1)
                    recipients[sender] = conn
                    ensure_directory(sender)  # Create a directory for the sender
                    conn.sendall("Registration successfull".encode('utf-8'))
                    print(f"Registered {sender} from {addr}")
                elif command == "send_message":
                    recipient , sender , subject , message = decoded_data.split(':')[1:]
                    if recipient in recipients:
                        # Route the message to the recipient
                        recipient_conn = recipients[recipient]
                        recipient_conn.sendall(f"{sender}:{message}".encode('utf-8'))
                        print(f"Message sent to {recipient}: {message}")

                        # Save the message to a file
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        filename = f"{recipient}/{timestamp}.txt"
                        with open(filename, 'w') as file:
                            file.write(f"From: {sender}\nSubject: {subject}\nMessage: {message}\n")

                        # Send confirmation back to sender
                        conn.sendall("Message successfully sent and saved".encode('utf-8'))
                        print(f"Message saved to {filename}")
                    else :
                        # Recipient not found locally, query other servers
                        server = query_other_servers(recipient , addr)
                        if server:
                            forward_message(server, recipient, sender, subject, message)
                            conn.sendall(f"Message forwarded to server {server}".encode('utf-8'))
                        else:
                            conn.sendall("Recipient not found anywhere".encode('utf-8'))
                            print(f"No recipient found for {recipient}")
                elif command == "query":
                    command , recipient = decoded_data.split(':' , 1)
                    if recipient in recipients:
                        conn.sendall("found".encode('utf-8'))
                    else:
                        conn.sendall("not found".encode('utf-8'))
                else:
                    conn.sendall("Invalid command".encode('utf-8'))
                    print("Command not found !")
            else:
                conn.sendall("Incorrect message format".encode('utf-8'))
                print("Incorrect message format received")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        conn.close() 

# Main function to set up the server
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")
        while True:
            conn, addr = s.accept()
            # Start a new thread to handle the connection
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    main()