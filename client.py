import socket
import threading
import sys

def clear_line():
    """Clears the current line in the terminal."""
    sys.stdout.write('\r' + ' ' * (len("Enter message: ") + 80) + '\r')
    sys.stdout.flush()

def listen_for_messages(sock):
    """ Continuously listen for messages from the server. """
    while True:
        response = sock.recv(1024)
        if not response:
            break  # Stop the loop if the server closes the connection or an error occurs
        clear_line()  # Clear the current input prompt before printing anything
        decoded_message = response.decode('utf-8')
        if ':' in decoded_message:
            server_message = decoded_message.split(":", 1)
            print(f"\n{server_message[0]} says: {server_message[1]}")
        else:
            print(f"\n{decoded_message}")
        print("Enter message: ", end='', flush=True)  # Prompt the user to type again without newline

def main():
    # Server details
    # The server's hostname or IP address
    HOST = input("Enter the server's IP address: ")  # e.g., 'localhost' or '192.168.1.2'
    # The port used by the server
    PORT = int(input("Enter the server's port number: "))  # e.g., 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # Register the client's unique name with the server
        my_name = input("Enter your unique name: ")
        s.sendall(f"register:{my_name}".encode('utf-8'))  # Assuming "register" is handled by the server

        #Receive registration confirmation
        print(s.recv(1024).decode('utf-8'))

        # Start a thread to continuously listen for messages from the server
        threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()
        # Daemon Thread: The thread is created as a daemon thread (daemon=True), 
        # which means it will automatically stop when the main program exits. 
        # This is useful for ensuring that no stray threads keep the program running 
        # after the main execution flow has ended.

        print("Type messages in the format 'recipient:subject:message'. Type 'exit' to quit.")
        while True:
            my_message = input("Enter message: ")
            if my_message.lower() == 'exit':
                break
            recipient , subject , message = my_message.split(':')
            s.sendall(f"send_message:{recipient}:{my_name}:{subject}:{message}".encode('utf-8'))
            

if __name__ == "__main__":
    main()
