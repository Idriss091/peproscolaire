"""
URLs pour l'application emploi du temps
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, RoomViewSet, TimeSlotViewSet,
    ScheduleViewSet, ScheduleModificationViewSet
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'timeslots', TimeSlotViewSet, basename='timeslot')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'modifications', ScheduleModificationViewSet, basename='modification')

app_name = 'timetable'

urlpatterns = [
    path('', include(router.urls)),
]