"""
APPLICATION RING (Casos de uso)
---------------------------------
Aqui vive la LOGICA DE NEGOCIO de DentaSmile. Cada caso de uso recibe
los repositorios (puertos) por constructor -> inyeccion de dependencias.
No importa Django, DRF ni HTTP.

Reglas de negocio implementadas:
  - No puede haber dos tratamientos con el mismo nombre.
  - No se puede eliminar un tratamiento que ya tiene citas.
  - Una cita debe apuntar a un tratamiento que exista.
  - No puede haber dos citas activas (no canceladas) en la misma fecha y hora.
"""

from typing import List

from dentasmile.domain.entities import Tratamiento, Cita
from dentasmile.domain.repositories import TratamientoRepository, CitaRepository
from .exceptions import (
    TratamientoNoEncontradoError, NombreTratamientoDuplicadoError,
    TratamientoConCitasError, CitaNoEncontradaError,
    TratamientoInvalidoError, HorarioOcupadoError,
)


# =====================================================================
#  TRATAMIENTO (entidad principal)
# =====================================================================

class ListarTratamientosUseCase:
    def __init__(self, repo: TratamientoRepository):
        self.repo = repo

    def ejecutar(self) -> List[Tratamiento]:
        return self.repo.listar()


class ObtenerTratamientoUseCase:
    def __init__(self, repo: TratamientoRepository):
        self.repo = repo

    def ejecutar(self, tratamiento_id: int) -> Tratamiento:
        t = self.repo.obtener_por_id(tratamiento_id)
        if t is None:
            raise TratamientoNoEncontradoError(
                f"No existe un tratamiento con id {tratamiento_id}")
        return t


class CrearTratamientoUseCase:
    def __init__(self, repo: TratamientoRepository):
        self.repo = repo

    def ejecutar(self, datos: dict) -> Tratamiento:
        if self.repo.existe_nombre(datos["nombre"]):
            raise NombreTratamientoDuplicadoError(
                f"Ya existe un tratamiento llamado '{datos['nombre']}'")
        t = Tratamiento(
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion", ""),
            precio=datos.get("precio", 0),
        )
        return self.repo.guardar(t)


class ActualizarTratamientoUseCase:
    def __init__(self, repo: TratamientoRepository):
        self.repo = repo

    def ejecutar(self, tratamiento_id: int, datos: dict) -> Tratamiento:
        t = self.repo.obtener_por_id(tratamiento_id)
        if t is None:
            raise TratamientoNoEncontradoError(
                f"No existe un tratamiento con id {tratamiento_id}")

        nuevo_nombre = datos.get("nombre", t.nombre)
        if self.repo.existe_nombre(nuevo_nombre, excluir_id=t.id):
            raise NombreTratamientoDuplicadoError(
                f"Ya existe un tratamiento llamado '{nuevo_nombre}'")

        t.nombre = nuevo_nombre
        t.descripcion = datos.get("descripcion", t.descripcion)
        t.precio = datos.get("precio", t.precio)
        return self.repo.guardar(t)


class EliminarTratamientoUseCase:
    def __init__(self, repo: TratamientoRepository):
        self.repo = repo

    def ejecutar(self, tratamiento_id: int) -> None:
        if self.repo.obtener_por_id(tratamiento_id) is None:
            raise TratamientoNoEncontradoError(
                f"No existe un tratamiento con id {tratamiento_id}")
        if self.repo.tiene_citas(tratamiento_id):
            raise TratamientoConCitasError(
                "No se puede eliminar: el tratamiento tiene citas asociadas")
        self.repo.eliminar(tratamiento_id)


# =====================================================================
#  CITA (entidad secundaria)
# =====================================================================

class ListarCitasUseCase:
    def __init__(self, repo: CitaRepository):
        self.repo = repo

    def ejecutar(self) -> List[Cita]:
        return self.repo.listar()


class ObtenerCitaUseCase:
    def __init__(self, repo: CitaRepository):
        self.repo = repo

    def ejecutar(self, cita_id: int) -> Cita:
        c = self.repo.obtener_por_id(cita_id)
        if c is None:
            raise CitaNoEncontradaError(f"No existe una cita con id {cita_id}")
        return c


class CrearCitaUseCase:
    def __init__(self, repo: CitaRepository, tratamiento_repo: TratamientoRepository):
        self.repo = repo
        self.tratamiento_repo = tratamiento_repo

    def ejecutar(self, datos: dict) -> Cita:
        if self.tratamiento_repo.obtener_por_id(datos["tratamiento_id"]) is None:
            raise TratamientoInvalidoError(
                f"El tratamiento {datos['tratamiento_id']} no existe")

        cita = Cita(
            paciente_nombre=datos["paciente_nombre"],
            paciente_telefono=datos["paciente_telefono"],
            tratamiento_id=datos["tratamiento_id"],
            fecha=datos["fecha"],
            hora=datos["hora"],
            estado=datos.get("estado", "pendiente"),
        )
        if cita.ocupa_horario() and self.repo.existe_cita_en_horario(cita.fecha, cita.hora):
            raise HorarioOcupadoError(
                f"Ya hay una cita el {cita.fecha} a las {cita.hora:%H:%M}")
        return self.repo.guardar(cita)


class ActualizarCitaUseCase:
    def __init__(self, repo: CitaRepository, tratamiento_repo: TratamientoRepository):
        self.repo = repo
        self.tratamiento_repo = tratamiento_repo

    def ejecutar(self, cita_id: int, datos: dict) -> Cita:
        cita = self.repo.obtener_por_id(cita_id)
        if cita is None:
            raise CitaNoEncontradaError(f"No existe una cita con id {cita_id}")

        cita.paciente_nombre = datos.get("paciente_nombre", cita.paciente_nombre)
        cita.paciente_telefono = datos.get("paciente_telefono", cita.paciente_telefono)
        cita.tratamiento_id = datos.get("tratamiento_id", cita.tratamiento_id)
        cita.fecha = datos.get("fecha", cita.fecha)
        cita.hora = datos.get("hora", cita.hora)
        cita.estado = datos.get("estado", cita.estado)

        if self.tratamiento_repo.obtener_por_id(cita.tratamiento_id) is None:
            raise TratamientoInvalidoError(
                f"El tratamiento {cita.tratamiento_id} no existe")
        if cita.ocupa_horario() and self.repo.existe_cita_en_horario(
                cita.fecha, cita.hora, excluir_id=cita.id):
            raise HorarioOcupadoError(
                f"Ya hay una cita el {cita.fecha} a las {cita.hora:%H:%M}")
        return self.repo.guardar(cita)


class EliminarCitaUseCase:
    def __init__(self, repo: CitaRepository):
        self.repo = repo

    def ejecutar(self, cita_id: int) -> None:
        if not self.repo.eliminar(cita_id):
            raise CitaNoEncontradaError(f"No existe una cita con id {cita_id}")
