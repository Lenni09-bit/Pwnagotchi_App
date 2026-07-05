"""
Pwnagotchi Handshake Manager & Hashcat Command Builder

Requirements:
    pip install PyQt6 paramiko

Run:
    python pwnagotchi_manager.py
"""

import os
import re
import sys
import subprocess
import threading
import shutil
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QCheckBox, QComboBox, QTextEdit, QGroupBox, QSplitter,
    QFrame, QScrollArea, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QClipboard

# CONSTANTS

HANDSHAKE_REMOTE_PATH = "/home/pi/handshakes"
DOWNLOAD_DIR = Path.home() / "Downloads" / "pwn"

WORKLOAD_MAP = {
    "Low":      "-w 1",
    "Balanced": "-w 2",
    "High":     "-w 3",
    "Extreme":  "-w 4",
}

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Courier New', monospace;
}
QTabWidget::pane {
    border: 1px solid #30363d;
    background-color: #161b22;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #21262d;
    color: #8b949e;
    padding: 8px 20px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    font-size: 12px;
}
QTabBar::tab:selected {
    background-color: #161b22;
    color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}
QTabBar::tab:hover:!selected {
    background-color: #30363d;
    color: #c9d1d9;
}
QGroupBox {
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 12px;
    padding: 12px;
    font-weight: bold;
    font-size: 12px;
    color: #58a6ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #58a6ff;
}
QLineEdit {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px 10px;
    color: #c9d1d9;
    font-size: 12px;
    selection-background-color: #264f78;
}
QLineEdit:focus {
    border: 1px solid #58a6ff;
}
QLineEdit:disabled {
    background-color: #161b22;
    color: #484f58;
}
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 5px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: bold;
    font-family: 'Courier New', monospace;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: #58a6ff;
}
QPushButton:pressed {
    background-color: #161b22;
}
QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}
QPushButton#primary {
    background-color: #1f6feb;
    color: #ffffff;
    border: none;
}
QPushButton#primary:hover {
    background-color: #388bfd;
    color: #ffffff;
}
QPushButton#primary:disabled {
    background-color: #21262d;
    color: #484f58;
}
QPushButton#danger {
    background-color: #da3633;
    color: #ffffff;
    border: none;
}
QPushButton#danger:hover {
    background-color: #f85149;
}
QPushButton#success {
    background-color: #238636;
    color: #ffffff;
    border: none;
}
QPushButton#success:hover {
    background-color: #2ea043;
}
QListWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 4px;
    color: #c9d1d9;
    font-size: 12px;
    font-family: 'Courier New', monospace;
}
QListWidget::item {
    padding: 5px 8px;
    border-radius: 3px;
}
QListWidget::item:selected {
    background-color: #264f78;
    color: #58a6ff;
}
QListWidget::item:hover {
    background-color: #21262d;
}
QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 8px;
    color: #39d353;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}
