"""Errores de negocio, sin depender de Django ni de HTTP.
La capa api/ (views.py) los traduce a codigos 400, 404, 409."""


class TratamientoNoEncontradoError(Exception):
    pass


class NombreTratamientoDuplicadoError(Exception):
    pass


class TratamientoConCitasError(Exception):
    """No se puede borrar un tratamiento que tiene citas asociadas."""


class CitaNoEncontradaError(Exception):
    pass


class TratamientoInvalidoError(Exception):
    """La cita apunta a un tratamiento que no existe."""


class HorarioOcupadoError(Exception):
    """Ya existe una cita activa en esa fecha y hora."""
