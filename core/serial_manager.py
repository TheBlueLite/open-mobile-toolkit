import serial
import serial.tools.list_ports
import time

class SerialManager:
    def __init__(self):
        self.connection = None

    @staticmethod
    def list_ports() -> list:
        """Devuelve una lista de diccionarios con los puertos COM disponibles."""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port in ports:
            available_ports.append({
                "port": port.device,          # Ej: "COM5"
                "description": port.description, # Ej: "SAMSUNG Mobile USB Serial Port"
                "hardware_id": port.hwid
            })
        return available_ports

    def connect(self, port_name: str, baudrate: int = 115200, timeout: float = 1.5) -> bool:
        """Abre la conexión con el puerto serie especificado."""
        try:
            self.connection = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout,
                rtscts=False,
                dsrdtr=False
            )
            return self.connection.is_open
        except Exception as e:
            print(f"[-] Error al conectar con {port_name}: {e}")
            return False

    def disconnect(self):
        """Cierra el puerto serie si está abierto."""
        if self.connection and self.connection.is_open:
            self.connection.close()

    def send_at_command(self, command: str, wait_time: float = 1.0) -> str:
        """Envía un comando AT y recupera la respuesta devuelta por el módem."""
        if not self.connection or not self.connection.is_open:
            return "[-] Error: El puerto no está abierto."

        try:
            # Limpiar búfer previo de entrada/salida
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()

            # Enviar comando con salto de línea estándar (\r\n)
            full_cmd = f"{command}\r\n"
            self.connection.write(full_cmd.encode('utf-8'))
            
            # Esperar a que el hardware de Samsung procese el comando
            time.sleep(wait_time)
            
            # Leer todos los bytes recibidos
            bytes_to_read = self.connection.in_waiting
            if bytes_to_read > 0:
                raw_response = self.connection.read(bytes_to_read)
                response = raw_response.decode('utf-8', errors='ignore').strip()
                return response if response else "[!] El puerto respondió pero devolvió caracteres vacíos."
            else:
                return "[-] Sin respuesta (Timeout): El puerto no devolvió datos."

        except Exception as e:
            return f"[-] Error durante la transmisión: {str(e)}"