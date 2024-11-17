import asyncio
import json
import re
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import websockets
from datetime import datetime

class MixnetMessage:
    def __init__(self, message_bytes, recipient_address, surbs=0):
        self.message_bytes = message_bytes
        self.recipient_address = recipient_address
        self.surbs = surbs

    def to_dict(self):
        # convert the message to a dictionary for json serialization
        return {
            "type": "send",
            "recipient": self.recipient_address,
            "message": self.message_bytes,
            "surbs": self.surbs
        }

    def is_valid(self):
        # validate message before sending
        return bool(self.recipient_address and self.message_bytes)

class AsyncTkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nym Messaging Client")

        # Create a notebook (tabs) container
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Create Inbox tab
        self.inboxTab = ttk.Frame(self.notebook)
        self.notebook.add(self.inboxTab, text="Inbox")

        # Create Sent tab
        self.sentTab = ttk.Frame(self.notebook)
        self.notebook.add(self.sentTab, text="Sent")

        # Add message log (Treeview) for inbox in the Inbox tab
        self.inboxTreeview = ttk.Treeview(self.inboxTab, columns=("Message", "Time", "Date"), show="headings")
        self.inboxTreeview.heading("Message", text="Message")
        self.inboxTreeview.heading("Time", text="Time")
        self.inboxTreeview.heading("Date", text="Date")
        self.inboxTreeview.column("Message", width=300)
        self.inboxTreeview.column("Time", width=150)
        self.inboxTreeview.column("Date", width=150)
        self.inboxTreeview.pack(pady=10, expand=True, fill="both")

        # Add message log (Treeview) for sent messages in the Sent tab
        self.sentTreeview = ttk.Treeview(self.sentTab, columns=("Message", "Time", "Date"), show="headings")
        self.sentTreeview.heading("Message", text="Message")
        self.sentTreeview.heading("Time", text="Time")
        self.sentTreeview.heading("Date", text="Date")
        self.sentTreeview.column("Message", width=300)
        self.sentTreeview.column("Time", width=150)
        self.sentTreeview.column("Date", width=150)
        self.sentTreeview.pack(pady=10, expand=True, fill="both")

        # Add recipient entry, message entry, and send button in the Send Message tab
        self.recipientEntry = self.CreateEntry(self.sentTab, "Recipient Address", width=50)
        self.recipientEntry.pack(pady=5)

        self.messageEntry = self.CreateEntry(self.sentTab, "Type your message here", width=50)
        self.messageEntry.pack(pady=5)

        self.sendButton = tk.Button(self.sentTab, text="Send", command=self.sendMessage)
        self.sendButton.pack(pady=5)

        # Frame for self address entry and copy button
        self.addressFrame = tk.Frame(self.sentTab)
        self.addressFrame.pack(pady=10)

        # Entry widget to display self address (users can highlight and copy from here)
        self.selfAddressEntry = tk.Entry(self.addressFrame, width=50, state='readonly')
        self.selfAddressEntry.grid(row=0, column=0, padx=(0, 10))
        self.selfAddressEntry.insert(0, "Fetching address...")

        # Button to copy the address to clipboard
        self.copyButton = tk.Button(self.addressFrame, text="Copy to Clipboard", command=self.copyToClipboard)
        self.copyButton.grid(row=0, column=1)

        # Websocket and asyncio setup
        self.loop = asyncio.get_event_loop()
        self.websocket = None

        # Schedule the asyncio task to start
        self.root.after(100, self.startAsyncLoop)

    def CreateEntry(self, parent, placeholder, width):
        entry = tk.Entry(parent, width=width, fg='grey')
        entry.insert(0, placeholder)

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='grey')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        return entry

    def sendMessage(self):
        # Strip any leading/trailing whitespace from the recipient address
        recipient = self.recipientEntry.get().strip()
        message_content = self.messageEntry.get().strip()
        
        # Validate recipient address format
        if not self.is_valid_nym_address(recipient):
            print("Invalid recipient address: contains unsupported characters.")
            return  # Exit the function if the address is invalid

        # Create MixnetMessage
        message = MixnetMessage(message_content, recipient)
        if message.is_valid():
            self.loop.create_task(self.asyncSendMessage(message))
            self.displaySentMessage(f"Sent: {message_content}")
            self.messageEntry.delete(0, 'end')
        else:
            print("Invalid message or recipient")

    def is_valid_nym_address(self, address):
        # Validate that the address only contains allowed characters for a nym address
        nym_address_regex = re.compile("^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz.@]+$")
        return bool(nym_address_regex.match(address))

    async def asyncSendMessage(self, message):
        if self.websocket:
            # Convert the MixnetMessage instance to dictionary for JSON serialization
            await self.websocket.send(json.dumps(message.to_dict()))

    async def connectWebsocket(self):
        try:
            self.websocket = await websockets.connect("ws://127.0.0.1:1977")
            await self.websocket.send(json.dumps({"type": "selfAddress"}))
            response = await self.websocket.recv()
            data = json.loads(response)
            self_address = data.get("address")
            print("Connected to WebSocket. Your Nym Address:", self_address)
            
            # Update the entry widget with the self address
            self.selfAddressEntry.config(state='normal')
            self.selfAddressEntry.delete(0, 'end')
            self.selfAddressEntry.insert(0, self_address)
            self.selfAddressEntry.config(state='readonly')
            self.self_address = self_address  # Store address for copying
            
            await self.receiveMessages()  # Start listening for incoming messages
        except Exception as e:
            print("Connection error:", e)

    async def receiveMessages(self):
        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)
                self.displayInboxMessage(f"Received: {data.get('message', '')}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by the server.")

    def displaySentMessage(self, message):
        # Basic info
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.sentTreeview.insert("", "end", values=(message, current_time, current_date))

    def displayInboxMessage(self, message):
        # Get the current date and time
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Insert the received message into the Inbox tab Treeview
        self.inboxTreeview.insert("", "end", values=(message, current_time, current_date))

    def copyToClipboard(self):
        # Copy the self address to the clipboard when the button is clicked
        self.root.clipboard_clear()  # Clear any previous clipboard contents
        self.root.clipboard_append(self.self_address)  # Copy the address to the clipboard

    def startAsyncLoop(self):
        self.loop.create_task(self.connectWebsocket())
        self.checkAsyncioLoop()

    def checkAsyncioLoop(self):
        # Allow the asyncio loop to run periodically
        self.loop.stop()  # Stop loop if already running
        self.loop.run_forever()  # Run pending asyncio tasks
        self.root.after(100, self.checkAsyncioLoop)  # Check again after 100ms

if __name__ == "__main__":
    root = tk.Tk()
    app = AsyncTkApp(root)
    root.mainloop()
