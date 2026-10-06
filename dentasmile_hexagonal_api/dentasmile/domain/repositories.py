"""
PUERTOS (Ports) de salida
---------------------------
Contratos abstractos que el dominio y los casos de uso necesitan.
Nadie aqui sabe que existe Django ORM: la implementacion concreta
esta en infrastructure/repositories.py.
"""

from abc import ABC, abstractmethod
from datetime import date, time
from typing import List, Optional

from .entities import Tratamiento, Cita


class TratamientoRepository(ABC):

    @abstractmethod
    def listar(self) -> List[Tratamiento]:
        ...

    @abstractmethod
    def obtener_por_id(self, tratamiento_id: int) -> Optional[Tratamiento]:
        ...

    @abstractmethod
    def existe_nombre(self, nombre: str, excluir_id: Optional[int] = None) -> bool:
        ...

    @abstractmethod
    def tiene_citas(self, tratamiento_id: int) -> bool:
        ...

    @abstractmethod
    def guardar(self, tratamiento: Tratamiento) -> Tratamiento:
        """Crea si no tiene id, actualiza si ya existe."""
        ...

    @abstractmethod
    def eliminar(self, tratamiento_id: int) -> bool:
        ...


class CitaRepository(ABC):

    @abstractmethod
    def listar(self) -> List[Cita]:
        ...

    @abstractmethod
    def obtener_por_id(self, cita_id: int) -> Optional[Cita]:
        ...

    @abstractmethod
    def existe_cita_en_horario(self, fecha: date, hora: time,
                               excluir_id: Optional[int] = None) -> bool:
        """True si ya hay una cita NO cancelada en esa fecha y hora."""
        ...

    @abstractmethod
    def guardar(self, cita: Cita) -> Cita:
        """Crea si no tiene id, actualiza si ya existe."""
        ...

    @abstractmethod
    def eliminar(self, cita_id: int) -> bool:
        ...
