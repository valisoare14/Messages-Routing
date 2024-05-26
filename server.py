import socket
import threading
import os
import datetime

HOST = 'localhost'
PORT = 12345

recipients = {}

other_servers = [('localhost', 12346), ('localhost', 12347)]

def ensure_directory(name):
    os.makedirs(name, exist_ok=True)

def query_other_servers(recipient , original_sender):
    for server in other_servers:
        if server == original_sender:
            continue 
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

def forward_message(server, recipient, sender, subject, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server)
            sock.sendall(f"send_message:{recipient}:{sender}:{subject}:{message}".encode('utf-8'))
    except ConnectionError:
        print(f"Failed to forward message to server {server}")

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            decoded_data = data.decode('utf-8')
            if ':' in decoded_data:
                command = decoded_data.split(':')[0]

                if command == "register":
                    command , sender = decoded_data.split(':' , 1)
                    recipients[sender] = conn
                    ensure_directory(sender)
                    conn.sendall("Registration successfull".encode('utf-8'))
                    print(f"Registered {sender} from {addr}")
                elif command == "send_message":
                    recipient , sender , subject , message = decoded_data.split(':')[1:]
                    if recipient in recipients:
                        recipient_conn = recipients[recipient]
                        recipient_conn.sendall(f"{sender}:{message}".encode('utf-8'))
                        print(f"Message sent to {recipient}: {message}")

                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        filename = f"{recipient}/{timestamp}.txt"
                        with open(filename, 'w') as file:
                            file.write(f"From: {sender}\nSubject: {subject}\nMessage: {message}\n")

                        conn.sendall("Message successfully sent and saved".encode('utf-8'))
                        print(f"Message saved to {filename}")
                    else :
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

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    main()
