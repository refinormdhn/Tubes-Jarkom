import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ipv4 = input("Enter server IPv4 address: ")
port = int(input("Enter server port number: "))
server_address = (ipv4, port)

sent_messages = []
running = True

# GUI setup
root = tk.Tk()
root.title("UDP Chat Client")

chat_box = scrolledtext.ScrolledText(root, state=tk.DISABLED)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def authenticate():
    global username
    password = simpledialog.askstring("Password", "Enter chatroom password:")
    client.sendto(f"PASSWORD:{password}".encode(), server_address)
    response, _ = client.recvfrom(1024)
    if response.decode() == "PASSWORD_ACCEPTED":
        username = simpledialog.askstring("Nickname", "Enter your nickname:")
        client.sendto(f"NICKNAME:{username}".encode(), server_address)
        receive_thread = threading.Thread(target=receive, daemon=True)
        receive_thread.start()
    else:
        messagebox.showerror("Error", "Incorrect password.")

def receive():
    while running:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            update_chat(decoded_message)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def update_chat(message):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, message + "\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def send_message():
    message = input_box.get()
    if message.lower() == 'exit()':
        client.sendto("EXIT()".encode(), server_address)
        client.close()
        root.quit()
    else:
        full_message = f"{username}: {message}"
        client.sendto(full_message.encode(), server_address)
        input_box.delete(0, tk.END)

input_box = tk.Entry(root)
input_box.pack(padx=10, pady=10, fill=tk.X)
input_box.bind("<Return>", lambda event: send_message())

# Start authentication process
authenticate()

root.mainloop()
