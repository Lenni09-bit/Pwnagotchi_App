"""
Pwnagotchi Handshake Manager & Hashcat Command Builder
======================================================
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

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# HANDSHAKE ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────────────────────
# DATA MODELS  (extended)
# ──────────────────────────────────────────────────────────────────────────────

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
        if ext == ".pcap":
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
            HandshakeQuality.GOOD:    "✅ GOOD",
            HandshakeQuality.WEAK:    "⚠️ WEAK",
            HandshakeQuality.FAIL:    "❌ FAIL",
            HandshakeQuality.UNKNOWN: "⏳ —",
        }.get(self.hs_quality, "—")

    def quality_color(self) -> str:
        return {
            HandshakeQuality.GOOD:    "#3fb950",
            HandshakeQuality.WEAK:    "#d29922",
            HandshakeQuality.FAIL:    "#f85149",
            HandshakeQuality.UNKNOWN: "#8b949e",
        }.get(self.hs_quality, "#8b949e")

    def list_label(self) -> str:
        prefix = "🌐" if self.is_remote else "💾"
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
            lines += ["", "⚠  This capture does not contain a valid WPA handshake.",
                      "   Try capturing again closer to the access point."]
        elif self.hs_quality == HandshakeQuality.WEAK:
            lines += ["", "⚠  Incomplete handshake — hashcat may still crack it via PMKID."]
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.list_label()

    def extension(self) -> str:
        return Path(self.filename).suffix.lower()

    def validate(self) -> "tuple[bool, str]":
        ext = self.extension()
        if self.is_remote:
            if ext not in (".pcap", ".hc22000"):
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
        elif ext != ".pcap":
            return False, f"Unsupported extension: {ext}"
        return True, "OK"


# ──────────────────────────────────────────────────────────────────────────────
# SSH WORKER THREAD
# ──────────────────────────────────────────────────────────────────────────────

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

    def set_download(self, remote_path: str, local_path: str):
        self._mode = "download"
        self._remote_path = remote_path
        self._local_path = local_path

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
            client = self._make_client()
            _, stdout, _ = client.exec_command(
                f"stat -c '%n %s' {HANDSHAKE_REMOTE_PATH}/*.pcap 2>/dev/null",
                timeout=15,
            )
            output = stdout.read().decode().strip()
            client.close()

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


# ──────────────────────────────────────────────────────────────────────────────
# REUSABLE UI HELPERS
# ──────────────────────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────────────────────
# SSH TAB
# ──────────────────────────────────────────────────────────────────────────────

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

        # ── Connection group ──────────────────────────────────────────────────
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

        self.connect_btn = make_button("🔗  Connect & Load Files", "primary")
        self.connect_btn.clicked.connect(self._connect)
        conn_layout.addWidget(self.connect_btn)

        layout.addWidget(conn_box)

        # ── File list ─────────────────────────────────────────────────────────
        files_box, files_layout = make_group("Remote Handshake Files")

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(180)
        files_layout.addWidget(self.file_list)

        self.download_btn = make_button("⬇  Download Selected", "success")
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
        self.connect_btn.setText("⏳  Connecting...")
        self.file_list.clear()
        self._loaded_files = []
        self.download_btn.setEnabled(False)
        self.status_update.emit(f"Connecting to {host}...", "info")

        self._ssh_worker = SSHWorker(host, user, password)
        self._ssh_worker.connected.connect(self._on_connected)
        self._ssh_worker.error.connect(self._on_error)
        self._ssh_worker.start()

    def _on_connected(self, file_info: list):
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("🔗  Connect & Load Files")

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
        self.connect_btn.setText("🔗  Connect & Load Files")
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
            msg = f"Downloaded {self._dl_success}/{total} file(s) → {DOWNLOAD_DIR}"
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


# ──────────────────────────────────────────────────────────────────────────────
# LOCAL FILES TAB
# ──────────────────────────────────────────────────────────────────────────────

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
        self.select_btn = make_button("📂  Select .pcap / .hc22000 Files", "primary")
        self.select_btn.clicked.connect(self._select_files)
        btn_row.addWidget(self.select_btn)

        self.analyse_btn = make_button("🔍  Analyse Selected")
        self.analyse_btn.setEnabled(False)
        self.analyse_btn.setToolTip("Run EAPOL handshake analysis on selected files")
        self.analyse_btn.clicked.connect(self._analyse_selected)
        btn_row.addWidget(self.analyse_btn)
        files_layout.addLayout(btn_row)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(160)
        files_layout.addWidget(self.file_list)

        clear_btn = make_button("🗑  Clear List")
        clear_btn.clicked.connect(self._clear)
        files_layout.addWidget(clear_btn)

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
            "Handshake Files (*.pcap *.hc22000);;All Files (*)",
        )
        if not paths:
            return

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
            self.status_update.emit(f"Added {added} file(s).", "ok")

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


# ──────────────────────────────────────────────────────────────────────────────
# ATTACK CONFIG PANEL
# ──────────────────────────────────────────────────────────────────────────────

class AttackConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._wordlist_path: str = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.attack_tabs = QTabWidget()

        # ── Wordlist Tab ──────────────────────────────────────────────────────
        wl_widget = QWidget()
        wl_layout = QVBoxLayout(wl_widget)
        wl_layout.setSpacing(10)

        wl_btn = make_button("📄  Select Wordlist (.txt)")
        wl_btn.clicked.connect(self._select_wordlist)
        wl_layout.addWidget(wl_btn)

        self.wl_path_label = QLabel("No wordlist selected")
        self.wl_path_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 4px;")
        self.wl_path_label.setWordWrap(True)
        wl_layout.addWidget(self.wl_path_label)
        wl_layout.addStretch()

        self.attack_tabs.addTab(wl_widget, "📋  Wordlist")

        # ── Bruteforce Tab ────────────────────────────────────────────────────
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

        self.attack_tabs.addTab(bf_widget, "🔢  Bruteforce")

        layout.addWidget(self.attack_tabs)
        self._update_mask_preview()

    def _select_wordlist(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist", str(Path.home()), "Text Files (*.txt);;All Files (*)"
        )
        if path:
            self._wordlist_path = path
            short = path if len(path) < 55 else "…" + path[-52:]
            self.wl_path_label.setText(short)
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
                f"⚠ Integer overflow! Reduce length (max ~13 for mixed sets)."
            )
            self.mask_preview.setStyleSheet("color: #f85149; font-size: 12px; padding: 4px;")
        elif keyspace > 10**15:
            self.mask_preview.setText(
                f"Mask: {mask}\n"
                f"⚠ Keyspace ~{keyspace:.2e} — will take very long."
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

    def get_wordlist(self) -> str:
        return self._wordlist_path

    def get_mask(self) -> tuple[str, bool]:
        """Returns (mask, overflow). Caller must check overflow before use."""
        mask = self._build_mask()
        _, overflow = self._calc_keyspace(mask) if mask else ("", False)
        return mask, overflow


# ──────────────────────────────────────────────────────────────────────────────
# HASHCAT COMMAND BUILDER PANEL
# ──────────────────────────────────────────────────────────────────────────────

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

        self.build_btn = make_button("⚡  BUILD COMMAND", "primary")
        self.build_btn.setMinimumHeight(40)
        cmd_layout.addWidget(self.build_btn)

        # ── Step 1: Convert ───────────────────────────────────────────────────
        self.convert_label = QLabel("Step 1 — Convert .pcap  (skip if already .hc22000)")
        self.convert_label.setStyleSheet(
            "color: #d29922; font-size: 11px; font-weight: bold; padding-top: 6px;"
        )
        cmd_layout.addWidget(self.convert_label)

        self.convert_edit = QTextEdit()
        self.convert_edit.setReadOnly(True)
        self.convert_edit.setPlaceholderText("→ hcxpcapngtool command will appear here…")
        self.convert_edit.setMaximumHeight(58)
        self.convert_edit.setStyleSheet(
            "QTextEdit { background: #1a1400; color: #d29922; border: 1px solid #554400;"
            " border-radius: 4px; font-family: 'Courier New'; font-size: 12px; padding: 6px; }"
        )
        cmd_layout.addWidget(self.convert_edit)

        self.copy_convert_btn = make_button("📋  Copy Convert Command")
        self.copy_convert_btn.setEnabled(False)
        self.copy_convert_btn.clicked.connect(self._copy_convert)
        cmd_layout.addWidget(self.copy_convert_btn)

        cmd_layout.addWidget(separator())

        # ── Step 2: Hashcat ───────────────────────────────────────────────────
        self.hashcat_label = QLabel("Step 2 — Run hashcat")
        self.hashcat_label.setStyleSheet(
            "color: #3fb950; font-size: 11px; font-weight: bold; padding-top: 4px;"
        )
        cmd_layout.addWidget(self.hashcat_label)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("→ hashcat command will appear here…")
        self.output_edit.setMaximumHeight(58)
        cmd_layout.addWidget(self.output_edit)

        self.copy_btn = make_button("📋  Copy hashcat Command", "success")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_hashcat)
        cmd_layout.addWidget(self.copy_btn)

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
            "→ not needed — file is already .hc22000" if not has_convert
            else ""
        )
        self.copy_convert_btn.setEnabled(has_convert)
        self.convert_label.setStyleSheet(
            f"color: {'#d29922' if has_convert else '#484f58'}; "
            "font-size: 11px; font-weight: bold; padding-top: 6px;"
        )

        self.output_edit.setPlainText(hashcat_cmd)
        self.copy_btn.setEnabled(bool(hashcat_cmd))

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


# ──────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────────────────────────────────────

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

        # ── LEFT: Source (SSH / Local) ────────────────────────────────────────
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
        self.source_tabs.addTab(self.ssh_tab, "🌐  Pwnagotchi (SSH)")
        self.source_tabs.addTab(self.local_tab, "💾  Local Files")

        self.ssh_tab.status_update.connect(self._set_status)
        self.local_tab.status_update.connect(self._set_status)

        left_layout.addWidget(self.source_tabs)
        splitter.addWidget(left_widget)

        # ── RIGHT: Attack config + Command builder ────────────────────────────
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

    # ── Status helper ──────────────────────────────────────────────────────────

    def _set_status(self, msg: str, level: str = "info"):
        icons = {"ok": "✅", "err": "❌", "warn": "⚠️", "info": "ℹ️"}
        obj_names = {"ok": "status_ok", "err": "status_err", "warn": "status_warn", "info": "status_info"}
        self.status_label.setText(f"{icons.get(level, 'ℹ️')}  {msg}")
        self.status_label.setObjectName(obj_names.get(level, "status_info"))
        # Force style refresh
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    # ── Active file selection ──────────────────────────────────────────────────

    def _get_active_files(self) -> list[HandshakeFile]:
        idx = self.source_tabs.currentIndex()
        if idx == 0:
            return self.ssh_tab.get_selected_files()
        else:
            return self.local_tab.get_selected_files()

    # ── Build hashcat command ──────────────────────────────────────────────────

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

        # It's a .pcap — build conversion command + expected output path
        hc_path = base_path.with_suffix(".hc22000")
        convert_cmd = (
            f"hcxpcapngtool -o {shlex.quote(str(hc_path))} "
            f"{shlex.quote(str(base_path))}"
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
        remote_warning = False

        for hf in files:
            if hf.is_remote:
                remote_warning = True

            hc_path, convert_cmd = self._resolve_hash_file(hf)

            if convert_cmd:
                needs_conversion.append(convert_cmd)

            # Build the hashcat command
            if mode == "wordlist":
                wordlist = self.attack_panel.get_wordlist()
                if not wordlist:
                    self._set_status("Select a wordlist file first.", "warn")
                    return
                wl_resolved = str(Path(wordlist).expanduser().resolve())
                cmd = (
                    f"hashcat -m 22000 -a 0 {workload} "
                    f"{shlex.quote(hc_path)} {shlex.quote(wl_resolved)}"
                )
            else:  # bruteforce
                mask, overflow = self.attack_panel.get_mask()
                if not mask:
                    self._set_status("Select at least one character set for bruteforce.", "warn")
                    return
                if overflow:
                    self._set_status(
                        "Mask keyspace overflows uint64 — reduce password length!", "err"
                    )
                    return
                # shlex.quote wraps mask in single quotes -> zsh-safe (?d?l etc.)
                cmd = (
                    f"hashcat -m 22000 -a 3 {workload} "
                    f"{shlex.quote(hc_path)} {shlex.quote(mask)}"
                )
            blocks.append(cmd)

        # Two separate commands
        convert_output = "\n".join(needs_conversion)
        hashcat_output = "\n".join(blocks)

        self.cmd_panel.set_commands(convert_output, hashcat_output)

        if remote_warning:
            self._set_status(
                "Remote file(s) — paths assume ~/Downloads/pwn/. Download first!", "warn"
            )
        elif needs_conversion:
            self._set_status(
                "Copy & run Step 1 first (convert), then copy & run Step 2 (hashcat).", "warn"
            )
        else:
            self._set_status("Command built — copy and run in terminal!", "ok")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

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
