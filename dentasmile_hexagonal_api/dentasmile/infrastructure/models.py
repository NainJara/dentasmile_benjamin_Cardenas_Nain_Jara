"""
Modelos de Django ORM = detalle de PERSISTENCIA (las 2 tablas).
Aqui NO hay reglas de negocio: solo columnas y la ForeignKey.
Solo se usan dentro de infrastructure/ (y en admin.py).

Cambios respecto a la API Mongo del semestre pasado:
  - "paciente": {"nombre", "telefono"}  ->  columnas paciente_nombre / paciente_telefono
  - "tratamientoId" (texto suelto)      ->  ForeignKey real hacia TratamientoModel
  - "tratamientoNombre"                 ->  ya no se guarda: se obtiene por la FK
"""

from django.db import models


class TratamientoModel(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, default="")
    precio = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "dentasmile_tratamiento"

    def __str__(self):
        return self.nombre


class CitaModel(models.Model):
    paciente_nombre = models.CharField(max_length=100)
    paciente_telefono = models.CharField(max_length=20)
    tratamiento = models.ForeignKey(
        TratamientoModel, on_delete=models.PROTECT, related_name="citas")
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, default="pendiente")

    class Meta:
        db_table = "dentasmile_cita"
        ordering = ["fecha", "hora"]

    def __str__(self):
        return f"{self.paciente_nombre} - {self.fecha} {self.hora:%H:%M}"
