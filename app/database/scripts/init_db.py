from typing import Tuple

from app.database.connection import create_db_and_tables, _ensure_data_dir
from app.core.storage import storage


def initialize_database() -> Tuple[bool, str]:
    try:
        _ensure_data_dir()
        create_db_and_tables()
        return True, "Tablas creadas exitosamente"
    except Exception as e:
        return False, f"Error al inicializar la base de datos: {str(e)}"


if __name__ == "__main__":
    success, message = initialize_database()
    if success:
        exit(0)
    else:
        exit(1)
