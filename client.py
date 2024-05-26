import socket
import threading
import sys

def clear_line():
    sys.stdout.write('\r' + ' ' * (len("Enter message: ") + 80) + '\r')
    sys.stdout.flush()

def listen_for_messages(sock):
    while True:
        response = sock.recv(1024)
        if not response:
            break  
        clear_line() 
        decoded_message = response.decode('utf-8')
        if ':' in decoded_message:
            server_message = decoded_message.split(":", 1)
            print(f"\n{server_message[0]} says: {server_message[1]}")
        else:
            print(f"\n{decoded_message}")
        print("Enter message: ", end='', flush=True)  

def main():
    HOST = input("Enter the server's IP address: ")  
    PORT = int(input("Enter the server's port number: ")) 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        my_name = input("Enter your unique name: ")
        s.sendall(f"register:{my_name}".encode('utf-8'))

        print(s.recv(1024).decode('utf-8'))

        threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()

        print("Type messages in the format 'recipient:subject:message'. Type 'exit' to quit.")
        while True:
            my_message = input("Enter message: ")
            if my_message.lower() == 'exit':
                break
            recipient , subject , message = my_message.split(':')
            s.sendall(f"send_message:{recipient}:{my_name}:{subject}:{message}".encode('utf-8'))
            

if __name__ == "__main__":
    main()
