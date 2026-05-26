import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings


class LocalStorage:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self._ensure_base_dir()

    def _ensure_base_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1].lower().lstrip(".")

    def _generate_unique_filename(self, original_filename: str, subdir: str = "") -> str:
        ext = self._get_extension(original_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        name_without_ext = os.path.splitext(os.path.basename(original_filename))[0]
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name_without_ext)
        
        new_filename = f"{safe_name}_{timestamp}_{unique_id}.{ext}" if ext else f"{safe_name}_{timestamp}_{unique_id}"
        
        if subdir:
            return os.path.join(subdir, new_filename)
        return new_filename

    def validate(
        self,
        filename: str,
        allowed_types: str = None,
        max_size_bytes: int = None
    ) -> None:
        ext = self._get_extension(filename)
        
        if allowed_types:
            allowed_list = [t.strip().lower().lstrip(".") for t in allowed_types.split(",")]
            if ext not in allowed_list and "*" not in allowed_list:
                raise ValueError(
                    f"Tipo de archivo no permitido. Extensiones permitidas: {allowed_types}"
                )
        
        if max_size_bytes is None:
            if ext.lower() in ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]:
                pass
            else:
                pass

    def save(
        self,
        content: bytes,
        filename: str,
        subdir: str = ""
    ) -> str:
        if subdir:
            subdir_path = self.base_dir / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
        
        relative_path = self._generate_unique_filename(filename, subdir)
        full_path = self.base_dir / relative_path
        
        with open(full_path, "wb") as f:
            f.write(content)
        
        return relative_path.replace("\\", "/")

    def get_url(self, relative_path: str) -> str:
        return f"/static/uploads/{relative_path}"

    def get_full_path(self, relative_path: str) -> Path:
        return self.base_dir / relative_path

    def delete(self, relative_path: str) -> bool:
        try:
            full_path = self.base_dir / relative_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False

    def exists(self, relative_path: str) -> bool:
        full_path = self.base_dir / relative_path
        return full_path.exists()

    def get_file_size(self, relative_path: str) -> int:
        full_path = self.base_dir / relative_path
        if full_path.exists():
            return full_path.stat().st_size
        return 0


storage = LocalStorage()
