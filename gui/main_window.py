import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QGroupBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from core.adb_manager import ADBManager
from core.serial_manager import SerialManager
from gui.workers import ADBWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.adb = ADBManager()
        self.serial = SerialManager()
        self.current_device = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Open Mobile Toolkit - v0.1")
        self.resize(900, 620)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QGroupBox { color: #cdd6f4; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QLabel { color: #cdd6f4; font-size: 13px; }
            QComboBox, QLineEdit { 
                background-color: #11111b; color: #cdd6f4; border: 1px solid #45475a; 
                padding: 5px; border-radius: 4px; 
            }
            QPushButton { 
                background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; 
                padding: 7px 12px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:pressed { background-color: #89b4fa; color: #11111b; }
            QPushButton:disabled { background-color: #181825; color: #585b70; border: 1px solid #313244; }
            QTextEdit { 
                background-color: #11111b; color: #a6e3a1; border: 1px solid #313244; 
                font-family: 'Consolas', monospace; font-size: 12px; border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Barra Superior
        top_bar = QHBoxLayout()
        self.btn_refresh = QPushButton("🔍 Leer Dispositivo (ADB)")
        self.btn_refresh.clicked.connect(self.read_adb_device)
        
        self.lbl_status = QLabel("Estado: Esperando acción...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_status)
        main_layout.addLayout(top_bar)

        # Cuerpo Central
        body_layout = QHBoxLayout()
        left_panel = QVBoxLayout()

        # Grupo 1: Datos ADB
        info_group = QGroupBox("Datos ADB")
        info_layout = QVBoxLayout(info_group)
        self.lbl_model = QLabel("Modelo: -")
        self.lbl_brand = QLabel("Marca: -")
        self.lbl_cpu = QLabel("Procesador: -")
        info_layout.addWidget(self.lbl_model)
        info_layout.addWidget(self.lbl_brand)
        info_layout.addWidget(self.lbl_cpu)
        left_panel.addWidget(info_group)

        # Grupo 2: Acciones ADB y Módem
        actions_group = QGroupBox("Acciones ADB / Módem")
        actions_layout = QVBoxLayout(actions_group)
        
        self.btn_read_modem = QPushButton("📶 Leer Módem por ADB")
        self.btn_read_modem.setEnabled(False)
        self.btn_read_modem.clicked.connect(self.read_modem_info)

        self.btn_reboot_download = QPushButton("🔄 Modo Download")
        self.btn_reboot_download.setEnabled(False)
        self.btn_reboot_download.clicked.connect(lambda: self.reboot_device("download"))
        
        self.btn_reboot_recovery = QPushButton("🛠️ Modo Recovery")
        self.btn_reboot_recovery.setEnabled(False)
        self.btn_reboot_recovery.clicked.connect(lambda: self.reboot_device("recovery"))

        # Nuevo botón para escanear Modo Download directamente vía USB
        self.btn_check_download = QPushButton("⚡ Escanear Modo Download")
        self.btn_check_download.clicked.connect(self.check_download_mode)

        actions_layout.addWidget(self.btn_read_modem)
        actions_layout.addWidget(self.btn_reboot_download)
        actions_layout.addWidget(self.btn_reboot_recovery)
        actions_layout.addWidget(self.btn_check_download)
        left_panel.addWidget(actions_group)

        # Grupo 3: Puerto Serie / Comandos AT
        serial_group = QGroupBox("Conexión Puerto Serie (COM)")
        serial_layout = QVBoxLayout(serial_group)

        port_box = QHBoxLayout()
        self.combo_ports = QComboBox()
        self.btn_scan_ports = QPushButton("🔄 Escanear")
        self.btn_scan_ports.clicked.connect(self.scan_ports)
        port_box.addWidget(self.combo_ports, stretch=2)
        port_box.addWidget(self.btn_scan_ports, stretch=1)
        serial_layout.addLayout(port_box)

        at_box = QHBoxLayout()
        self.input_at = QLineEdit()
        self.input_at.setPlaceholderText("Ej: AT")
        self.btn_send_at = QPushButton("Enviar AT")
        self.btn_send_at.clicked.connect(self.send_at)
        at_box.addWidget(self.input_at, stretch=2)
        at_box.addWidget(self.btn_send_at, stretch=1)
        serial_layout.addLayout(at_box)

        left_panel.addWidget(serial_group)
        body_layout.addLayout(left_panel, stretch=1)

        # Panel Derecho: Consola
        log_group = QGroupBox("Consola de Procesos")
        log_layout = QVBoxLayout(log_group)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console)

        body_layout.addWidget(log_group, stretch=2)
        main_layout.addLayout(body_layout)

        self.scan_ports()
        self.log("=== Open Mobile Toolkit Inicializado ===")

    def log(self, text: str):
        self.log_console.append(text)

    def scan_ports(self):
        self.combo_ports.clear()
        ports = SerialManager.list_ports()
        if ports:
            for p in ports:
                self.combo_ports.addItem(f"{p['port']} - {p['description']}", p['port'])
            self.log("[+] Puertos COM detectados.")
        else:
            self.combo_ports.addItem("No hay puertos COM disponibles")
            self.log("[-] No se detectaron puertos serie activos.")

    def send_at(self):
        selected_port = self.combo_ports.currentData()
        command = self.input_at.text().strip()

        if not selected_port or selected_port == "No hay puertos COM disponibles":
            self.log("[-] Selecciona un puerto COM válido.")
            return

        if not command:
            command = "AT"

        self.log(f"\n[➔] Abriendo {selected_port} y enviando: {command}")
        
        if self.serial.connect(selected_port):
            response = self.serial.send_at_command(command)
            self.log(f"[+] Respuesta del Puerto:\n{response}")
            self.serial.disconnect()
        else:
            self.log(f"[-] No se pudo abrir el puerto {selected_port}.")

    def read_adb_device(self):
        self.btn_refresh.setEnabled(False)
        self.lbl_status.setText("Estado: Leyendo dispositivo...")
        
        # Iniciar Worker en segundo plano
        self.worker = ADBWorker(action="read_device")
        self.worker.log_signal.connect(self.log)
        self.worker.device_info_signal.connect(self.update_device_ui)
        self.worker.finished_signal.connect(self.on_adb_finished)
        self.worker.start()

    def update_device_ui(self, info: dict):
        self.current_device = info.get("dev_id")
        self.lbl_model.setText(f"Modelo: {info.get('Modelo', '-')}")
        self.lbl_brand.setText(f"Marca: {info.get('Marca', '-')}")
        self.lbl_cpu.setText(f"Procesador: {info.get('Procesador', '-')}")
        self.lbl_status.setText(f"Conectado: {info.get('Modelo', self.current_device)}")
        
        self.btn_read_modem.setEnabled(True)
        self.btn_reboot_download.setEnabled(True)
        self.btn_reboot_recovery.setEnabled(True)

    def on_adb_finished(self, success: bool):
        self.btn_refresh.setEnabled(True)
        if not success:
            self.lbl_status.setText("Estado: Sin dispositivo")
            self.current_device = None
            self.btn_read_modem.setEnabled(False)
            self.btn_reboot_download.setEnabled(False)
            self.btn_reboot_recovery.setEnabled(False)

    def read_modem_info(self):
        if not self.current_device:
            return
        
        self.btn_read_modem.setEnabled(False)
        self.worker = ADBWorker(action="read_modem", device_id=self.current_device)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(lambda: self.btn_read_modem.setEnabled(True))
        self.worker.start()

    def reboot_device(self, mode: str):
        if not self.current_device:
            return

        self.lbl_status.setText("Estado: Reiniciando...")
        self.worker = ADBWorker(action="reboot", device_id=self.current_device, mode=mode)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(lambda: self.on_adb_finished(False))
        self.worker.start()

    def check_download_mode(self):
        self.worker = ADBWorker(action="read_download")
        self.worker.log_signal.connect(self.log)
        self.worker.start()