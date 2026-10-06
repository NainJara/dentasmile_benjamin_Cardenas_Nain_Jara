"""
DOMINIO (Core Domain)
-----------------------
Entidades de negocio PURAS de DentaSmile. No heredan de models.Model,
no importan Django ni DRF: son dataclasses de Python. Hay DOS entidades:

  1. Tratamiento (entidad principal / catalogo)
  2. Cita        (entidad secundaria / documento transaccional)

La relacion entre ambas (Cita -> Tratamiento) se expresa aqui solo con
el campo tratamiento_id; la ForeignKey real vive en infrastructure/models.py.
"""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

ESTADOS_CITA = ("pendiente", "confirmada", "cancelada")


@dataclass
class Tratamiento:
    nombre: str
    descripcion: str = ""
    precio: int = 0                       # precio "desde", en pesos chilenos
    id: Optional[int] = None


@dataclass
class Cita:
    paciente_nombre: str                  # antes: paciente.nombre (subdocumento Mongo)
    paciente_telefono: str                # antes: paciente.telefono
    tratamiento_id: int                   # ForeignKey hacia Tratamiento
    fecha: date
    hora: time
    estado: str = "pendiente"
    id: Optional[int] = None
    tratamiento_nombre: Optional[str] = None   # solo lectura, lo rellena el repositorio

    def ocupa_horario(self) -> bool:
        """Regla de negocio pura: una cita cancelada libera su horario."""
        return self.estado != "cancelada"
