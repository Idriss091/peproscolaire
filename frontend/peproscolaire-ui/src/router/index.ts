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