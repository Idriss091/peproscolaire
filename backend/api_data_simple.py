"""
APIs de données simples pour tester l'affichage frontend
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from apps.homework.models import Homework
from apps.grades.models import Grade, Evaluation
from apps.timetable.models import Schedule
from apps.messaging.models import Message
import json

User = get_user_model()

def get_user_from_request(request):
    """Extraire l'utilisateur depuis le token JWT"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        import jwt
        from django.conf import settings
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        return User.objects.get(id=user_id)
    except:
        return None

@csrf_exempt
def homework_list_api(request):
    """Liste des devoirs selon le type d'utilisateur"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_user_from_request(request)
    if not user:
        return JsonResponse({'detail': 'Non authentifié'}, status=401)
    
    try:
        if user.user_type == 'student':
            # Pour un élève : ses devoirs
            homeworks = Homework.objects.filter(
                class_group__students=user
            ).select_related('subject', 'teacher')[:10]
        elif user.user_type == 'teacher':
            # Pour un professeur : les devoirs qu'il a donnés
            homeworks = Homework.objects.filter(
                teacher=user
            ).select_related('subject')[:10]
        else:
            # Pour les autres : tous les devoirs récents
            homeworks = Homework.objects.all().select_related('subject', 'teacher')[:10]
        
        homework_data = []
        for hw in homeworks:
            homework_data.append({
                'id': hw.id,
                'title': hw.title,
                'description': hw.description,
                'subject': hw.subject.name if hw.subject else 'Matière inconnue',
                'due_date': hw.due_date.isoformat(),
                'given_date': hw.given_date.isoformat(),
                'estimated_duration': hw.estimated_duration,
                'homework_type': hw.homework_type,
                'teacher_name': f"{hw.teacher.first_name} {hw.teacher.last_name}" if hw.teacher else 'Professeur'
            })
        
        return JsonResponse({'results': homework_data})
        
    except Exception as e:
        # Si pas de données, retourner des données de demo
        return JsonResponse({
            'results': [
                {
                    'id': 1,
                    'title': 'Exercices de mathématiques',
                    'description': 'Faire les exercices 1 à 5 page 42',
                    'subject': 'Mathématiques',
                    'due_date': '2025-06-25T23:59:59Z',
                    'given_date': '2025-06-21T10:00:00Z',
                    'estimated_duration': 60,
                    'homework_type': 'exercise',
                    'teacher_name': 'M. Dupont'
                },
                {
                    'id': 2,
                    'title': 'Lecture Chapitre 3',
                    'description': 'Lire le chapitre 3 du livre de français',
                    'subject': 'Français',
                    'due_date': '2025-06-24T23:59:59Z',
                    'given_date': '2025-06-20T14:00:00Z',
                    'estimated_duration': 30,
                    'homework_type': 'reading',
                    'teacher_name': 'Mme Martin'
                }
            ]
        })

@csrf_exempt
def grades_list_api(request):
    """Liste des notes selon le type d'utilisateur"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_user_from_request(request)
    if not user:
        return JsonResponse({'detail': 'Non authentifié'}, status=401)
    
    try:
        if user.user_type == 'student':
            # Pour un élève : ses notes
            grades = Grade.objects.filter(
                student=user
            ).select_related('evaluation', 'evaluation__subject')[:10]
        elif user.user_type == 'teacher':
            # Pour un professeur : les notes qu'il a données
            grades = Grade.objects.filter(
                graded_by=user
            ).select_related('evaluation', 'student')[:10]
        else:
            # Pour les autres : toutes les notes récentes
            grades = Grade.objects.all().select_related('evaluation', 'student')[:10]
        
        grades_data = []
        for grade in grades:
            grades_data.append({
                'id': grade.id,
                'value': grade.value,
                'max_value': grade.max_value,
                'coefficient': grade.coefficient,
                'comment': grade.comment or '',
                'graded_at': grade.graded_at.isoformat(),
                'evaluation_name': grade.evaluation.name if grade.evaluation else 'Évaluation',
                'subject_name': grade.evaluation.subject.name if grade.evaluation and grade.evaluation.subject else 'Matière',
                'student_name': f"{grade.student.first_name} {grade.student.last_name}" if grade.student else 'Élève'
            })
        
        return JsonResponse({'results': grades_data})
        
    except Exception as e:
        # Si pas de données, retourner des données de demo
        return JsonResponse({
            'results': [
                {
                    'id': 1,
                    'value': 15.5,
                    'max_value': 20,
                    'coefficient': 1,
                    'comment': 'Bon travail',
                    'graded_at': '2025-06-20T10:00:00Z',
                    'evaluation_name': 'Contrôle Chapitre 2',
                    'subject_name': 'Mathématiques',
                    'student_name': 'Marie Élève'
                },
                {
                    'id': 2,
                    'value': 18,
                    'max_value': 20,
                    'coefficient': 2,
                    'comment': 'Excellent',
                    'graded_at': '2025-06-19T15:30:00Z',
                    'evaluation_name': 'Dissertation',
                    'subject_name': 'Français',
                    'student_name': 'Marie Élève'
                }
            ]
        })