QCheckBox {
    spacing: 8px;
    color: #c9d1d9;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #30363d;
    background-color: #21262d;
}
QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
}
QComboBox {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px 10px;
    color: #c9d1d9;
    font-size: 12px;
    min-width: 120px;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
    selection-background-color: #264f78;
}
QLabel#status_ok {
    color: #3fb950;
    font-size: 12px;
    padding: 4px;
}
QLabel#status_err {
    color: #f85149;
    font-size: 12px;
    padding: 4px;
}
QLabel#status_info {
    color: #58a6ff;
    font-size: 12px;
    padding: 4px;
}
QLabel#status_warn {
    color: #d29922;
    font-size: 12px;
    padding: 4px;
}
QSplitter::handle {
    background-color: #30363d;
    width: 2px;
}
QScrollBar:vertical {
    border: none;
    background: #161b22;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #58a6ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #21262d;
    text-align: center;
    color: #c9d1d9;
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 3px;
}
"""


# DATA MODELS

# HANDSHAKE ANALYSIS

class HandshakeQuality:
    GOOD    = "GOOD"
    WEAK    = "WEAK"
    FAIL    = "FAIL"
    UNKNOWN = "UNKNOWN"


def _fmt_size(n_bytes: "Optional[int]") -> str:
    if n_bytes is None:
        return "—"
    if n_bytes < 1024:
        return f"{n_bytes} B"
    elif n_bytes < 1024 ** 2:
        return f"{n_bytes / 1024:.1f} KB"
    elif n_bytes < 1024 ** 3:
        return f"{n_bytes / 1024**2:.1f} MB"
    else:
        return f"{n_bytes / 1024**3:.2f} GB"


def _analyse_pcap(pcap_path: str) -> "tuple[str, int]":
    import shutil as _shutil
    import tempfile
    try:
        # Method 1: tshark
        tshark = _shutil.which("tshark")
        if tshark:
            result = subprocess.run(
                [tshark, "-r", pcap_path, "-Y", "eapol", "-T", "fields",
                 "-e", "frame.number"],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
                count = len(lines)
                if count >= 4:
                    return HandshakeQuality.GOOD, count
                elif count > 0:
                    return HandshakeQuality.WEAK, count
                else:
                    return HandshakeQuality.FAIL, 0

        # Method 2: hcxpcapngtool
        hcx = _shutil.which("hcxpcapngtool") or "/opt/homebrew/bin/hcxpcapngtool"
        if Path(hcx).exists():
            with tempfile.NamedTemporaryFile(suffix=".hc22000", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                subprocess.run(
                    [hcx, "-o", tmp_path, pcap_path],
                    capture_output=True, text=True, timeout=20,
                )
                count = 0
                if Path(tmp_path).exists():
                    with open(tmp_path, "r", errors="ignore") as fh:
                        count = sum(1 for l in fh if l.startswith("WPA*"))
                    os.unlink(tmp_path)
                if count >= 2:
                    return HandshakeQuality.GOOD, count * 2
                elif count == 1:
                    return HandshakeQuality.WEAK, 2
                else:
                    return HandshakeQuality.FAIL, 0
            except Exception:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        # Method 3: raw EAPOL ethertype scan
        EAPOL_MAGIC = b"\x88\x8e"
        count = 0
        with open(pcap_path, "rb") as fh:
            data = fh.read()
        idx = 0
        while True:
            idx = data.find(EAPOL_MAGIC, idx)
            if idx == -1:
                break
            count += 1
            idx += 2
        if count >= 4:
            return HandshakeQuality.GOOD, count
        elif count > 0:
            return HandshakeQuality.WEAK, count
        else:
            return HandshakeQuality.FAIL, 0
    except Exception:
        return HandshakeQuality.FAIL, 0


# DATA MODELS  (extended)

class HandshakeFile:
    """Represents a .pcap or .hc22000 file, either remote or local."""

    def __init__(self, path: str, is_remote: bool = False):
        self.path = path
        self.is_remote = is_remote
        self.filename = os.path.basename(path)
        # Extended fields
        self.size_bytes: "Optional[int]" = None
        self.hs_quality: str = HandshakeQuality.UNKNOWN
        self.eapol_count: int = 0
        self.hs_analysed: bool = False

    def fetch_local_size(self) -> None:
        try:
            self.size_bytes = Path(self.path).expanduser().resolve().stat().st_size
        except Exception:
            self.size_bytes = None

    def size_str(self) -> str:
        return _fmt_size(self.size_bytes)

    def analyse(self) -> None:
        if self.is_remote:
            self.hs_quality = HandshakeQuality.UNKNOWN
            self.hs_analysed = True
            return
        ext = self.extension()
        if ext in (".pcap", ".pcapng"):
            quality, count = _analyse_pcap(self.path)
            self.hs_quality = quality
            self.eapol_count = count
        elif ext == ".hc22000":
            try:
                count = 0
                with open(self.path, "r", errors="ignore") as fh:
                    for line in fh:
                        if line.startswith("WPA*02*"):
                            count += 1
                self.eapol_count = count * 4
                if count >= 1:
                    self.hs_quality = HandshakeQuality.GOOD
                else:
                    with open(self.path, "r", errors="ignore") as fh:
                        pmkid = sum(1 for l in fh if l.startswith("WPA*01*"))
                    if pmkid:
                        self.hs_quality = HandshakeQuality.WEAK
                        self.eapol_count = pmkid
                    else:
                        self.hs_quality = HandshakeQuality.FAIL
            except Exception:
                self.hs_quality = HandshakeQuality.FAIL
        else:
            self.hs_quality = HandshakeQuality.UNKNOWN
        self.hs_analysed = True

    def quality_icon(self) -> str:
        return {
            HandshakeQuality.GOOD:    "GOOD",
            HandshakeQuality.WEAK:    "WEAK",
            HandshakeQuality.FAIL:    "FAIL",
            HandshakeQuality.UNKNOWN: "UNKNOWN",
        }.get(self.hs_quality, "—")

    def quality_color(self) -> str:
        return {
            HandshakeQuality.GOOD:    "#3fb950",
            HandshakeQuality.WEAK:    "#d29922",
            HandshakeQuality.FAIL:    "#f85149",
            HandshakeQuality.UNKNOWN: "#8b949e",
        }.get(self.hs_quality, "#8b949e")

    def list_label(self) -> str:
        prefix = "[SSH]" if self.is_remote else "[LOCAL]"
        size   = self.size_str().rjust(9)
        status = self.quality_icon()
        return f"{prefix}  {self.filename:<40}  {size}   {status}"

    def detail_text(self) -> str:
        lines = [
            f"File:        {self.filename}",
            f"Type:        {self.extension().lstrip('.').upper()}",
            f"Location:    {'Remote (SSH)' if self.is_remote else self.path}",
            f"Size:        {self.size_str()}",
            f"Status:      {self.quality_icon()}",
            f"EAPOL/WPA:   {self.eapol_count if self.hs_analysed else 'not yet analysed'}",
        ]
        if self.hs_quality == HandshakeQuality.FAIL:
            lines += ["", "Warning: this capture does not contain a valid WPA handshake.",
                      "   Try capturing again closer to the access point."]
        elif self.hs_quality == HandshakeQuality.WEAK:
            lines += ["", "Warning: incomplete handshake, hashcat may still crack it via PMKID."]
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.list_label()

    def extension(self) -> str:
        return Path(self.filename).suffix.lower()

    def validate(self) -> "tuple[bool, str]":
        ext = self.extension()
        if self.is_remote:
            if ext not in (".pcap", ".pcapng", ".hc22000"):
                return False, f"Unknown extension: {ext}"
            return True, "OK"
        if not os.path.exists(self.path):
            return False, f"File not found: {self.path}"
        if ext == ".hc22000":
            try:
                with open(self.path, "r", errors="ignore") as f:
                    first_line = f.readline().strip()
                if not first_line.startswith("WPA*"):
                    return False, ".hc22000 file does not start with 'WPA*'"
            except Exception as e:
                return False, f"Cannot read file: {e}"
        elif ext not in (".pcap", ".pcapng"):
            return False, f"Unsupported extension: {ext}"
        return True, "OK"


# SSH WORKER THREAD

class SSHWorker(QThread):
    """Runs SSH operations in a background thread to avoid UI freezes."""

    connected = pyqtSignal(list)          # list of (path, size_or_None) tuples
    error = pyqtSignal(str)
    download_done = pyqtSignal(str)       # local path of downloaded file
    download_error = pyqtSignal(str)

    def __init__(self, host: str, username: str, password: str):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self._mode = "list"
        self._remote_path: str = ""
        self._local_path: str = ""
        self._list_dir: str = HANDSHAKE_REMOTE_PATH

    def set_download(self, remote_path: str, local_path: str):
        self._mode = "download"
        self._remote_path = remote_path
        self._local_path = local_path

    def set_list_dir(self, remote_dir: str):
        """Configure which remote folder to scan for .pcap files (fixes the
        old hardcoded-path bug where any handshakes outside
        /home/pi/handshakes were invisible)."""
        self._mode = "list"
        self._list_dir = remote_dir.strip() or HANDSHAKE_REMOTE_PATH

    def _make_client(self):
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            self.host,
            username=self.username,
            password=self.password,
            timeout=10,
            banner_timeout=10,
            auth_timeout=10,
        )
        return client

    def run(self):
        try:
            import paramiko
        except ImportError:
            self.error.emit("Paramiko not installed. Run: pip install paramiko")
            return

        if self._mode == "list":
            self._run_list()
        elif self._mode == "download":
            self._run_download()

    def _run_list(self):
        try:
            import shlex
            client = self._make_client()
            remote_dir = shlex.quote(self._list_dir.rstrip("/") or "/")
            # Search the configured folder recursively (find handles pcap AND
            # pcapng, and won't silently return nothing just because the
            # handshakes live one directory deeper than expected).
            cmd = (
                f"find {remote_dir} -maxdepth 4 -type f "
                f"\\( -iname '*.pcap' -o -iname '*.pcapng' \\) "
                f"-exec stat -c '%n %s' {{}} \\; 2>/dev/null"
            )
            _, stdout, stderr = client.exec_command(cmd, timeout=20)
            output = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            client.close()

            if not output and err:
                self.error.emit(f"No files found in '{self._list_dir}' ({err})")
                return

            file_info: list = []
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit(" ", 1)
                if len(parts) == 2:
                    try:
                        file_info.append((parts[0], int(parts[1])))
                    except ValueError:
                        file_info.append((parts[0], None))
                else:
                    file_info.append((line, None))
            self.connected.emit(file_info)

        except Exception as e:
            self.error.emit(str(e))

    def _run_download(self):
        try:
            import paramiko
            client = self._make_client()
            sftp = client.open_sftp()
            os.makedirs(os.path.dirname(self._local_path), exist_ok=True)
            sftp.get(self._remote_path, self._local_path)
            sftp.close()
            client.close()
            self.download_done.emit(self._local_path)
        except Exception as e:
            self.download_error.emit(str(e))


# REUSABLE UI HELPERS

class ScriptRunWorker(QThread):
    """Runs a generated shell script and streams its output back to the UI
    so the whole convert-and-crack pipeline can happen with one click instead
    of manually copy/pasting two commands per file."""

    output_line = pyqtSignal(str)
    finished_run = pyqtSignal(int)

    def __init__(self, script_path: str):
        super().__init__()
        self.script_path = script_path
        self._proc: "subprocess.Popen | None" = None

    def run(self):
        try:
            self._proc = subprocess.Popen(
                ["/bin/bash", self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert self._proc.stdout is not None
            for line in self._proc.stdout:
                self.output_line.emit(line.rstrip("\n"))
            self._proc.wait()
            self.finished_run.emit(self._proc.returncode)
        except Exception as e:
            self.output_line.emit(f"[ERROR] {e}")
            self.finished_run.emit(-1)

    def stop(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()


def make_label(text: str, bold: bool = False, size: int = 12) -> QLabel:
    lbl = QLabel(text)
    font = QFont("Courier New", size)
    font.setBold(bold)
    lbl.setFont(font)
    return lbl


def make_button(text: str, obj_name: str = "") -> QPushButton:
    btn = QPushButton(text)
    if obj_name:
        btn.setObjectName(obj_name)
    return btn


def make_group(title: str) -> tuple[QGroupBox, QVBoxLayout]:
    box = QGroupBox(title)
    layout = QVBoxLayout(box)
    layout.setSpacing(8)
    return box, layout


def separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #30363d;")
    return line


# SSH TAB

class SSHTab(QWidget):
    files_loaded = pyqtSignal(list)   # list of HandshakeFile
    status_update = pyqtSignal(str, str)  # message, level

    def __init__(self):
        super().__init__()
        self._ssh_worker: SSHWorker | None = None
        self._dl_worker: SSHWorker | None = None
        self._loaded_files: list[HandshakeFile] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Connection group
        conn_box, conn_layout = make_group("SSH Connection")

        row1 = QHBoxLayout()
        row1.addWidget(make_label("IP Address:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.x.x")
        row1.addWidget(self.ip_input)
        conn_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(make_label("Username: "))
        self.user_input = QLineEdit("pi")
        row2.addWidget(self.user_input)
        conn_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(make_label("Password: "))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("raspberry")
        row3.addWidget(self.pass_input)
        conn_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(make_label("Handshake Folder:"))
        self.remote_dir_input = QLineEdit(HANDSHAKE_REMOTE_PATH)
        self.remote_dir_input.setPlaceholderText("/home/pi/handshakes")
        self.remote_dir_input.setToolTip(
            "Folder on the Pwnagotchi to scan (searched recursively, 4 levels "
            "deep). Change this if your handshakes live somewhere other than "
            "the default — e.g. /home/pi/loot or a custom plugin path."
        )
        row4.addWidget(self.remote_dir_input)
        conn_layout.addLayout(row4)

        self.connect_btn = make_button("Connect & Load Files", "primary")
        self.connect_btn.clicked.connect(self._connect)
        conn_layout.addWidget(self.connect_btn)

        layout.addWidget(conn_box)

        # File list
        files_box, files_layout = make_group("Remote Handshake Files")

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(180)
        files_layout.addWidget(self.file_list)

        self.download_btn = make_button("Download Selected", "success")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._download_selected)
        files_layout.addWidget(self.download_btn)

        layout.addWidget(files_box)

        detail_box, detail_layout = make_group("File Details")
        self.detail_label = QTextEdit()
        self.detail_label.setReadOnly(True)
        self.detail_label.setMaximumHeight(110)
        self.detail_label.setPlaceholderText("Select a file to see details…")
        self.detail_label.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #8b949e;"
            " border: 1px solid #21262d; border-radius: 4px;"
            " font-family: 'Courier New'; font-size: 11px; padding: 6px; }"
        )
        detail_layout.addWidget(self.detail_label)
        layout.addWidget(detail_box)

        self.file_list.currentItemChanged.connect(self._on_ssh_selection_changed)
        layout.addStretch()

    def _connect(self):
        host = self.ip_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()

        if not host:
            self.status_update.emit("Please enter an IP address.", "err")
            return

        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        self.file_list.clear()
        self._loaded_files = []
        self.download_btn.setEnabled(False)
        self.status_update.emit(f"Connecting to {host}...", "info")

        remote_dir = self.remote_dir_input.text().strip() or HANDSHAKE_REMOTE_PATH

        self._ssh_worker = SSHWorker(host, user, password)
        self._ssh_worker.set_list_dir(remote_dir)
        self._ssh_worker.connected.connect(self._on_connected)
        self._ssh_worker.error.connect(self._on_error)
        self._ssh_worker.start()

    def _on_connected(self, file_info: list):
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect & Load Files")

        if not file_info:
            self.status_update.emit("Connected — no .pcap files found.", "warn")
            return

        for entry in file_info:
            if isinstance(entry, tuple):
                p, size = entry
            else:
                p, size = entry, None
            hf = HandshakeFile(p, is_remote=True)
            hf.size_bytes = size
            hf.hs_quality = HandshakeQuality.UNKNOWN
            valid, msg = hf.validate()
            if valid:
                self._loaded_files.append(hf)
                item = QListWidgetItem(hf.list_label())
                item.setForeground(QColor(hf.quality_color()))
                item.setData(Qt.ItemDataRole.UserRole, hf)
                self.file_list.addItem(item)

        self.download_btn.setEnabled(True)
        self.files_loaded.emit(self._loaded_files)
        self.status_update.emit(f"Loaded {len(self._loaded_files)} file(s) from remote.", "ok")

    def _on_error(self, msg: str):
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect & Load Files")
        self.status_update.emit(f"SSH error: {msg}", "err")

    def _download_selected(self):
        selected = self.file_list.selectedItems()
        if not selected:
            self.status_update.emit("No files selected for download.", "warn")
            return

        host = self.ip_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.download_btn.setEnabled(False)

        # Download one at a time (simplest stable approach)
        self._pending_downloads = [
            item.data(Qt.ItemDataRole.UserRole) for item in selected
        ]
        self._dl_host = host
        self._dl_user = user
        self._dl_pass = password
        self._dl_success = 0
        self._dl_fail = 0
        self._download_next()

    def _download_next(self):
        if not self._pending_downloads:
            self.download_btn.setEnabled(True)
            total = self._dl_success + self._dl_fail
            msg = f"Downloaded {self._dl_success}/{total} file(s) to {DOWNLOAD_DIR}"
            level = "ok" if self._dl_fail == 0 else "warn"
            self.status_update.emit(msg, level)
            return

        hf: HandshakeFile = self._pending_downloads.pop(0)
        local_path = str(DOWNLOAD_DIR / hf.filename)

        self._dl_worker = SSHWorker(self._dl_host, self._dl_user, self._dl_pass)
        self._dl_worker.set_download(hf.path, local_path)
        self._dl_worker.download_done.connect(self._on_dl_done)
        self._dl_worker.download_error.connect(self._on_dl_error)
        self._dl_worker.start()
        self.status_update.emit(f"Downloading {hf.filename}...", "info")

    def _on_dl_done(self, local_path: str):
        self._dl_success += 1
        self._download_next()

    def _on_dl_error(self, msg: str):
        self._dl_fail += 1
        self.status_update.emit(f"Download failed: {msg}", "err")
        self._download_next()

    def _on_ssh_selection_changed(self, current, _previous):
        if current is None:
            self.detail_label.setPlainText("")
            return
        hf = current.data(Qt.ItemDataRole.UserRole)
        if hf:
            self.detail_label.setPlainText(hf.detail_text())

    def get_selected_files(self) -> list[HandshakeFile]:
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.file_list.selectedItems()
        ]


# LOCAL FILES TAB

class LocalTab(QWidget):
    files_loaded = pyqtSignal(list)
    status_update = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._loaded_files: list[HandshakeFile] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        files_box, files_layout = make_group("Local Handshake Files")

        btn_row = QHBoxLayout()
        self.select_btn = make_button("Select Files", "primary")
        self.select_btn.setToolTip("Pick individual .pcap / .hc22000 files")
        self.select_btn.clicked.connect(self._select_files)
        btn_row.addWidget(self.select_btn)

        self.select_folder_btn = make_button("Scan Folder", "primary")
        self.select_folder_btn.setToolTip(
            "Point at a folder — every .pcap/.pcapng/.hc22000 file inside "
            "(including subfolders) will be analysed automatically. Pick "
            "which ones to crunch afterwards with the checkboxes/selection."
        )
        self.select_folder_btn.clicked.connect(self._select_folder)
        btn_row.addWidget(self.select_folder_btn)

        self.analyse_btn = make_button("Analyse Selected")
        self.analyse_btn.setEnabled(False)
        self.analyse_btn.setToolTip("Run EAPOL handshake analysis on selected files")
        self.analyse_btn.clicked.connect(self._analyse_selected)
        btn_row.addWidget(self.analyse_btn)
        files_layout.addLayout(btn_row)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(160)
        files_layout.addWidget(self.file_list)

        list_btn_row = QHBoxLayout()
        select_all_btn = make_button("Select All")
        select_all_btn.clicked.connect(self.file_list.selectAll)
        list_btn_row.addWidget(select_all_btn)

        select_none_btn = make_button("Select None")
        select_none_btn.clicked.connect(self.file_list.clearSelection)
        list_btn_row.addWidget(select_none_btn)

        clear_btn = make_button("Clear List")
        clear_btn.clicked.connect(self._clear)
        list_btn_row.addWidget(clear_btn)
        files_layout.addLayout(list_btn_row)

        layout.addWidget(files_box)

        detail_box, detail_layout = make_group("File Details")
        self.detail_label = QTextEdit()
        self.detail_label.setReadOnly(True)
        self.detail_label.setMaximumHeight(110)
        self.detail_label.setPlaceholderText("Select a file to see details…")
        self.detail_label.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #8b949e;"
            " border: 1px solid #21262d; border-radius: 4px;"
            " font-family: 'Courier New'; font-size: 11px; padding: 6px; }"
        )
        detail_layout.addWidget(self.detail_label)
        layout.addWidget(detail_box)

        self.file_list.currentItemChanged.connect(self._on_local_selection_changed)
        layout.addStretch()

    def _select_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Handshake Files",
            str(Path.home()),
            "Handshake Files (*.pcap *.pcapng *.hc22000);;All Files (*)",
        )
        if not paths:
            return
        self._add_paths(paths)

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Scan for Handshakes", str(Path.home())
        )
        if not folder:
            return

        exts = {".pcap", ".pcapng", ".hc22000"}
        existing = {Path(hf.path).resolve() for hf in self._loaded_files}
        found: list[str] = []
        for root, _dirs, filenames in os.walk(folder):
            for fname in filenames:
                if Path(fname).suffix.lower() in exts:
                    full = Path(root) / fname
                    if full.resolve() not in existing:
                        found.append(str(full))

        if not found:
            self.status_update.emit(
                f"No .pcap/.pcapng/.hc22000 files found under {folder}.", "warn"
            )
            return

        self.status_update.emit(
            f"Scanning {len(found)} file(s) in {folder} …", "info"
        )
        self._add_paths(sorted(found))

    def _add_paths(self, paths: list[str]) -> None:
        added = 0
        for p in paths:
            hf = HandshakeFile(p, is_remote=False)
            valid, msg = hf.validate()
            if valid:
                hf.fetch_local_size()
                hf.analyse()
                self._loaded_files.append(hf)
                item = QListWidgetItem(hf.list_label())
                item.setForeground(QColor(hf.quality_color()))
                item.setData(Qt.ItemDataRole.UserRole, hf)
                self.file_list.addItem(item)
                added += 1
            else:
                self.status_update.emit(f"Skipped {hf.filename}: {msg}", "warn")

        if added:
            self.analyse_btn.setEnabled(True)
            self.files_loaded.emit(self._loaded_files)
            self.status_update.emit(
                f"Added {added} file(s) — select the ones you want to crunch, "
                f"then set your wordlist(s) and Build Command.",
                "ok",
            )

    def _clear(self):
        self.file_list.clear()
        self._loaded_files.clear()
        self.detail_label.setPlainText("")
        self.analyse_btn.setEnabled(False)
        self.files_loaded.emit([])
        self.status_update.emit("File list cleared.", "info")

    def _analyse_selected(self):
        selected = self.file_list.selectedItems()
        if not selected:
            selected = [self.file_list.item(i) for i in range(self.file_list.count())]
        for item in selected:
            hf = item.data(Qt.ItemDataRole.UserRole)
            if hf and not hf.is_remote:
                hf.analyse()
                item.setText(hf.list_label())
                item.setForeground(QColor(hf.quality_color()))
        self.status_update.emit(f"Analysis complete for {len(selected)} file(s).", "ok")

    def _on_local_selection_changed(self, current, _previous):
        if current is None:
            self.detail_label.setPlainText("")
            return
        hf = current.data(Qt.ItemDataRole.UserRole)
        if hf:
            self.detail_label.setPlainText(hf.detail_text())

    def get_selected_files(self) -> list[HandshakeFile]:
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.file_list.selectedItems()
        ]


# ATTACK CONFIG PANEL

class AttackConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._wordlist_paths: list[str] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.attack_tabs = QTabWidget()

        # Wordlist Tab
        wl_widget = QWidget()
        wl_layout = QVBoxLayout(wl_widget)
        wl_layout.setSpacing(10)

        wl_btn_row = QHBoxLayout()
        wl_add_btn = make_button("Add Wordlist(s)", "primary")
        wl_add_btn.setToolTip(
            "Select one or more wordlists — they'll be tried in order against "
            "every selected handshake."
        )
        wl_add_btn.clicked.connect(self._add_wordlists)
        wl_btn_row.addWidget(wl_add_btn)

        wl_remove_btn = make_button("Remove Selected")
        wl_remove_btn.clicked.connect(self._remove_wordlists)
        wl_btn_row.addWidget(wl_remove_btn)
        wl_layout.addLayout(wl_btn_row)

        self.wl_list = QListWidget()
        self.wl_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.wl_list.setMinimumHeight(90)
        self.wl_list.setToolTip(
            "Queue of wordlists. Each selected handshake will be run against "
            "each wordlist in this order (hashcat's potfile automatically "
            "skips a hash once it's already been cracked, so later wordlists "
            "won't re-run work that already succeeded)."
        )
        wl_layout.addWidget(self.wl_list)

        self.wl_path_label = QLabel("No wordlists selected")
        self.wl_path_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 4px;")
        self.wl_path_label.setWordWrap(True)
        wl_layout.addWidget(self.wl_path_label)
        wl_layout.addStretch()

        self.attack_tabs.addTab(wl_widget, "Wordlist")

        # Bruteforce Tab
        bf_widget = QWidget()
        bf_layout = QVBoxLayout(bf_widget)
        bf_layout.setSpacing(10)

        charset_box, cs_layout = make_group("Character Sets")
        self.cb_digits    = QCheckBox("Numbers  (?d)  0-9")
        self.cb_lower     = QCheckBox("Lowercase (?l)  a-z")
        self.cb_upper     = QCheckBox("Uppercase (?u)  A-Z")
        self.cb_symbols   = QCheckBox("Symbols   (?s)  !@#…")
        self.cb_digits.setChecked(True)
        self.cb_lower.setChecked(True)
        for cb in (self.cb_digits, self.cb_lower, self.cb_upper, self.cb_symbols):
            cs_layout.addWidget(cb)
            cb.stateChanged.connect(self._update_mask_preview)
        bf_layout.addWidget(charset_box)

        len_box, len_layout = make_group("Password Length")
        len_row = QHBoxLayout()
        len_row.addWidget(make_label("Length:"))
        self.len_input = QLineEdit("8")
        self.len_input.setMaximumWidth(80)
        self.len_input.textChanged.connect(self._update_mask_preview)
        len_row.addWidget(self.len_input)
        len_row.addStretch()
        len_layout.addLayout(len_row)

        self.mask_preview = QLabel("Mask: ?d?l?d?l?d?l?d?l")
        self.mask_preview.setStyleSheet("color: #3fb950; font-size: 12px; padding: 4px;")
        len_layout.addWidget(self.mask_preview)
        bf_layout.addWidget(len_box)
        bf_layout.addStretch()

        self.attack_tabs.addTab(bf_widget, "Bruteforce")

        layout.addWidget(self.attack_tabs)
        self._update_mask_preview()

    def _add_wordlists(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Wordlist(s)", str(Path.home()),
            "Text Files (*.txt);;All Files (*)"
        )
        if not paths:
            return
        added = 0
        for path in paths:
            if path not in self._wordlist_paths:
                self._wordlist_paths.append(path)
                self.wl_list.addItem(QListWidgetItem(path))
                added += 1
        self._refresh_wl_label()

    def _remove_wordlists(self):
        for item in self.wl_list.selectedItems():
            path = item.text()
            if path in self._wordlist_paths:
                self._wordlist_paths.remove(path)
            self.wl_list.takeItem(self.wl_list.row(item))
        self._refresh_wl_label()

    def _refresh_wl_label(self):
        n = len(self._wordlist_paths)
        if n == 0:
            self.wl_path_label.setText("No wordlists selected")
            self.wl_path_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 4px;")
        else:
            self.wl_path_label.setText(
                f"{n} wordlist(s) queued — tried in order per handshake."
            )
            self.wl_path_label.setStyleSheet("color: #3fb950; font-size: 11px; padding: 4px;")

    # Charset sizes for keyspace calculation
    _CHARSET_SIZES = {"?d": 10, "?l": 26, "?u": 26, "?s": 33}
    _U64_MAX = 2**64 - 1  # hashcat uses uint64 for keyspace

    def _update_mask_preview(self):
        mask = self._build_mask()
        if not mask:
            self.mask_preview.setText("Mask: (select at least one charset)")
            self.mask_preview.setStyleSheet("color: #8b949e; font-size: 12px; padding: 4px;")
            return

        keyspace, overflow = self._calc_keyspace(mask)
        length = len(mask) // 2  # each token is 2 chars (?d, ?l, …)

        if overflow:
            self.mask_preview.setText(
                f"Mask: {mask}\n"
                f"Warning: integer overflow. Reduce length (max ~13 for mixed sets)."
            )
            self.mask_preview.setStyleSheet("color: #f85149; font-size: 12px; padding: 4px;")
        elif keyspace > 10**15:
            self.mask_preview.setText(
                f"Mask: {mask}\n"
                f"Warning: keyspace ~{keyspace:.2e} - this will take a very long time."
            )
            self.mask_preview.setStyleSheet("color: #d29922; font-size: 12px; padding: 4px;")
        else:
            self.mask_preview.setText(
                f"Mask: {mask}  ({keyspace:.2e} combinations)"
            )
            self.mask_preview.setStyleSheet("color: #3fb950; font-size: 12px; padding: 4px;")

    def _calc_keyspace(self, mask: str) -> tuple[int, bool]:
        """Returns (keyspace, overflow_bool). Overflow = exceeds uint64."""
        tokens = [mask[i:i+2] for i in range(0, len(mask), 2)]
        keyspace = 1
        for tok in tokens:
            size = self._CHARSET_SIZES.get(tok, 1)
            keyspace *= size
            if keyspace > self._U64_MAX:
                return 0, True
        return keyspace, False

    def _build_mask(self) -> str:
        charset = ""
        if self.cb_digits.isChecked():   charset += "?d"
        if self.cb_lower.isChecked():    charset += "?l"
        if self.cb_upper.isChecked():    charset += "?u"
        if self.cb_symbols.isChecked():  charset += "?s"

        try:
            length = max(1, int(self.len_input.text().strip()))
        except ValueError:
            length = 8

        return charset * length

    def get_mode(self) -> str:
        return "wordlist" if self.attack_tabs.currentIndex() == 0 else "bruteforce"

    def get_wordlists(self) -> list[str]:
        return list(self._wordlist_paths)

    def get_mask(self) -> tuple[str, bool]:
        """Returns (mask, overflow). Caller must check overflow before use."""
        mask = self._build_mask()
        _, overflow = self._calc_keyspace(mask) if mask else ("", False)
        return mask, overflow


# HASHCAT COMMAND BUILDER PANEL

class CommandBuilderPanel(QWidget):
    status_update = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._convert_command: str = ""
        self._hashcat_command: str = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        cmd_box, cmd_layout = make_group("Hashcat Command Builder")

        # Workload row
        wl_row = QHBoxLayout()
        wl_row.addWidget(make_label("Workload Profile:"))
        self.workload_combo = QComboBox()
        self.workload_combo.addItems(["Low", "Balanced", "High", "Extreme"])
        self.workload_combo.setCurrentText("Balanced")
        wl_row.addWidget(self.workload_combo)
        wl_row.addStretch()
        cmd_layout.addLayout(wl_row)

        cmd_layout.addWidget(separator())

        self.build_btn = make_button("BUILD COMMAND", "primary")
        self.build_btn.setMinimumHeight(40)
        cmd_layout.addWidget(self.build_btn)

        # Step 1: Convert
        self.convert_label = QLabel("Step 1 — Convert .pcap  (skip if already .hc22000)")
        self.convert_label.setStyleSheet(
            "color: #d29922; font-size: 11px; font-weight: bold; padding-top: 6px;"
        )
        cmd_layout.addWidget(self.convert_label)

        self.convert_edit = QTextEdit()
        self.convert_edit.setReadOnly(True)
        self.convert_edit.setPlaceholderText("hcxpcapngtool command will appear here...")
        self.convert_edit.setMaximumHeight(58)
        self.convert_edit.setStyleSheet(
            "QTextEdit { background: #1a1400; color: #d29922; border: 1px solid #554400;"
            " border-radius: 4px; font-family: 'Courier New'; font-size: 12px; padding: 6px; }"
        )
        cmd_layout.addWidget(self.convert_edit)

        self.copy_convert_btn = make_button("Copy Convert Command")
        self.copy_convert_btn.setEnabled(False)
        self.copy_convert_btn.clicked.connect(self._copy_convert)
        cmd_layout.addWidget(self.copy_convert_btn)

        cmd_layout.addWidget(separator())

        # Step 2: Hashcat
        self.hashcat_label = QLabel("Step 2 — Run hashcat")
        self.hashcat_label.setStyleSheet(
            "color: #3fb950; font-size: 11px; font-weight: bold; padding-top: 4px;"
        )
        cmd_layout.addWidget(self.hashcat_label)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("hashcat command will appear here...")
        self.output_edit.setMaximumHeight(58)
        cmd_layout.addWidget(self.output_edit)

        self.copy_btn = make_button("Copy hashcat Command", "success")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_hashcat)
        cmd_layout.addWidget(self.copy_btn)

        cmd_layout.addWidget(separator())

        # Step 3: Auto convert-and-go
        auto_label = QLabel("Step 3 — or just let it run")
        auto_label.setStyleSheet(
            "color: #58a6ff; font-size: 11px; font-weight: bold; padding-top: 4px;"
        )
        cmd_layout.addWidget(auto_label)

        run_row = QHBoxLayout()
        self.run_btn = make_button("Save & Run Script", "primary")
        self.run_btn.setEnabled(False)
        self.run_btn.setToolTip(
            "Writes both steps into one script and runs it here: converts "
            "any .pcap that isn't already .hc22000, then crunches every "
            "selected handshake against every queued wordlist in order."
        )
        self.run_btn.clicked.connect(self._save_and_run)
        run_row.addWidget(self.run_btn)

        self.stop_btn = make_button("Stop", "danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_run)
        run_row.addWidget(self.stop_btn)
        cmd_layout.addLayout(run_row)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Live hcxpcapngtool / hashcat output will appear here...")
        self.console.setMinimumHeight(140)
        self.console.setStyleSheet(
            "QTextEdit { background: #010409; color: #c9d1d9; border: 1px solid #30363d;"
            " border-radius: 4px; font-family: 'Courier New'; font-size: 11px; padding: 6px; }"
        )
        cmd_layout.addWidget(self.console)

        layout.addWidget(cmd_box)

    def set_build_handler(self, fn):
        self.build_btn.clicked.connect(fn)

    def set_commands(self, convert_cmd: str, hashcat_cmd: str):
        """Set convert (may be empty) and hashcat commands in separate fields."""
        self._convert_command = convert_cmd
        self._hashcat_command = hashcat_cmd

        has_convert = bool(convert_cmd)
        self.convert_edit.setPlainText(convert_cmd if has_convert else "")
        self.convert_edit.setPlaceholderText(
            "not needed - file is already .hc22000" if not has_convert
            else ""
        )
        self.copy_convert_btn.setEnabled(has_convert)
        self.convert_label.setStyleSheet(
            f"color: {'#d29922' if has_convert else '#484f58'}; "
            "font-size: 11px; font-weight: bold; padding-top: 6px;"
        )

        self.output_edit.setPlainText(hashcat_cmd)
        self.copy_btn.setEnabled(bool(hashcat_cmd))
        self.run_btn.setEnabled(bool(hashcat_cmd))

    # Backwards-compat shim
    def set_command(self, cmd: str):
        self.set_commands("", cmd)

    def _copy_convert(self):
        if self._convert_command:
            QApplication.clipboard().setText(self._convert_command)
            self.status_update.emit(
                "Convert command copied — run this in terminal FIRST, then copy hashcat command.", "warn"
            )

    def _copy_hashcat(self):
        if self._hashcat_command:
            QApplication.clipboard().setText(self._hashcat_command)
            self.status_update.emit("hashcat command copied to clipboard!", "ok")

    def get_workload(self) -> str:
        return WORKLOAD_MAP.get(self.workload_combo.currentText(), "-w 2")

    def _build_script_text(self) -> str:
        lines = ["#!/bin/bash", "set -uo pipefail", ""]
        if self._convert_command:
            lines.append("echo '=== Step 1: Converting .pcap files ==='")
            lines.append(self._convert_command)
            lines.append("")
        lines.append("echo '=== Step 2: Cracking ==='")
        lines.append(self._hashcat_command)
        lines.append("")
        return "\n".join(lines)

    def _save_and_run(self):
        if not self._hashcat_command:
            self.status_update.emit("Build a command plan first.", "warn")
            return

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        script_path = DOWNLOAD_DIR / "run_attack.sh"
        try:
            script_path.write_text(self._build_script_text())
            os.chmod(script_path, 0o755)
        except Exception as e:
            self.status_update.emit(f"Could not write script: {e}", "err")
            return

        self.console.clear()
        self.console.append(f"$ bash {script_path}\n")
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_update.emit(f"Running {script_path} — watch the console below.", "info")

        self._worker = ScriptRunWorker(str(script_path))
        self._worker.output_line.connect(self._on_output_line)
        self._worker.finished_run.connect(self._on_run_finished)
        self._worker.start()

    def _on_output_line(self, line: str):
        self.console.append(line)

    def _on_run_finished(self, returncode: int):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if returncode == 0:
            self.status_update.emit(
                "Script finished. Check the console for any cracked passwords.", "ok"
            )
        else:
            self.status_update.emit(
                f"Script exited with code {returncode} — hashcat returns "
                f"non-zero if a wordlist runs out without a match, so check "
                f"the console before assuming something's wrong.", "warn"
            )

    def _stop_run(self):
        if hasattr(self, "_worker") and self._worker.isRunning():
            self._worker.stop()
            self.console.append("\n[stopped by user]")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


# MAIN WINDOW

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pwnagotchi Manager  //  Hashcat Command Builder")
        self.setMinimumSize(900, 680)
        self.resize(1050, 740)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # Header
        header = make_label("  PWNAGOTCHI  MANAGER", bold=True, size=15)
        header.setStyleSheet("color: #58a6ff; letter-spacing: 3px; padding: 6px 0;")
        root.addWidget(header)
        root.addWidget(separator())

        # Main splitter: left = source tabs, right = attack + command
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # LEFT: Source (SSH / Local)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        source_label = make_label("  SOURCE", bold=True, size=11)
        source_label.setStyleSheet("color: #8b949e; letter-spacing: 2px;")
        left_layout.addWidget(source_label)

        self.source_tabs = QTabWidget()
        self.ssh_tab = SSHTab()
        self.local_tab = LocalTab()
        self.source_tabs.addTab(self.ssh_tab, "Pwnagotchi (SSH)")
        self.source_tabs.addTab(self.local_tab, "Local Files")

        self.ssh_tab.status_update.connect(self._set_status)
        self.local_tab.status_update.connect(self._set_status)

        left_layout.addWidget(self.source_tabs)
        splitter.addWidget(left_widget)

        # RIGHT: Attack config + Command builder
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        atk_label = make_label("  ATTACK CONFIG", bold=True, size=11)
        atk_label.setStyleSheet("color: #8b949e; letter-spacing: 2px;")
        right_layout.addWidget(atk_label)

        self.attack_panel = AttackConfigPanel()
        right_layout.addWidget(self.attack_panel)

        cmd_label = make_label("  COMMAND BUILDER", bold=True, size=11)
        cmd_label.setStyleSheet("color: #8b949e; letter-spacing: 2px;")
        right_layout.addWidget(cmd_label)

        self.cmd_panel = CommandBuilderPanel()
        self.cmd_panel.set_build_handler(self._build_command)
        self.cmd_panel.status_update.connect(self._set_status)
        right_layout.addWidget(self.cmd_panel)

        splitter.addWidget(right_widget)
        splitter.setSizes([440, 480])

        root.addWidget(splitter, stretch=1)

        # Status bar
        root.addWidget(separator())
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("status_info")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)

    # Status helper

    def _set_status(self, msg: str, level: str = "info"):
        icons = {"ok": "[OK]", "err": "[ERROR]", "warn": "[WARN]", "info": "[INFO]"}
        obj_names = {"ok": "status_ok", "err": "status_err", "warn": "status_warn", "info": "status_info"}
        self.status_label.setText(f"{icons.get(level, '[INFO]')} {msg}")
        self.status_label.setObjectName(obj_names.get(level, "status_info"))
        # Force style refresh
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    # Active file selection

    def _get_active_files(self) -> list[HandshakeFile]:
        idx = self.source_tabs.currentIndex()
        if idx == 0:
            return self.ssh_tab.get_selected_files()
        else:
            return self.local_tab.get_selected_files()

    # Build hashcat command

    def _resolve_hash_file(self, hf: "HandshakeFile") -> tuple[str, str | None]:
        """
        Returns (hash_file_path, convert_cmd_or_None).
        - For .hc22000: returns the path directly, no conversion needed.
        - For .pcap: returns the expected .hc22000 path + the hcxpcapngtool command.
        Remote files are resolved to ~/Downloads/pwn/<filename>.
        The returned hash_file_path is always the .hc22000 path to pass to hashcat.
        """
        import shlex

        # Resolve base path
        if hf.is_remote:
            base_path = DOWNLOAD_DIR / hf.filename
        else:
            base_path = Path(hf.path).expanduser().resolve()

        if hf.extension() == ".hc22000":
            return str(base_path), None

        # It's a .pcap — build conversion command + expected output path.
        # Guarded with a [ -f ... ] check so re-running the generated script
        # (e.g. after adding more wordlists) doesn't reconvert every time.
        hc_path = base_path.with_suffix(".hc22000")
        convert_cmd = (
            f"[ -f {shlex.quote(str(hc_path))} ] || hcxpcapngtool "
            f"-o {shlex.quote(str(hc_path))} {shlex.quote(str(base_path))}"
        )
        return str(hc_path), convert_cmd

    def _build_command(self):
        import shlex

        files = self._get_active_files()
        if not files:
            self._set_status("Select at least one file from the list above.", "warn")
            return

        mode = self.attack_panel.get_mode()
        workload = self.cmd_panel.get_workload()

        blocks: list[str] = []
        needs_conversion: list[str] = []
        seen_convert: set[str] = set()
        remote_warning = False

        if mode == "wordlist":
            wordlists = self.attack_panel.get_wordlists()
            if not wordlists:
                self._set_status("Add at least one wordlist first.", "warn")
                return
            wl_resolved_list = [
                str(Path(wl).expanduser().resolve()) for wl in wordlists
            ]
        else:
            mask, overflow = self.attack_panel.get_mask()
            if not mask:
                self._set_status("Select at least one character set for bruteforce.", "warn")
                return
            if overflow:
                self._set_status(
                    "Mask keyspace overflows uint64 — reduce password length!", "err"
                )
                return

        for hf in files:
            if hf.is_remote:
                remote_warning = True

            hc_path, convert_cmd = self._resolve_hash_file(hf)

            if convert_cmd and convert_cmd not in seen_convert:
                needs_conversion.append(convert_cmd)
                seen_convert.add(convert_cmd)

            if mode == "wordlist":
                blocks.append(f"echo '--- Cracking {hf.filename} ---'")
                for wl_resolved in wl_resolved_list:
                    blocks.append(
                        f"hashcat -m 22000 -a 0 {workload} "
                        f"{shlex.quote(hc_path)} {shlex.quote(wl_resolved)}"
                    )
            else:  # bruteforce
                # shlex.quote wraps mask in single quotes -> zsh-safe (?d?l etc.)
                blocks.append(
                    f"hashcat -m 22000 -a 3 {workload} "
                    f"{shlex.quote(hc_path)} {shlex.quote(mask)}"
                )

        # Two command blocks — conversion (deduped) and cracking (multi-file,
        # multi-wordlist, in order). hashcat's potfile means a hash already
        # cracked by an earlier wordlist is skipped almost instantly by later
        # wordlists, so it's safe to just run through the whole queue.
        convert_output = "\n".join(needs_conversion)
        hashcat_output = "\n".join(blocks)

        self.cmd_panel.set_commands(convert_output, hashcat_output)

        n_files = len(files)
        n_wl = len(wl_resolved_list) if mode == "wordlist" else 1
        if remote_warning:
            self._set_status(
                "Remote file(s) — paths assume ~/Downloads/pwn/. Download first!", "warn"
            )
        elif needs_conversion:
            self._set_status(
                f"Built plan for {n_files} file(s) × {n_wl} wordlist(s). "
                f"Use Save & Run to auto-convert and crunch, or copy the "
                f"commands manually.", "warn"
            )
        else:
            self._set_status(
                f"Built plan for {n_files} file(s) × {n_wl} wordlist(s) — "
                f"ready to run.", "ok"
            )


# ENTRY POINT

def main():
    # Check PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        print("ERROR: PyQt6 not installed. Run:\n  pip install PyQt6 paramiko")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    app.setApplicationName("Pwnagotchi Manager")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
