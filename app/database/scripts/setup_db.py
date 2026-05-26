from typing import Tuple

from app.database.scripts.init_db import initialize_database
from app.database.scripts.seed_data import seed_all


def setup_database() -> Tuple[bool, str, int, bool]:
    try:
        success_init, message_init = initialize_database()
        if not success_init:
            return False, message_init, 0, False
        
        success_seed, message_seed, count_requisitos, admin_creado = seed_all()
        if not success_seed:
            return False, message_seed, 0, False
        
        return True, "Base de datos configurada exitosamente", count_requisitos, admin_creado
    except Exception as e:
        return False, f"Error en configuración: {str(e)}", 0, False


if __name__ == "__main__":
    success, message, count, admin_created = setup_database()
    if success:
        exit(0)
    else:
        exit(1)