@csrf_exempt
def timetable_api(request):
    """Emploi du temps selon le type d'utilisateur"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_user_from_request(request)
    if not user:
        return JsonResponse({'detail': 'Non authentifié'}, status=401)
    
    # Données de demo pour l'emploi du temps
    demo_schedule = {
        'monday': [
            {'time': '08:00-09:00', 'subject': 'Mathématiques', 'teacher': 'M. Dupont', 'room': 'A101'},
            {'time': '09:00-10:00', 'subject': 'Français', 'teacher': 'Mme Martin', 'room': 'B202'},
            {'time': '10:15-11:15', 'subject': 'Histoire', 'teacher': 'M. Durand', 'room': 'C303'},
            {'time': '11:15-12:15', 'subject': 'Anglais', 'teacher': 'Mme Smith', 'room': 'B205'}
        ],
        'tuesday': [
            {'time': '08:00-09:00', 'subject': 'Sciences', 'teacher': 'M. Bernard', 'room': 'Lab1'},
            {'time': '09:00-10:00', 'subject': 'Mathématiques', 'teacher': 'M. Dupont', 'room': 'A101'},
            {'time': '10:15-11:15', 'subject': 'EPS', 'teacher': 'M. Sport', 'room': 'Gymnase'},
            {'time': '11:15-12:15', 'subject': 'Français', 'teacher': 'Mme Martin', 'room': 'B202'}
        ],
        'wednesday': [
            {'time': '08:00-09:00', 'subject': 'Mathématiques', 'teacher': 'M. Dupont', 'room': 'A101'},
            {'time': '09:00-10:00', 'subject': 'Géographie', 'teacher': 'M. Terre', 'room': 'C301'}
        ],
        'thursday': [
            {'time': '08:00-09:00', 'subject': 'Anglais', 'teacher': 'Mme Smith', 'room': 'B205'},
            {'time': '09:00-10:00', 'subject': 'Sciences', 'teacher': 'M. Bernard', 'room': 'Lab1'},
            {'time': '10:15-11:15', 'subject': 'Art plastique', 'teacher': 'Mme Pinceau', 'room': 'Art1'},
            {'time': '11:15-12:15', 'subject': 'Français', 'teacher': 'Mme Martin', 'room': 'B202'}
        ],
        'friday': [
            {'time': '08:00-09:00', 'subject': 'Mathématiques', 'teacher': 'M. Dupont', 'room': 'A101'},
            {'time': '09:00-10:00', 'subject': 'Histoire', 'teacher': 'M. Durand', 'room': 'C303'},
            {'time': '10:15-11:15', 'subject': 'Musique', 'teacher': 'Mme Note', 'room': 'Musique1'},
            {'time': '11:15-12:15', 'subject': 'EPS', 'teacher': 'M. Sport', 'room': 'Gymnase'}
        ]
    }
    
    return JsonResponse(demo_schedule)

@csrf_exempt
def messages_list_api(request):
    """Liste des messages selon le type d'utilisateur"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_user_from_request(request)
    if not user:
        return JsonResponse({'detail': 'Non authentifié'}, status=401)
    
    # Données de demo pour les messages
    demo_messages = [
        {
            'id': 1,
            'subject': 'Réunion parents-professeurs',
            'sender_name': 'Administration',
            'sent_at': '2025-06-21T09:00:00Z',
            'is_read': False,
            'priority': 'normal',
            'body': 'La réunion parents-professeurs aura lieu le 25 juin à 18h.'
        },
        {
            'id': 2,
            'subject': 'Contrôle de mathématiques reporté',
            'sender_name': 'M. Dupont',
            'sent_at': '2025-06-20T14:30:00Z',
            'is_read': True,
            'priority': 'high',
            'body': 'Le contrôle prévu vendredi est reporté à lundi prochain.'
        },
        {
            'id': 3,
            'subject': 'Sortie scolaire musée',
            'sender_name': 'Mme Martin',
            'sent_at': '2025-06-19T16:45:00Z',
            'is_read': True,
            'priority': 'normal',
            'body': 'N\'oubliez pas l\'autorisation parentale pour la sortie au musée.'
        }
    ]
    
    return JsonResponse({'results': demo_messages})