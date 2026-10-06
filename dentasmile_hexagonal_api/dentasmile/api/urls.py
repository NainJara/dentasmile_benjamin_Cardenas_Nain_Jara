from django.urls import path
from . import views

urlpatterns = [
    path("tratamientos/", views.TratamientoListCreateView.as_view(), name="tratamiento-list-create"),
    path("tratamientos/<int:tratamiento_id>/", views.TratamientoDetailView.as_view(), name="tratamiento-detail"),
    path("citas/", views.CitaListCreateView.as_view(), name="cita-list-create"),
    path("citas/<int:cita_id>/", views.CitaDetailView.as_view(), name="cita-detail"),
]
