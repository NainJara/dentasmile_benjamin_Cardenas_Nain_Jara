"""
Contenedor de inyeccion de dependencias (simple). Es el UNICO lugar
que decide que implementacion concreta de cada repositorio se usa.
"""

from .repositories import DjangoTratamientoRepository, DjangoCitaRepository


def get_tratamiento_repository():
    return DjangoTratamientoRepository()


def get_cita_repository():
    return DjangoCitaRepository()
