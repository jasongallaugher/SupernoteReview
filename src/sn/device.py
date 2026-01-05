import adbutils
import os
from pathlib import Path

class SupernoteDevice:
    def __init__(self):
        self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        self.device = self._get_device()

    def _get_device(self):
        devices = self.adb.device_list()
        if not devices:
            raise Exception("No ADB devices found. Ensure your Supernote is connected via wireless ADB (adb connect <ip>).")
        
        if len(devices) == 1:
            return devices[0]
            
        # If multiple, prefer the one that looks like an IP address (wireless)
        for d in devices:
            if "." in d.serial and ":" in d.serial:
                return d
                
        # Fallback to the first one
        return devices[0]

    def ensure_dir(self, remote_dir):
        # adbutils doesn't have a direct mkdir -p, we'll use shell
        self.device.shell(f"mkdir -p {remote_dir}")

    def push(self, local_path, remote_path):
        remote_dir = os.path.dirname(remote_path)
        self.ensure_dir(remote_dir)
        self.device.sync.push(local_path, remote_path)

    def pull(self, remote_path, local_path):
        self.device.sync.pull(remote_path, local_path)

    def exists(self, remote_path):
        # Check if file exists on device
        res = self.device.shell(f"ls {remote_path}")
        return "No such file" not in res

    def open_pdf(self, remote_path):
        """
        Opens the specified PDF in the native Supernote viewer.
        """
        # Supernote prefers /sdcard/ path in intents sometimes
        uri_path = remote_path.replace("/storage/emulated/0/", "/sdcard/")
        
        cmd = (
            f"am start -a android.intent.action.VIEW "
            f"-d \"file://{uri_path}\" "
            f"-n com.supernote.document/.MainActivity"
        )
        return self.device.shell(cmd)

    def list_dir(self, remote_dir):
        """Returns a list of filenames in the directory."""
        res = self.device.shell(f"ls {remote_dir}")
        if "No such file" in res:
            return []
        return [f.strip() for f in res.splitlines() if f.strip()]
