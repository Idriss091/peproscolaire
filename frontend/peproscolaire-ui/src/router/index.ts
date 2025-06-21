import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import des composants
const LoginView = () => import('@/views/auth/LoginView.vue')
const DashboardView = () => import('@/views/DashboardView.vue')

// Modules principaux
const GradesView = () => import('@/views/grades/GradesView.vue')
const EvaluationsView = () => import('@/views/grades/EvaluationsView.vue')
const EvaluationGradesView = () => import('@/views/grades/EvaluationGradesView.vue')
const TimetableView = () => import('@/views/timetable/TimetableView.vue')
const AttendanceView = () => import('@/views/attendance/AttendanceView.vue')
const MessagingView = () => import('@/views/messaging/MessagingView.vue')
const StudentRecordsView = () => import('@/views/student-records/StudentRecordsView.vue')
const HomeworkView = () => import('@/views/homework/HomeworkView.vue')

// IA et détection des risques
const AiDropoutDetectionView = () => import('@/views/ai/AiDropoutDetectionView.vue')
const AiAppreciationGeneratorView = () => import('@/views/ai/AiAppreciationGeneratorView.vue')
const RiskProfilesView = () => import('@/views/risk-detection/RiskProfilesView.vue')
const RiskProfileDetailView = () => import('@/views/risk-detection/RiskProfileDetailView.vue')
const AlertsView = () => import('@/views/risk-detection/AlertsView.vue')
const InterventionPlansView = () => import('@/views/risk-detection/InterventionPlansView.vue')
const InterventionPlanDetailView = () => import('@/views/risk-detection/InterventionPlanDetailView.vue')

