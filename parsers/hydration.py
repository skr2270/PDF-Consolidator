"""Cloud hydration check: verifies files are fully downloaded."""
import os

class CloudHydrationChecker:
    """Verifies files in cloud-synced folders (OneDrive / Google Drive) are hydrated."""

    @staticmethod
    def is_hydrated(file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            size = os.path.getsize(file_path)
            if size == 0:
                return False
            with open(file_path, "rb") as f:
                header = f.read(1024)
                if not header.startswith(b"%PDF-"):
                    return False
            return True
        except Exception:
            return False
