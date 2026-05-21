# 🐾 Pwnagotchi Manager

A macOS & Windows desktop app to manage your [Pwnagotchi](https://pwnagotchi.ai/) handshake captures and build [Hashcat](https://hashcat.net/) cracking commands — no terminal required.

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **SSH connection** — connect directly to your Pwnagotchi and browse captured `.pcap` files
- **Download handshakes** — pull files from the device to your Mac/PC with one click
- **Handshake analysis** — detects EAPOL frames and rates captures as GOOD / WEAK / FAIL
- **Local file support** — open `.pcap` or `.hc22000` files already on your machine
- **Hashcat command builder** — generates ready-to-run wordlist or bruteforce commands
- **Conversion helper** — auto-generates the `hcxpcapngtool` command when a `.pcap` needs converting
- **Dark UI** — GitHub-style dark theme built with PyQt6

---

## 📥 Download

Go to the [**Releases**](../../releases/latest) page and download:

| Platform | File |
|----------|------|
| macOS    | `Pwnagotchi.dmg` |
| Windows  | `Pwnagotchi.exe` |

No Python installation required — everything is bundled.

---

## 🛠 Run from source

**Requirements**
```
Python 3.10+
pip install PyQt6 paramiko
```

**Run**
```bash
git clone https://github.com/Lenni09-bit/Pwnagotchi_App.git
cd Pwnagotchi_App
pip install PyQt6 paramiko
python pwnagotchi_gui.py
```

---

## 🔧 Build it yourself

**macOS (DMG)**
```bash
pip install pyinstaller
pyinstaller pwnagotchi_gui.spec
```

**Windows (EXE)**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Pwnagotchi pwnagotchi_gui.py
```

---

## 📖 How to use

1. Connect your Pwnagotchi to the same Wi-Fi as your computer (or via USB ethernet)
2. Open the app → **Pwnagotchi (SSH)** tab
3. Enter the IP address (usually `10.0.0.2` for USB, or check your router)
4. Username: `pi` · Password: `raspberry` (default)
5. Click **Connect & Load Files**
6. Select files → **Download Selected**
7. Switch to **Attack Config**, choose wordlist or bruteforce
8. Click **Build Command** → copy and run in terminal

---

## 🧰 External tools (optional)

The app works best with these installed:

| Tool | Purpose |
|------|---------|
| [hcxpcapngtool](https://github.com/ZerBea/hcxtools) | Convert `.pcap` → `.hc22000` |
| [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) | Analyse EAPOL frames |
| [hashcat](https://hashcat.net/hashcat/) | Crack the handshake |

On macOS: `brew install hcxtools wireshark hashcat`

---

## ⚠️ Legal notice

This tool is intended for **authorized security testing and educational purposes only**.  
Only use it on networks you own or have explicit written permission to test.  
Unauthorized access to networks is illegal in most jurisdictions.

---

## 📄 License

MIT — see [LICENSE](LICENSE)
