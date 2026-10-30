import usb.core
import usb.util
import struct

class LokeManager:
    # Vendor ID de Samsung Electronics
    SAMSUNG_VID = 0x04e8
    
    # Product IDs conocidos en Modo Download (Odin/Loke)
    DOWNLOAD_PIDS = [0x6601, 0x685d, 0x68c0, 0x6860]

    def __init__(self):
        self.device = None
        self.out_endpoint = None
        self.in_endpoint = None

    def find_download_device(self) -> dict:
        """Busca dispositivos Samsung en modo Download conectados por USB."""
        for pid in self.DOWNLOAD_PIDS:
            dev = usb.core.find(idVendor=self.SAMSUNG_VID, idProduct=pid)
            if dev is not None:
                self.device = dev
                return {
                    "status": True,
                    "vid": hex(self.SAMSUNG_VID),
                    "pid": hex(pid),
                    "product": "Samsung Download/Odin Device"
                }
        return {"status": False, "message": "No se detectó ningún dispositivo Samsung en modo Download."}

    def init_loke_session(self) -> bool:
        """Inicializa los endpoints USB para intercambiar paquetes con Loke."""
        if not self.device:
            return False

        try:
            self.device.set_configuration()
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]

            # Mapear endpoints BULK de entrada y salida
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self.out_endpoint = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.in_endpoint = ep

            return bool(self.out_endpoint and self.in_endpoint)
        except Exception as e:
            print(f"[-] Error configurando sesión USB Loke: {e}")
            return False