"""
ADAPTADORES SECUNDARIOS (Driven Adapters)
-------------------------------------------
Implementaciones CONCRETAS de los puertos de domain/repositories.py
usando Django ORM + SQLite. Traducen entre entidades de dominio
(dataclasses) y modelos de persistencia (models.Model).
"""

from datetime import date, time
from typing import List, Optional

from dentasmile.domain.entities import Tratamiento, Cita
from dentasmile.domain.repositories import TratamientoRepository, CitaRepository
from .models import TratamientoModel, CitaModel


# ---------------------------- Tratamiento ----------------------------

def _tratamiento_to_entity(m: TratamientoModel) -> Tratamiento:
    return Tratamiento(id=m.id, nombre=m.nombre, descripcion=m.descripcion, precio=m.precio)


class DjangoTratamientoRepository(TratamientoRepository):

    def listar(self) -> List[Tratamiento]:
        return [_tratamiento_to_entity(m) for m in TratamientoModel.objects.order_by("id")]

    def obtener_por_id(self, tratamiento_id: int) -> Optional[Tratamiento]:
        m = TratamientoModel.objects.filter(id=tratamiento_id).first()
        return _tratamiento_to_entity(m) if m else None

    def existe_nombre(self, nombre: str, excluir_id: Optional[int] = None) -> bool:
        qs = TratamientoModel.objects.filter(nombre__iexact=nombre)
        if excluir_id is not None:
            qs = qs.exclude(id=excluir_id)
        return qs.exists()

    def tiene_citas(self, tratamiento_id: int) -> bool:
        return CitaModel.objects.filter(tratamiento_id=tratamiento_id).exists()

    def guardar(self, t: Tratamiento) -> Tratamiento:
        if t.id is None:
            m = TratamientoModel.objects.create(
                nombre=t.nombre, descripcion=t.descripcion, precio=t.precio)
        else:
            m = TratamientoModel.objects.get(id=t.id)
            m.nombre, m.descripcion, m.precio = t.nombre, t.descripcion, t.precio
            m.save()
        return _tratamiento_to_entity(m)

    def eliminar(self, tratamiento_id: int) -> bool:
        borrados, _ = TratamientoModel.objects.filter(id=tratamiento_id).delete()
        return borrados > 0


# ------------------------------- Cita --------------------------------

def _cita_to_entity(m: CitaModel) -> Cita:
    return Cita(
        id=m.id, paciente_nombre=m.paciente_nombre, paciente_telefono=m.paciente_telefono,
        tratamiento_id=m.tratamiento_id, tratamiento_nombre=m.tratamiento.nombre,
        fecha=m.fecha, hora=m.hora, estado=m.estado,
    )


class DjangoCitaRepository(CitaRepository):

    def listar(self) -> List[Cita]:
        return [_cita_to_entity(m) for m in CitaModel.objects.select_related("tratamiento")]

    def obtener_por_id(self, cita_id: int) -> Optional[Cita]:
        m = CitaModel.objects.select_related("tratamiento").filter(id=cita_id).first()
        return _cita_to_entity(m) if m else None

    def existe_cita_en_horario(self, fecha: date, hora: time,
                               excluir_id: Optional[int] = None) -> bool:
        qs = CitaModel.objects.filter(fecha=fecha, hora=hora).exclude(estado="cancelada")
        if excluir_id is not None:
            qs = qs.exclude(id=excluir_id)
        return qs.exists()

    def guardar(self, c: Cita) -> Cita:
        if c.id is None:
            m = CitaModel.objects.create(
                paciente_nombre=c.paciente_nombre, paciente_telefono=c.paciente_telefono,
                tratamiento_id=c.tratamiento_id, fecha=c.fecha, hora=c.hora, estado=c.estado,
            )
        else:
            m = CitaModel.objects.get(id=c.id)
            m.paciente_nombre, m.paciente_telefono = c.paciente_nombre, c.paciente_telefono
            m.tratamiento_id, m.fecha, m.hora, m.estado = c.tratamiento_id, c.fecha, c.hora, c.estado
            m.save()
        return _cita_to_entity(CitaModel.objects.select_related("tratamiento").get(id=m.id))

    def eliminar(self, cita_id: int) -> bool:
        borrados, _ = CitaModel.objects.filter(id=cita_id).delete()
        return borrados > 0
