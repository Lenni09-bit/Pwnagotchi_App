Pwnagotchi Manager

Pwnagotchi Manager is a simple desktop application for macOS and Windows that helps you manage handshake captures from your Pwnagotchi. It also makes it easier to create Hashcat commands without having to remember long terminal commands.

Features

- Connect to your Pwnagotchi over SSH
- Configurable remote handshake folder (searched recursively) instead of a hardcoded path
- Browse and download captured .pcap files
- Point at a local folder and it will scan and analyse every .pcap/.pcapng/.hc22000 file inside, including subfolders
- Check whether a handshake is usable
- Open local .pcap and .hc22000 files
- Queue multiple wordlists and run them in order against multiple handshakes in one pass
- Generate Hashcat commands for wordlist or bruteforce attacks
- Generate the hcxpcapngtool command when a .pcap file needs to be converted
- One-click "Save & Run Script" that converts and cracks automatically, with live output
- Simple dark interface built with PyQt6

Download

Download the latest version from the Releases page.

Supported platforms:

- macOS (Pwnagotchi.dmg)
- Windows (Pwnagotchi.exe)

Python is not required. Everything is included in the download.

Run from source

Requirements:

- Python 3.10 or newer
- PyQt6
- paramiko

Install the required packages:

bash
pip install PyQt6 paramiko


Clone the repository and start the program:

bash
git clone https://github.com/Lenni09-bit/Pwnagotchi_App.git
cd Pwnagotchi_App
python pwnagotchi_gui.py


Build

macOS:

bash
pip install pyinstaller
pyinstaller pwnagotchi_gui.spec


Windows:

bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Pwnagotchi pwnagotchi_gui.py


How to use

- Connect your Pwnagotchi to your computer using USB Ethernet or the same Wi-Fi network.
- Open the app and go to the Pwnagotchi (SSH) tab.
- Enter the IP address of your Pwnagotchi.
- Log in with your username and password (default: pi / raspberry).
- If your handshakes are not in the default /home/pi/handshakes folder, change the "Handshake Folder" field before connecting.
- Click Connect & Load Files.
- Select the handshake files you want to download.
- Alternatively, open the Local Files tab and click Scan Folder to point at any local folder; every .pcap/.pcapng/.hc22000 file inside will be analysed automatically, then pick which ones to use.
- Open the Attack Config tab.
- Add one or more wordlists (they will be tried in order for each selected handshake), or switch to Bruteforce.
- Click Build Command to see the generated commands, or click Save & Run Script to have the app convert and crack automatically and show live output.

Optional tools
These programs are optional but add extra features:

- hcxpcapngtool – Convert .pcap files to .hc22000
- tshark – Analyze EAPOL frames
- hashcat – Test passwords against captured handshakes

On macOS you can install them with:

brew install hcxtools wireshark hashcat

Legal notice
This project is intended for educational purposes and authorized security testing only.
Only use it on networks that you own or have permission to test.

License
This project is licensed under the MIT License. See the LICENSE file for more information.