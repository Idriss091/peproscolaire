"""
Configuration admin pour l'emploi du temps
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Subject, Room, TimeSlot, Schedule,
    ScheduleModification
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'color_display', 'coefficient', 'is_optional']
    list_filter = ['is_optional']
    search_fields = ['name', 'short_name']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Couleur'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'building', 'floor', 'capacity', 'room_type', 'is_available']
    list_filter = ['school', 'room_type', 'is_available', 'building']
    search_fields = ['name', 'building']
    ordering = ['school', 'building', 'name']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['school', 'get_day_display', 'start_time', 'end_time', 'order', 'is_break']
    list_filter = ['school', 'day', 'is_break']
    ordering = ['school', 'day', 'order']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'class_group', 'subject', 'teacher', 'time_slot',
        'room', 'week_type', 'is_cancelled'
    ]
    list_filter = [
        'academic_year', 'class_group__level', 'subject',
        'week_type', 'is_cancelled'
    ]
    search_fields = [
        'class_group__name', 'subject__name',
        'teacher__first_name', 'teacher__last_name'
    ]
    raw_id_fields = ['teacher', 'class_group']
    autocomplete_fields = ['subject', 'room']


@admin.register(ScheduleModification)
class ScheduleModificationAdmin(admin.ModelAdmin):
    list_display = [
        'schedule', 'date', 'modification_type',
        'created_by', 'created_at'
    ]
    list_filter = ['modification_type', 'date']
    date_hierarchy = 'date'
    raw_id_fields = ['schedule', 'substitute_teacher', 'created_by']