**UDP Chat Application**
This repository contains a simple UDP chat application consisting of a server and a client, both implemented in Python. Users can communicate with each other in a chatroom after authenticating with a password and choosing a unique nickname.

**Prerequisites**
Python 3.x
Tkinter (usually included with Python installations)

**Getting Started**

**IMPORTANT**
When you want to connect wirelessly between two pc, make sure it connected to the same internet.
After that search for the server's pc IP address, and type it into the server.py, make sure to use same IP when asked on client.py.

**Running the Server**
Open a Terminal.

Run the server script:
python server.py

Set the chatroom password when prompted. This password will be required for clients to join the chatroom.
To shut down the server, type exit() in the terminal.

**Running the Client**
Open another Terminal.

Run the client script:
python client.py

Enter the server's IP address and port number when prompted. This should match the address where the server is running (e.g., localhost and 12345).
Enter the chatroom password when prompted.
Choose a unique nickname when prompted. If the nickname is already taken, you will be asked to choose another one.
Start chatting! Messages will appear in the chat window, and you can send messages by typing in the input box and pressing Enter or clicking the Send button.
To leave the chatroom, type exit() and press Enter.

**Notes**
The server can handle multiple clients, but all clients must provide the correct password and a unique nickname to participate in the chat.
Ensure that the server is running before starting the client.
If you encounter any issues, check that the server is properly bound to the desired address and port, and ensure there are no firewalls blocking UDP traffic.


