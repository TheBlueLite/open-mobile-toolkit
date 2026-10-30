import subprocess
import os

class ADBManager:
    def __init__(self, tools_dir=None):
        if tools_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.adb_path = os.path.join(base_dir, "tools", "win", "adb.exe")
        else:
            self.adb_path = tools_dir

    def _execute(self, command: str) -> str:
        try:
            full_cmd = f'"{self.adb_path}" {command}'
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error al ejecutar ADB: {str(e)}"

    def check_connection(self) -> bool:
        return os.path.exists(self.adb_path)

    def get_devices(self) -> list:
        output = self._execute("devices")
        lines = output.splitlines()
        devices = []
        for line in lines[1:]:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices

    def get_device_info(self, device_id: str) -> dict:
        props = {
            "Modelo": f"-s {device_id} shell getprop ro.product.model",
            "Marca": f"-s {device_id} shell getprop ro.product.brand",
            "Versión Android": f"-s {device_id} shell getprop ro.build.version.release",
            "Parche de Seguridad": f"-s {device_id} shell getprop ro.build.version.security_patch",
            "Procesador": f"-s {device_id} shell getprop ro.board.platform"
        }
        
        info = {}
        for key, cmd in props.items():
            info[key] = self._execute(cmd)
        return info

    def get_modem_info(self, device_id: str) -> dict:
        """Extrae datos del módem y la red celular vía ADB Shell."""
        props = {
            "Baseband (Firma Módem)": f"-s {device_id} shell getprop gsm.version.baseband",
            "Estado Tarjeta SIM": f"-s {device_id} shell getprop gsm.sim.state",
            "Operadora Detectada": f"-s {device_id} shell getprop gsm.operator.alpha",
            "Tipo de Red": f"-s {device_id} shell getprop gsm.network.type"
        }
        
        results = {}
        for key, cmd in props.items():
            val = self._execute(cmd)
            results[key] = val if val else "No disponible"
        return results

    def reboot_to(self, device_id: str, mode: str) -> str:
        return self._execute(f"-s {device_id} reboot {mode}")