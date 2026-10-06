"""
Serializadores DRF (NO ModelSerializer, a proposito): traducen entre
JSON y las entidades de dominio, sin acoplar la capa API al ORM.
"""

from rest_framework import serializers
from dentasmile.domain.entities import ESTADOS_CITA


class TratamientoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    precio = serializers.IntegerField(required=False, min_value=0, default=0)


class CitaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    paciente_nombre = serializers.CharField(max_length=100)
    paciente_telefono = serializers.CharField(max_length=20)
    tratamiento_id = serializers.IntegerField()
    tratamiento_nombre = serializers.CharField(read_only=True)
    fecha = serializers.DateField()
    hora = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
    estado = serializers.ChoiceField(choices=ESTADOS_CITA, required=False, default="pendiente")
