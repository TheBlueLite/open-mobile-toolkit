from PyQt6.QtCore import QThread, pyqtSignal
from core.adb_manager import ADBManager
from core.loke_manager import LokeManager

class ADBWorker(QThread):
    log_signal = pyqtSignal(str)
    device_info_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(bool)

    def __init__(self, action: str, device_id: str = None, mode: str = None):
        super().__init__()
        self.adb = ADBManager()
        self.loke = LokeManager()
        self.action = action
        self.device_id = device_id
        self.mode = mode

    def run(self):
        if self.action == "read_device":
            self.log_signal.emit("\n[+] Buscando dispositivos ADB...")
            devices = self.adb.get_devices()
            if devices:
                dev_id = devices[0]
                self.log_signal.emit(f"[+] Dispositivo encontrado: {dev_id}")
                info = self.adb.get_device_info(dev_id)
                info["dev_id"] = dev_id
                self.device_info_signal.emit(info)
                self.finished_signal.emit(True)
            else:
                self.log_signal.emit("[-] No se detectó ningún dispositivo ADB activo.")
                self.finished_signal.emit(False)

        elif self.action == "read_modem":
            if self.device_id:
                self.log_signal.emit("\n[+] Leyendo parámetros de módem vía ADB...")
                modem_data = self.adb.get_modem_info(self.device_id)
                for k, v in modem_data.items():
                    self.log_signal.emit(f"  - {k}: {v}")
            self.finished_signal.emit(True)

        elif self.action == "read_download":
            self.log_signal.emit("\n[+] Escaneando bus USB en busca de Samsung en Modo Download...")
            res = self.loke.find_download_device()
            if res["status"]:
                self.log_signal.emit(f"[+] Dispositivo Samsung detectado: PID {res['pid']} (VID {res['vid']})")
                if self.loke.init_loke_session():
                    self.log_signal.emit("[+] Interfaz USB Loke inicializada correctamente.")
                else:
                    self.log_signal.emit("[!] Dispositivo detectado en el sistema (requiere driver LibUSB/WinUSB en Windows para control USB directo).")
                self.finished_signal.emit(True)
            else:
                self.log_signal.emit(f"[-] {res['message']}")
                self.finished_signal.emit(False)

        elif self.action == "reboot":
            if self.device_id and self.mode:
                self.log_signal.emit(f"\n[➔] Reiniciando dispositivo en modo '{self.mode}'...")
                self.adb.reboot_to(self.device_id, self.mode)
                self.log_signal.emit(f"[+] Comando enviado exitosamente.")
            self.finished_signal.emit(True)