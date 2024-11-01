import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime

# Inisialisasi socket UDP dan alamat server
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = None
running = True
username = ""

# GUI setup
root = tk.Tk()
root.title("UDP Chat Client")

# Kotak chat untuk menampilkan pesan
chat_box = scrolledtext.ScrolledText(root, state=tk.DISABLED)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Fungsi untuk memperbarui chat box dengan pesan baru
def update_chat(message):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, message + "\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

# Fungsi untuk otentikasi dengan percobaan berulang
def authenticate():
    global username, running
    while running:
        password = simpledialog.askstring("Password", "Enter chatroom password:", show="*")
        if password is None:
            running = False
            root.quit()
            return False

        client.sendto(f"PASSWORD:{password}".encode(), server_address)
        
        try:
            response, _ = client.recvfrom(1024)
            if response.decode() == "PASSWORD_ACCEPTED":
                if request_unique_username():
                    return True
                else:
                    running = False
                    root.quit()
                    return False
            else:
                messagebox.showerror("Error", "Incorrect password. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            running = False
            root.quit()
            return False

# Fungsi untuk meminta username unik
def request_unique_username():
    global username, running
    while running:
        username = simpledialog.askstring("Nickname", "Enter your nickname:")
        if username is None:  # User clicked Cancel
            running = False
            root.quit()
            return False

        try:
            client.sendto(f"NICKNAME:{username}".encode(), server_address)
            response, _ = client.recvfrom(1024)
            decoded_response = response.decode()
            
            if decoded_response == "USERNAME_ACCEPTED":
                # Show welcome message
                timestamp = datetime.now().strftime('%H:%M:%S')
                update_chat(f"Hello {username}, welcome to the roomchat!")
                update_chat(f"Type 'exit()' to leave the chat.")
                update_chat(f"\n")
                
                # Mulai thread untuk menerima pesan setelah otentikasi berhasil
                receive_thread = threading.Thread(target=receive, daemon=True)
                receive_thread.start()
                return True
            elif decoded_response == "USERNAME_TAKEN":
                messagebox.showwarning("Warning", "Username already taken. Please choose another.")
                continue  # Keep asking for a new username
            else:
                # Handle unexpected response
                messagebox.showerror("Error", f"Unexpected server response: {decoded_response}")
                continue
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            running = False
            root.quit()
            return False
    return False

# Fungsi untuk menerima pesan dari server
def receive():
    global running
    while running:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            timestamp = datetime.now().strftime('%H:%M:%S')
            update_chat(f"[{timestamp}] {decoded_message}")
        except Exception as e:
            if running:  # Only print error if we're still supposed to be running
                print(f"An error occurred: {e}")
            break

# Fungsi untuk mengirim pesan
def send_message():
    global running
    message = input_box.get()
    if message.lower() == 'exit()':
        running = False
        client.sendto("EXIT()".encode(), server_address)
        client.close()
        root.quit()
    else:
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"{username}: {message}"
        client.sendto(full_message.encode(), server_address)
        update_chat(f"[{timestamp}] You: {message}")
        input_box.delete(0, tk.END)

# Fungsi untuk konfigurasi server dan otentikasi awal
def setup_server():
    global server_address, running
    ipv4 = simpledialog.askstring("Server IP", "Enter server IPv4 address:")
    if ipv4 is None:
        running = False
        root.quit()
        return
        
    port = simpledialog.askinteger("Server Port", "Enter server port number:")
    if port is None:
        running = False
        root.quit()
        return
        
    server_address = (ipv4, port)
    update_chat("Connecting to the chat server...\n")
    
    if not authenticate():
        running = False
        root.quit()

# Frame untuk menempatkan kotak input dan tombol Send dalam satu baris
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=5, fill=tk.X)

# Kotak input untuk mengetik pesan
input_box = tk.Entry(input_frame)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
input_box.bind("<Return>", lambda event: send_message())

# Tombol "Send" untuk mengirim pesan (ikon pesawat kertas)
send_button = tk.Button(input_frame, text="✈️", command=send_message, font=("Arial", 12))
send_button.pack(side=tk.RIGHT)

def on_closing():
    global running
    running = False
    client.close()
    root.quit()

# Set up the window close handler
root.protocol("WM_DELETE_WINDOW", on_closing)

# Memulai setup server dan proses otentikasi
setup_server()

# Menjalankan loop GUI
root.mainloop()