// Autres
const SettingsView = () => import('@/views/SettingsView.vue')
const ProfileView = () => import('@/views/auth/ProfileView.vue')
const NotFoundView = () => import('@/views/NotFoundView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        requiresAuth: false,
        title: 'Connexion'
      }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: {
        requiresAuth: true,
        title: 'Tableau de bord',
        permissions: ['read_own_data'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: {
        requiresAuth: true,
        title: 'Mon profil',
        layout: 'AppLayout'
      }
    },
    {
      path: '/grades',
      name: 'grades',
      component: GradesView,
      meta: {
        requiresAuth: true,
        title: 'Notes et évaluations',
        permissions: ['teacher_access', 'student_access', 'parent_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/timetable',
      name: 'timetable',
      component: TimetableView,
      meta: {
        requiresAuth: true,
        title: 'Emploi du temps',
        permissions: ['teacher_access', 'student_access', 'parent_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: AttendanceView,
      meta: {
        requiresAuth: true,
        title: 'Vie scolaire',
        permissions: ['teacher_access', 'admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/messaging',
      name: 'messaging',
      component: MessagingView,
      meta: {
        requiresAuth: true,
        title: 'Messagerie',
        permissions: ['teacher_access', 'student_access', 'parent_access', 'admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/student-records',
      name: 'student-records',
      component: StudentRecordsView,
      meta: {
        requiresAuth: true,
        title: 'Dossiers Élèves',
        permissions: ['teacher_access', 'admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/homework',
      name: 'homework',
      component: HomeworkView,
      meta: {
        requiresAuth: true,
        title: 'Devoirs',
        permissions: ['teacher_access', 'student_access', 'parent_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/ai-dropout-detection',
      name: 'ai-dropout-detection',
      component: AiDropoutDetectionView,
      meta: {
        requiresAuth: true,
        title: 'Détection IA du décrochage',
        permissions: ['teacher_access', 'admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/ai-appreciation-generator',
      name: 'ai-appreciation-generator',
      component: AiAppreciationGeneratorView,
      meta: {
        requiresAuth: true,
        title: 'Générateur d\'appréciations IA',
        permissions: ['teacher_access', 'admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/risk-detection',
      name: 'risk-detection',
      redirect: '/risk-detection/profiles',
      meta: {
        requiresAuth: true,
        permissions: ['teacher_access', 'admin_access'],
        layout: 'AppLayout'
      },
      children: [
        {
          path: 'profiles',
          name: 'risk-profiles',
          component: RiskProfilesView,
          meta: {
            title: 'Profils de risque',
            permissions: ['teacher_access', 'admin_access']
          }
        },
        {
          path: 'profiles/:id',
          name: 'risk-profile-detail',
          component: RiskProfileDetailView,
          meta: {
            title: 'Détail du profil de risque',
            permissions: ['teacher_access', 'admin_access']
          }
        },
        {
          path: 'alerts',
          name: 'alerts',
          component: AlertsView,
          meta: {
            title: 'Alertes',
            permissions: ['teacher_access', 'admin_access']
          }
        },
        {
          path: 'interventions',
          name: 'intervention-plans',
          component: InterventionPlansView,
          meta: {
            title: 'Plans d\'intervention',
            permissions: ['teacher_access', 'admin_access']
          }
        },
        {
          path: 'interventions/:id',
          name: 'intervention-plan-detail',
          component: InterventionPlanDetailView,
          meta: {
            title: 'Détail du plan d\'intervention',
            permissions: ['teacher_access', 'admin_access']
          }
        }
      ]
    },
    {
      path: '/student',
      redirect: '/student/dashboard',
      meta: {
        requiresAuth: true,
        permissions: ['student_access'],
        layout: 'AppLayout'
      },
      children: [
        {
          path: 'dashboard',
          name: 'student-dashboard',
          component: DashboardView,
          meta: {
            title: 'Tableau de bord - Élève',
            permissions: ['student_access']
          }
        },
        {
          path: 'timetable',
          name: 'student-timetable',
          component: TimetableView,
          meta: {
            title: 'Emploi du temps',
            permissions: ['student_access']
          }
        },
        {
          path: 'homework',
          name: 'student-homework',
          component: HomeworkView,
          meta: {
            title: 'Devoirs',
            permissions: ['student_access']
          }
        },
        {
          path: 'grades',
          name: 'student-grades',
          component: GradesView,
          meta: {
            title: 'Notes',
            permissions: ['student_access']
          }
        },
        {
          path: 'messages',
          name: 'student-messages',
          component: MessagingView,
          meta: {
            title: 'Messagerie',
            permissions: ['student_access']
          }
        }
      ]
    },
    {
      path: '/parent',
      redirect: '/parent/dashboard',
      meta: {
        requiresAuth: true,
        permissions: ['parent_access'],
        layout: 'AppLayout'
      },
      children: [
        {
          path: 'dashboard',
          name: 'parent-dashboard',
          component: DashboardView,
          meta: {
            title: 'Tableau de bord - Parent',
            permissions: ['parent_access']
          }
        },
        {
          path: 'children',
          name: 'parent-children',
          component: StudentRecordsView,
          meta: {
            title: 'Suivi enfants',
            permissions: ['parent_access']
          }
        },
        {
          path: 'timetable',
          name: 'parent-timetable',
          component: TimetableView,
          meta: {
            title: 'Emploi du temps',
            permissions: ['parent_access']
          }
        },
        {
          path: 'grades',
          name: 'parent-grades',
          component: GradesView,
          meta: {
            title: 'Notes',
            permissions: ['parent_access']
          }
        },
        {
          path: 'attendance',
          name: 'parent-attendance',
          component: AttendanceView,
          meta: {
            title: 'Vie scolaire',
            permissions: ['parent_access']
          }
        },
        {
          path: 'messages',
          name: 'parent-messages',
          component: MessagingView,
          meta: {
            title: 'Messagerie',
            permissions: ['parent_access']
          }
        }
      ]
    },
    {
      path: '/admin',
      redirect: '/admin/dashboard',
      meta: {
        requiresAuth: true,
        permissions: ['admin_access'],
        layout: 'AppLayout'
      },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: DashboardView,
          meta: {
            title: 'Tableau de bord - Administration',
            permissions: ['admin_access']
          }
        },
        {
          path: 'school',
          name: 'admin-school',
          component: SettingsView,
          meta: {
            title: 'Gestion école',
            permissions: ['admin_access']
          }
        },
        {
          path: 'users',
          name: 'admin-users',
          component: StudentRecordsView,
          meta: {
            title: 'Utilisateurs',
            permissions: ['admin_access']
          }
        },
        {
          path: 'timetable',
          name: 'admin-timetable',
          component: TimetableView,
          meta: {
            title: 'Emplois du temps',
            permissions: ['admin_access']
          }
        },
        {
          path: 'statistics',
          name: 'admin-statistics',
          component: DashboardView,
          meta: {
            title: 'Statistiques',
            permissions: ['admin_access']
          }
        },
        {
          path: 'risk-detection',
          name: 'admin-risk-detection',
          redirect: '/risk-detection/profiles',
          meta: {
            title: 'Détection risques',
            permissions: ['admin_access']
          }
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: SettingsView,
          meta: {
            title: 'Paramètres',
            permissions: ['admin_access']
          }
        }
      ]
    },
    {
      path: '/teacher',
      redirect: '/teacher/dashboard',
      meta: {
        requiresAuth: true,
        permissions: ['teacher_access'],
        layout: 'AppLayout'
      },
      children: [
        {
          path: 'dashboard',
          name: 'teacher-dashboard',
          component: DashboardView,
          meta: {
            title: 'Tableau de bord - Enseignant',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'homework',
          name: 'teacher-homework',
          component: HomeworkView,
          meta: {
            title: 'Cahier de textes',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'timetable',
          name: 'teacher-timetable',
          component: TimetableView,
          meta: {
            title: 'Emploi du temps',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'grades',
          name: 'teacher-grades',
          component: GradesView,
          meta: {
            title: 'Notes et évaluations',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'attendance',
          name: 'teacher-attendance',
          component: AttendanceView,
          meta: {
            title: 'Présences et absences',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'messaging',
          name: 'teacher-messaging',
          component: MessagingView,
          meta: {
            title: 'Messagerie',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'student-records',
          name: 'teacher-student-records',
          component: StudentRecordsView,
          meta: {
            title: 'Dossiers élèves',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'risk-detection',
          name: 'teacher-risk-detection',
          redirect: '/risk-detection/profiles',
          meta: {
            title: 'Détection des risques',
            permissions: ['teacher_access']
          }
        },
        {
          path: 'messages',
          name: 'teacher-messages',
          component: MessagingView,
          meta: {
            title: 'Messages',
            permissions: ['teacher_access']
          }
        }
      ]
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: {
        requiresAuth: true,
        title: 'Paramètres',
        permissions: ['admin_access'],
        layout: 'AppLayout'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: {
        title: 'Page non trouvée'
      }
    }
  ]
})

// Guards de navigation
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Mettre à jour le titre de la page
  if (to.meta.title) {
    document.title = `${to.meta.title} - PEP RO Scolaire`
  }
  
  // Vérifier l'authentification
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      // Rediriger vers la page de connexion
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // Vérifier les permissions
    if (to.meta.permissions && Array.isArray(to.meta.permissions)) {
      const hasPermission = to.meta.permissions.some((permission: string) => 
        authStore.hasPermission(permission)
      )
      
      if (!hasPermission) {
        // Rediriger vers le dashboard si pas de permission
        next({ name: 'dashboard' })
        return
      }
    }
  } else {
    // Si l'utilisateur est déjà connecté et tente d'accéder à la page de connexion
    if (to.name === 'login' && authStore.isAuthenticated) {
      const redirectPath = typeof to.query.redirect === 'string' ? to.query.redirect : '/dashboard'
      next(redirectPath)
      return
    }
  }
  
  next()
})

// Guard après navigation pour les analyses
router.afterEach((to, from) => {
  // Analytics ou logging si nécessaire
  if (import.meta.env.MODE === 'development') {
    console.log(`Navigation: ${from.path} -> ${to.path}`)
  }
})

export default router

// Types pour les métadonnées de route
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    title?: string
    permissions?: string[]
    layout?: string
  }
}