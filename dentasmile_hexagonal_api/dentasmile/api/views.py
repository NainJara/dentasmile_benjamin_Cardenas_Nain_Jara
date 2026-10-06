"""
ADAPTADOR PRIMARIO (Driving Adapter) - API REST
-------------------------------------------------
Las vistas reciben HTTP, validan con el Serializer, llaman al caso de
uso y devuelven la Response con el codigo correcto. NO tienen logica de
negocio (esa vive en application/use_cases.py).

Toda la API exige token:  Authorization: Token <token>
"""

from dataclasses import asdict

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dentasmile.infrastructure.di import get_tratamiento_repository, get_cita_repository
from dentasmile.application.use_cases import (
    ListarTratamientosUseCase, ObtenerTratamientoUseCase, CrearTratamientoUseCase,
    ActualizarTratamientoUseCase, EliminarTratamientoUseCase,
    ListarCitasUseCase, ObtenerCitaUseCase, CrearCitaUseCase,
    ActualizarCitaUseCase, EliminarCitaUseCase,
)
from dentasmile.application.exceptions import (
    TratamientoNoEncontradoError, NombreTratamientoDuplicadoError, TratamientoConCitasError,
    CitaNoEncontradaError, TratamientoInvalidoError, HorarioOcupadoError,
)
from .serializers import TratamientoSerializer, CitaSerializer


def _error(e, codigo):
    return Response({"detail": str(e)}, status=codigo)


class _ProtegidaView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


# =====================================================================
#  TRATAMIENTOS  (entidad principal)
# =====================================================================

class TratamientoListCreateView(_ProtegidaView):

    def get(self, request):
        """GET /api/tratamientos/ -> lista todos los tratamientos"""
        items = ListarTratamientosUseCase(get_tratamiento_repository()).ejecutar()
        return Response(TratamientoSerializer([asdict(t) for t in items], many=True).data)

    def post(self, request):
        """POST /api/tratamientos/ -> crea un tratamiento"""
        serializer = TratamientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            t = CrearTratamientoUseCase(get_tratamiento_repository()).ejecutar(serializer.validated_data)
        except NombreTratamientoDuplicadoError as e:
            return _error(e, status.HTTP_400_BAD_REQUEST)
        return Response(TratamientoSerializer(asdict(t)).data, status=status.HTTP_201_CREATED)


class TratamientoDetailView(_ProtegidaView):

    def get(self, request, tratamiento_id):
        """GET /api/tratamientos/<id>/ -> detalle"""
        try:
            t = ObtenerTratamientoUseCase(get_tratamiento_repository()).ejecutar(tratamiento_id)
        except TratamientoNoEncontradoError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        return Response(TratamientoSerializer(asdict(t)).data)

    def put(self, request, tratamiento_id):
        """PUT /api/tratamientos/<id>/ -> actualiza"""
        serializer = TratamientoSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            t = ActualizarTratamientoUseCase(get_tratamiento_repository()).ejecutar(
                tratamiento_id, serializer.validated_data)
        except TratamientoNoEncontradoError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        except NombreTratamientoDuplicadoError as e:
            return _error(e, status.HTTP_400_BAD_REQUEST)
        return Response(TratamientoSerializer(asdict(t)).data)

    def delete(self, request, tratamiento_id):
        """DELETE /api/tratamientos/<id>/ -> elimina"""
        try:
            EliminarTratamientoUseCase(get_tratamiento_repository()).ejecutar(tratamiento_id)
        except TratamientoNoEncontradoError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        except TratamientoConCitasError as e:
            return _error(e, status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
#  CITAS  (entidad secundaria)
# =====================================================================

class CitaListCreateView(_ProtegidaView):

    def get(self, request):
        """GET /api/citas/ -> lista todas las citas"""
        items = ListarCitasUseCase(get_cita_repository()).ejecutar()
        return Response(CitaSerializer([asdict(c) for c in items], many=True).data)

    def post(self, request):
        """POST /api/citas/ -> crea una cita"""
        serializer = CitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            c = CrearCitaUseCase(get_cita_repository(), get_tratamiento_repository()).ejecutar(
                serializer.validated_data)
        except TratamientoInvalidoError as e:
            return _error(e, status.HTTP_400_BAD_REQUEST)
        except HorarioOcupadoError as e:
            return _error(e, status.HTTP_409_CONFLICT)
        return Response(CitaSerializer(asdict(c)).data, status=status.HTTP_201_CREATED)


class CitaDetailView(_ProtegidaView):

    def get(self, request, cita_id):
        """GET /api/citas/<id>/ -> detalle"""
        try:
            c = ObtenerCitaUseCase(get_cita_repository()).ejecutar(cita_id)
        except CitaNoEncontradaError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        return Response(CitaSerializer(asdict(c)).data)

    def put(self, request, cita_id):
        """PUT /api/citas/<id>/ -> actualiza"""
        serializer = CitaSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            c = ActualizarCitaUseCase(get_cita_repository(), get_tratamiento_repository()).ejecutar(
                cita_id, serializer.validated_data)
        except CitaNoEncontradaError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        except TratamientoInvalidoError as e:
            return _error(e, status.HTTP_400_BAD_REQUEST)
        except HorarioOcupadoError as e:
            return _error(e, status.HTTP_409_CONFLICT)
        return Response(CitaSerializer(asdict(c)).data)

    def delete(self, request, cita_id):
        """DELETE /api/citas/<id>/ -> elimina"""
        try:
            EliminarCitaUseCase(get_cita_repository()).ejecutar(cita_id)
        except CitaNoEncontradaError as e:
            return _error(e, status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
