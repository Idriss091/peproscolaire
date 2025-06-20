"""
Serializers pour la gestion des dossiers élèves
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import (
    StudentRecord, Guardian, EmergencyContact,
    MedicalRecord, StudentDocument, ScholarshipRecord,
    DisciplinaryRecord, OrientationRecord
)
from apps.authentication.serializers import UserSerializer
from apps.schools.serializers import AcademicYearSerializer


class GuardianSerializer(serializers.ModelSerializer):
    """Serializer pour les responsables légaux"""
    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Guardian
        fields = [
            'id', 'user', 'first_name', 'last_name', 'full_name',
            'relationship', 'email', 'phone', 'mobile_phone',
            'work_phone', 'address', 'postal_code', 'city',
            'profession', 'employer', 'has_custody',
            'is_primary_contact', 'receives_mail', 'can_pickup',
            'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """S'assurer qu'il y a au moins un contact principal"""
        if not attrs.get('is_primary_contact', False):
            student_record = self.context.get('student_record')
            if student_record:
                primary_exists = Guardian.objects.filter(
                    student_record=student_record,
                    is_primary_contact=True
                ).exclude(pk=self.instance.pk if self.instance else None).exists()
                
                if not primary_exists:
                    attrs['is_primary_contact'] = True
        
        return attrs


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer pour les contacts d'urgence"""
    
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone',
            'priority', 'notes'
        ]
        read_only_fields = ['id']


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer pour le dossier médical"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'blood_type', 'height', 'weight',
            'last_medical_check', 'doctor_name', 'doctor_phone',
            'chronic_conditions', 'allergies', 'medications',
            'vaccinations_up_to_date', 'vaccination_details',
            'physical_restrictions', 'emergency_protocol',
            'insurance_company', 'insurance_number',
            'confidential_notes'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'confidential_notes': {'write_only': True}
        }
    
    def to_representation(self, instance):
        """Masquer les notes confidentielles selon les permissions"""
        data = super().to_representation(instance)
        user = self.context['request'].user
        
        # Seuls certains utilisateurs peuvent voir les notes confidentielles
        if user.user_type not in ['admin', 'superadmin']:
            data.pop('confidential_notes', None)
        
        return data


class StudentDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents"""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    verified_by_name = serializers.CharField(
        source='verified_by.get_full_name',
        read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)
    size_mb = serializers.FloatField(read_only=True)
    
    class Meta:
        model = StudentDocument
        fields = [
            'id', 'document_type', 'title', 'description',
            'file', 'issue_date', 'expiry_date', 'uploaded_by',
            'uploaded_by_name', 'is_verified', 'verified_by',
            'verified_by_name', 'verified_at', 'is_confidential',
            'is_expired', 'size_mb', 'created_at'
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'verified_by',
            'verified_at', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class ScholarshipRecordSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers de bourse"""
    academic_year_name = serializers.CharField(
        source='academic_year.name',
        read_only=True
    )
    
    class Meta:
        model = ScholarshipRecord
        fields = [
            'id', 'academic_year', 'academic_year_name',
            'scholarship_type', 'amount', 'status',
            'application_date', 'decision_date',
            'reference_number', 'notes'
        ]
        read_only_fields = ['id']


class DisciplinaryRecordSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers disciplinaires"""
    academic_year = AcademicYearSerializer(read_only=True)
    tutor_name = serializers.CharField(
        source='tutor_assigned.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = DisciplinaryRecord
        fields = [
            'id', 'academic_year', 'total_warnings',
            'total_detentions', 'total_exclusions',
            'has_disciplinary_council', 'council_date',
            'council_decision', 'improvement_plan',
            'tutor_assigned', 'tutor_name', 'notes'
        ]
        read_only_fields = [
            'id', 'total_warnings', 'total_detentions',
            'total_exclusions'
        ]


class OrientationRecordSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers d'orientation"""
    academic_year_name = serializers.CharField(
        source='academic_year.name',
        read_only=True
    )
    
    class Meta:
        model = OrientationRecord
        fields = [
            'id', 'academic_year', 'academic_year_name',
            'current_level', 'student_wishes',
            'class_council_opinion', 'recommended_orientation',
            'final_decision', 'decision_date', 'has_appeal',
            'appeal_decision', 'meeting_report',
            'next_school', 'next_program'
        ]
        read_only_fields = ['id']


