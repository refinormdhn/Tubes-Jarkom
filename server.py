import socket
import threading

# Initialize server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 12345))

clients = []
usernames = {}
running = True

# Set the chatroom password
chatroom_password = input("Set the chatroom password: ")
print(f"Chatroom password: {chatroom_password}\nType \"exit()\" to shut down the server.")

def receive():
    while running:
        try:
            message, addr = server.recvfrom(1024)
            if addr not in clients:
                if not message.decode().startswith("PASSWORD:"):
                    # If first message is not a password attempt, ignore it
                    server.sendto("Please provide password first.".encode(), addr)
                    continue
                clients.append(addr)
            handle_message(message, addr)
        except socket.error as e:
            if e.errno == 10054:  # Connection reset by peer
                handle_exit(addr)
            else:
                print(f"Error receiving message: {e}")
        except Exception as e:
            print(f"Unexpected error in receive: {e}")

def handle_message(message, addr):
    try:
        decoded_message = message.decode()
        
        if decoded_message.startswith("PASSWORD:"):
            password = decoded_message.split(":", 1)[1]
            if password == chatroom_password:
                server.sendto("PASSWORD_ACCEPTED".encode(), addr)
            else:
                server.sendto("PASSWORD_REJECTED".encode(), addr)
                clients.remove(addr)
                
        elif decoded_message.startswith("NICKNAME:"):
            name = decoded_message.split(":", 1)[1]
            if name not in usernames.values():
                usernames[addr] = name
                server.sendto("USERNAME_ACCEPTED".encode(), addr)  # Send acceptance first
                broadcast(f"{name} has joined the chat!".encode(), addr)
                print(f"{name} has joined the chat.")
            else:
                server.sendto("USERNAME_TAKEN".encode(), addr)
                
        elif decoded_message == "EXIT()":
            handle_exit(addr)
            
        else:
            if addr not in usernames:
                server.sendto("Please set a nickname first.".encode(), addr)
                return
                
            if ":" in decoded_message:
                client_id, actual_message = decoded_message.split(":", 1)
                broadcast(f"{usernames[addr]}:{actual_message}".encode(), addr)
                print(f"{usernames[addr]}:{actual_message}")
            else:
                print(f"Received malformed message from {addr}: {decoded_message}")
                
    except Exception as e:
        print(f"Error handling message: {e}")
        if addr in clients:
            handle_exit(addr)

def handle_exit(addr):
    try:
        if addr in clients:
            clients.remove(addr)
        if addr in usernames:
            name = usernames.pop(addr)
            broadcast(f"{name} has left the chat.".encode(), addr)
            print(f"{name} has left the chat.")
    except Exception as e:
        print(f"Error in handle_exit: {e}")

def broadcast(message, sender_addr):
    disconnected_clients = []
    for client in clients:
        if client != sender_addr:
            try:
                server.sendto(message, client)
            except Exception as e:
                print(f"Error broadcasting message to {client}: {e}")
                disconnected_clients.append(client)
    
    # Clean up disconnected clients
    for client in disconnected_clients:
        if client in clients:
            handle_exit(client)

def listen_for_exit():
    global running
    while True:
        try:
            command = input()
            if command.lower() == 'exit()':
                running = False
                print("Shutting down the server...")
                # Send shutdown message to all clients
                for client in clients[:]:  # Use a copy of the list
                    try:
                        server.sendto("Server is shutting down.".encode(), client)
                        handle_exit(client)
                    except:
                        pass
                server.close()
                break
        except Exception as e:
            print(f"Error in listen_for_exit: {e}")
            break

# Start the threads
receive_thread = threading.Thread(target=receive)
receive_thread.daemon = True  # Make thread daemon so it exits when main thread exits
receive_thread.start()

exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.daemon = True  # Make thread daemon so it exits when main thread exits
exit_thread.start()

try:
    # Keep main thread alive
    while running:
        threading.Event().wait(1)
except KeyboardInterrupt:
    print("\nServer shutting down...")
    running = False

server.close()
