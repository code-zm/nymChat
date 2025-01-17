# nymChat
---
A Python Messaging Client that routes messages through the Nym Mixnet, protecting users from traffic metadata analysis.
---
## Prerequisites

- **Linux-based OS**
- **nym-client**: Download from [Nym Client Release Page](https://github.com/nymtech/nym/releases/tag/nym-binaries-v2024.12-aero)
---
## Setting up nym-client

1. **Download and make executable:**
- Once you've downloaded the `nym-client` file, navigate (`cd`) to its location in the terminal.
- Make it executable by running: `sudo chmod +x nym-client`

2. **Initialize the client**:
- Initialize the client with a unique ID by running:  `./nym-client init --id name` 
- Replace `name` with any identifier you'd like to use for your client.

3. **Run the client**:
- Start the client by running: `./nym-client run --id name`
- Replace `name` with the identifier you used during initialization.
> Once you see the message `> Client startup finished!`, you’ll know the Nym client is ready. Keep this terminal running, and open a new terminal for the next steps.
---
## Running nymChat.py

1. **Set up your Python environment**:
- Clone this repository and navigate to the directory:
```
git clone https://github.com/code-zm/nymChat.git
cd nymChat
```

2. **Create Virutal Environment**
- Run these commands to create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**:
- Install required dependencies by running: `pip install -r requirements.txt`

4. **Run the Script**:
- In a new terminal, run the Python script `python nymChat.py`

5. **Enter recipient's Nym address**:
- Exchange Nym addresses with whoever you wish to communicate with. Simply enter it into the GUI and begin sending messages. 
---
## Script Overview

- **Sending Messages**: Enter your message into the GUI.
- **Receiving Messages**: The script will display incoming messages from the Nym network in real-time as well as the messages you have sent.
---

## How to Use testClient.py
#### Run `testClient.py`
Test Client Script. Start the script with this command:
```
python testClient.py
```

#### Register a Pseudonym:
1. In the **client GUI**, click "Register."
2. Enter a pseudonym and click "Register."
3. The pseudonym will be sent to the server and added to the directory.

#### Query a Pseudonym:
1. In the **client GUI**, click "Send Query."
2. Enter the pseudonym and your query message, then click "Send."
3. The server will respond if the pseudonym exists, and you’ll see the response in the client GUI.

## Troubleshooting
If you encounter any connection issues, verify that:

- The Nym client is running and accessible in the background.
- The WebSocket URI (`ws://127.0.0.1:1977`) in `nymChat.py` matches the Nym client’s configuration.
- Try restarting the nym-client if you run into issues! CTRL + C to stop it. 
---
## License
This project is licensed under the GNU General Public License v3