class StudentRecordSerializer(serializers.ModelSerializer):
    """Serializer pour le dossier complet de l'élève"""
    student = UserSerializer(read_only=True)
    age = serializers.IntegerField(
        source='get_age',
        read_only=True
    )
    guardians = GuardianSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    medical_record = MedicalRecordSerializer(read_only=True)
    
    class Meta:
        model = StudentRecord
        fields = [
            'id', 'student', 'national_id', 'birth_certificate_number',
            'birth_place', 'birth_country', 'nationality', 'age',
            'family_situation', 'siblings_count', 'entry_date',
            'previous_school', 'options', 'specialties',
            'has_special_needs', 'special_needs_details',
            'has_disability', 'disability_details',
            'has_pai', 'has_pap', 'has_pps',
            'uses_school_transport', 'transport_line',
            'lunch_type', 'dietary_restrictions',
            'photo_authorization', 'leave_alone_authorization',
            'administrative_notes', 'is_active',
            'graduation_date', 'graduation_reason',
            'guardians', 'emergency_contacts', 'medical_record',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un dossier élève"""
    
    class Meta:
        model = StudentRecord
        fields = [
            'student', 'national_id', 'birth_certificate_number',
            'birth_place', 'birth_country', 'nationality',
            'family_situation', 'siblings_count', 'entry_date',
            'previous_school'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        # Créer le dossier
        student_record = super().create(validated_data)
        
        # Créer automatiquement le dossier médical
        MedicalRecord.objects.create(student_record=student_record)
        
        return student_record


class StudentSummarySerializer(serializers.Serializer):
    """
    Serializer pour le résumé complet d'un élève
    Agrège les données de tous les modules
    """
    
    def to_representation(self, instance):
        """Instance est un StudentRecord"""
        student = instance.student
        current_year = timezone.now().year
        
        # Informations de base
        summary = {
            'personal_info': StudentRecordSerializer(instance).data,
            'current_class': self._get_current_class(student),
            'academic_performance': self._get_academic_performance(student),
            'attendance_summary': self._get_attendance_summary(student),
            'behavior_summary': self._get_behavior_summary(student),
            'recent_documents': self._get_recent_documents(instance),
            'alerts': self._get_active_alerts(student)
        }
        
        return summary
    
    def _get_current_class(self, student):
        """Récupérer la classe actuelle"""
        from apps.schools.models import StudentClassEnrollment
        
        enrollment = StudentClassEnrollment.objects.filter(
            student=student,
            is_active=True
        ).select_related('class_group').first()
        
        if enrollment:
            return {
                'class_name': str(enrollment.class_group),
                'class_id': str(enrollment.class_group.id),
                'enrollment_date': enrollment.enrollment_date
            }
        return None
    
    def _get_academic_performance(self, student):
        """Récupérer les performances académiques"""
        from apps.grades.models import GeneralAverage
        
        # Dernière moyenne générale
        last_average = GeneralAverage.objects.filter(
            student=student
        ).order_by('-grading_period__end_date').first()
        
        if last_average:
            return {
                'period': last_average.grading_period.name,
                'general_average': float(last_average.average) if last_average.average else None,
                'rank': last_average.rank,
                'class_size': last_average.class_size,
                'honor_roll': last_average.honor_roll
            }
        return None
    
    def _get_attendance_summary(self, student):
        """Récupérer le résumé de présence"""
        from apps.attendance.models import Attendance, AttendanceStatus
        from datetime import date, timedelta
        
        # Sur les 30 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        attendances = Attendance.objects.filter(
            student=student,
            date__range=[start_date, end_date]
        )
        
        total = attendances.count()
        if total == 0:
            return None
        
        return {
            'period': '30 derniers jours',
            'total_courses': total,
            'absences': attendances.filter(status=AttendanceStatus.ABSENT).count(),
            'justified_absences': attendances.filter(
                status=AttendanceStatus.ABSENT,
                is_justified=True
            ).count(),
            'delays': attendances.filter(status=AttendanceStatus.LATE).count(),
            'attendance_rate': round(
                attendances.filter(
                    status__in=[AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                ).count() / total * 100, 2
            )
        }
    
    def _get_behavior_summary(self, student):
        """Récupérer le résumé de comportement"""
        from apps.attendance.models import StudentBehavior, Sanction
        from django.db.models import Sum
        
        # Sur l'année en cours
        behaviors = StudentBehavior.objects.filter(
            student=student,
            date__year=timezone.now().year
        )
        
        sanctions = Sanction.objects.filter(
            student=student,
            date__year=timezone.now().year
        )
        
        behavior_points = behaviors.aggregate(
            total_points=Sum('points')
        )['total_points'] or 0
        
        return {
            'year': timezone.now().year,
            'behavior_points': behavior_points,
            'positive_behaviors': behaviors.filter(behavior_type='positive').count(),
            'negative_behaviors': behaviors.filter(behavior_type='negative').count(),
            'sanctions_count': sanctions.count(),
            'recent_sanctions': [
                {
                    'type': s.get_sanction_type_display(),
                    'date': s.date,
                    'reason': s.reason
                }
                for s in sanctions.order_by('-date')[:3]
            ]
        }
    
    def _get_recent_documents(self, instance):
        """Récupérer les documents récents"""
        documents = instance.documents.order_by('-created_at')[:5]
        
        return [
            {
                'id': str(doc.id),
                'type': doc.get_document_type_display(),
                'title': doc.title,
                'is_expired': doc.is_expired,
                'created_at': doc.created_at
            }
            for doc in documents
        ]
    
    def _get_active_alerts(self, student):
        """Récupérer les alertes actives"""
        alerts = []
        
        # Alertes d'assiduité
        from apps.attendance.models import AttendanceAlert
        
        attendance_alerts = AttendanceAlert.objects.filter(
            student=student,
            is_resolved=False
        ).order_by('-created_at')[:3]
        
        for alert in attendance_alerts:
            alerts.append({
                'type': 'attendance',
                'message': alert.message,
                'level': alert.alert_type,
                'date': alert.created_at
            })
        
        # Documents expirés
        expired_docs = StudentDocument.objects.filter(
            student_record=instance,
            expiry_date__lt=timezone.now().date()
        )
        
        for doc in expired_docs:
            alerts.append({
                'type': 'document',
                'message': f"Document expiré: {doc.title}",
                'level': 'warning',
                'date': doc.expiry_date
            })
        
        return alerts


class ParentAccessSerializer(serializers.Serializer):
    """
    Serializer pour l'accès parent aux dossiers de leurs enfants
    """
    
    def to_representation(self, instance):
        """Instance est un Guardian"""
        children_records = []
        
        # Récupérer tous les dossiers où ce parent est responsable
        student_records = StudentRecord.objects.filter(
            guardians__user=instance
        ).distinct()
        
        for record in student_records:
            # Vérifier les droits du parent
            guardian = record.guardians.filter(user=instance).first()
            
            if guardian and (guardian.has_custody or guardian.is_primary_contact):
                # Le parent a accès au dossier
                summary = StudentSummarySerializer(record).data
                
                # Filtrer certaines informations sensibles si pas d'autorité parentale
                if not guardian.has_custody:
                    summary['personal_info'].pop('administrative_notes', None)
                    summary['personal_info'].pop('medical_record', None)
                
                children_records.append({
                    'student': summary,
                    'relationship': guardian.get_relationship_display(),
                    'access_rights': {
                        'has_custody': guardian.has_custody,
                        'is_primary_contact': guardian.is_primary_contact,
                        'receives_mail': guardian.receives_mail,
                        'can_pickup': guardian.can_pickup
                    }
                })
        
        return {
            'children_count': len(children_records),
            'children': children_records
        }