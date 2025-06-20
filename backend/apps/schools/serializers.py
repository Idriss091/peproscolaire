"""
Serializers pour la gestion des établissements et classes
"""
from rest_framework import serializers
from .models import School, AcademicYear, Level, Class, StudentClassEnrollment
from apps.authentication.serializers import UserSerializer


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer pour les établissements"""
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'school_type', 'address', 'postal_code',
            'city', 'phone', 'email', 'website', 'logo', 'subdomain',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer pour les années scolaires"""
    school_name = serializers.CharField(
        source='school.name',
        read_only=True
    )
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'school', 'school_name', 'name',
            'start_date', 'end_date', 'is_current', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LevelSerializer(serializers.ModelSerializer):
    """Serializer pour les niveaux"""
    
    class Meta:
        model = Level
        fields = [
            'id', 'name', 'short_name', 'order', 'school_type'
        ]


class ClassSerializer(serializers.ModelSerializer):
    """Serializer pour les classes"""
    school_name = serializers.CharField(
        source='school.name',
        read_only=True
    )
    level_name = serializers.CharField(
        source='level.name',
        read_only=True
    )
    main_teacher_name = serializers.CharField(
        source='main_teacher.get_full_name',
        read_only=True
    )
    student_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'school', 'school_name', 'academic_year',
            'level', 'level_name', 'name', 'main_teacher',
            'main_teacher_name', 'max_students', 'student_count',
            'created_at'
        ]
        read_only_fields = ['id', 'student_count', 'created_at']


class StudentClassEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer pour les inscriptions"""
    student = UserSerializer(read_only=True)
    class_name = serializers.CharField(
        source='class_group.__str__',
        read_only=True
    )
    
    class Meta:
        model = StudentClassEnrollment
        fields = [
            'id', 'student', 'class_group', 'class_name',
            'enrollment_date', 'is_active'
        ]
        read_only_fields = ['id', 'enrollment_date']