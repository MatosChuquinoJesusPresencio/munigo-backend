from sqlmodel import SQLModel, Field


class Empleado(SQLModel, table=True):
    __tablename__ = "empleados"

    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id")
    nombres: str
    apellidos: str
    cargo: str
    area: str
