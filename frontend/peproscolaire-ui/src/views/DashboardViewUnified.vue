<template>
  <div class="space-y-6">
    <!-- En-tête du dashboard -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Tableau de bord
            </h1>
            <p class="mt-1 text-sm text-gray-600">
              Bienvenue {{ authStore.user?.first_name }}, voici un aperçu de votre activité
            </p>
          </div>
          <div class="flex items-center space-x-3">
            <div class="text-sm text-gray-500">
              {{ formatDate(new Date()) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistiques rapides pour tous les modules -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Statistiques notes -->
      <BaseCard v-if="showGradesStats">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <AcademicCapIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <router-link to="/grades/evaluations" class="group">
              <p class="text-sm font-medium text-gray-500 group-hover:text-blue-600">Évaluations ce mois</p>
              <p class="text-2xl font-semibold text-gray-900 group-hover:text-blue-700">{{ stats.evaluations }}</p>
            </router-link>
          </div>
        </div>
      </BaseCard>

      <!-- Statistiques emploi du temps -->
      <BaseCard v-if="showTimetableStats">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CalendarIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <router-link to="/timetable" class="group">
              <p class="text-sm font-medium text-gray-500 group-hover:text-green-600">Cours cette semaine</p>
              <p class="text-2xl font-semibold text-gray-900 group-hover:text-green-700">{{ stats.weeklyClasses }}</p>
            </router-link>
          </div>
        </div>
      </BaseCard>

      <!-- Statistiques vie scolaire -->
      <BaseCard v-if="showAttendanceStats">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UserGroupIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <router-link to="/attendance" class="group">
              <p class="text-sm font-medium text-gray-500 group-hover:text-yellow-600">Taux de présence</p>
              <p class="text-2xl font-semibold text-gray-900 group-hover:text-yellow-700">{{ stats.attendanceRate }}%</p>
            </router-link>
          </div>
        </div>
      </BaseCard>

      <!-- Statistiques détection des risques -->
      <BaseCard v-if="showRiskStats">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <router-link to="/risk-detection/profiles" class="group">
              <p class="text-sm font-medium text-gray-500 group-hover:text-red-600">Élèves à risque</p>
              <p class="text-2xl font-semibold text-gray-900 group-hover:text-red-700">{{ riskDetectionStore.dashboardStats?.summary.at_risk_students || 0 }}</p>
            </router-link>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Contenu principal en colonnes -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Colonne principale -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Activité récente -->
        <BaseCard>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Activité récente</h3>
            <BaseButton variant="outline" size="sm">
              Voir tout
            </BaseButton>
          </div>
          
          <div v-if="loading.activities" class="text-center py-8">
            <LoadingSpinner />
          </div>
          
          <div v-else-if="recentActivities.length === 0" class="text-center py-8">
            <ClockIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">Aucune activité récente</p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="activity in recentActivities"
              :key="activity.id"
              class="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div class="flex-shrink-0">
                <component
                  :is="getActivityIcon(activity.type)"
                  :class="[getActivityColor(activity.type), 'h-5 w-5']"
                />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-900">
                  {{ activity.description }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatRelativeTime(activity.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </BaseCard>

        <!-- Emploi du temps du jour -->
        <BaseCard v-if="showTimetableStats">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Emploi du temps d'aujourd'hui</h3>
            <router-link to="/timetable">
              <BaseButton variant="outline" size="sm">
                Voir la semaine
              </BaseButton>
            </router-link>
          </div>
          
          <div v-if="loading.todaySchedule" class="text-center py-8">
            <LoadingSpinner />
          </div>
          
          <div v-else-if="todaySchedule.length === 0" class="text-center py-8">
            <CalendarIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">Aucun cours aujourd'hui</p>
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="course in todaySchedule"
              :key="course.id"
              class="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow"
            >
              <div class="flex items-center space-x-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: course.subject_color || '#3B82F6' }"
                ></div>
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    {{ course.subject_name }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ course.class_name }} • {{ course.room_name }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">
                  {{ formatTime(timetableStore.getTimeSlotById(course.time_slot)?.start_time || '') }} - {{ formatTime(timetableStore.getTimeSlotById(course.time_slot)?.end_time || '') }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ getCourseStatus(course) }}
                </p>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Alertes importantes -->
        <BaseCard v-if="showRiskStats">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Alertes importantes</h3>
            <router-link to="/risk-detection/alerts">
              <BaseButton variant="outline" size="sm">
                Voir toutes
              </BaseButton>
            </router-link>
          </div>
          
          <div v-if="loading.alerts" class="text-center py-8">
            <LoadingSpinner />
          </div>
          
          <div v-else-if="recentAlerts.length === 0" class="text-center py-8">
            <CheckCircleIcon class="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p class="text-sm text-gray-600">Aucune alerte</p>
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="alert in recentAlerts"
              :key="alert.id"
              class="p-3 rounded-lg border-l-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
              :class="getAlertBorderColor(alert.priority)"
              @click="goToAlert(alert)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">
                    {{ alert.title }}
                  </p>
                  <p class="text-xs text-gray-600 mt-1">
                    {{ alert.risk_profile.student.first_name }} {{ alert.risk_profile.student.last_name }}
                  </p>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ formatRelativeTime(alert.created_at) }}
                  </p>
                </div>
                <BaseBadge
                  :variant="getAlertVariant(alert.priority)"
                  size="sm"
                >
                  {{ alert.priority }}
                </BaseBadge>
              </div>
            </div>
          </div>
        </BaseCard>

        <!-- Actions rapides -->
        <BaseCard>
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h3>
          
          <div class="space-y-2">
            <BaseButton
              v-if="authStore.hasPermission('teacher_access')"
              variant="outline"
              class="w-full justify-start"
              @click="$router.push('/grades/evaluations')"
            >
              <AcademicCapIcon class="w-4 h-4 mr-2" />
              Créer une évaluation
            </BaseButton>
            
            <BaseButton
              v-if="authStore.hasPermission('teacher_access')"
              variant="outline"
              class="w-full justify-start"
              @click="$router.push('/attendance')"
            >
              <UserGroupIcon class="w-4 h-4 mr-2" />
              Faire l'appel
            </BaseButton>
            
            <BaseButton
              v-if="authStore.hasPermission('teacher_access')"
              variant="outline"
              class="w-full justify-start"
              @click="$router.push('/timetable')"
            >
              <CalendarIcon class="w-4 h-4 mr-2" />
              Consulter l'emploi du temps
            </BaseButton>
            
            <BaseButton
              variant="outline"
              class="w-full justify-start"
              @click="$router.push('/profile')"
            >
              <UserIcon class="w-4 h-4 mr-2" />
              Modifier mon profil
            </BaseButton>
          </div>
        </BaseCard>

        <!-- Prochaines échéances -->
        <BaseCard v-if="showGradesStats">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Prochaines échéances</h3>
          
          <div v-if="upcomingDeadlines.length === 0" class="text-center py-4">
            <CalendarIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-600">Aucune échéance</p>
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="deadline in upcomingDeadlines"
              :key="deadline.id"
              class="flex items-center justify-between p-2 rounded-lg bg-gray-50"
            >
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ deadline.title }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ deadline.subject_name }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-xs font-medium" :class="getDeadlineColor(deadline.date)">
                  {{ formatRelativeDate(deadline.date) }}
                </p>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  AcademicCapIcon,
  CalendarIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { useGradesStore } from '@/stores/grades'
import { useTimetableStore } from '@/stores/timetable'
import { useAttendanceStore } from '@/stores/attendance'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

import type { Alert, Schedule } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const riskDetectionStore = useRiskDetectionStore()
const gradesStore = useGradesStore()
const timetableStore = useTimetableStore()
const attendanceStore = useAttendanceStore()

// État local
const loading = ref({
  activities: false,
  alerts: false,
  todaySchedule: false
})

const stats = computed(() => ({
  evaluations: gradesStore.evaluations.length,
  weeklyClasses: timetableStore.weeklyStats.activeClasses,
  attendanceRate: attendanceStore.weeklyAttendanceStats.attendance_rate
}))

const recentActivities = ref<any[]>([])
const recentAlerts = ref<Alert[]>([])
const todaySchedule = ref<Schedule[]>([])
const upcomingDeadlines = ref<any[]>([])

// Permissions d'affichage
const showGradesStats = computed(() => 
  authStore.hasPermission('teacher_access') || 
  authStore.hasPermission('student_access') || 
  authStore.hasPermission('parent_access')
)

const showTimetableStats = computed(() => 
  authStore.hasPermission('teacher_access') || 
  authStore.hasPermission('student_access') || 
  authStore.hasPermission('parent_access')
)

const showAttendanceStats = computed(() => 
  authStore.hasPermission('teacher_access') || 
  authStore.hasPermission('admin_access')
)

const showRiskStats = computed(() => 
  authStore.hasPermission('teacher_access') || 
  authStore.hasPermission('admin_access')
)

// Méthodes
const loadDashboardData = async () => {
  try {
    // Charger les activités récentes (mock pour l'instant)
    loading.value.activities = true
    recentActivities.value = [
      {
        id: '1',
        type: 'evaluation',
        description: 'Nouvelle évaluation créée: Contrôle Mathématiques',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '2',
        type: 'attendance',
        description: 'Appel effectué pour la classe 6ème A',
        created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '3',
        type: 'alert',
        description: 'Nouvelle alerte pour Jean Dupont',
        created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
      }
    ]
    loading.value.activities = false

    // Charger l'emploi du temps du jour
    if (showTimetableStats.value) {
      loading.value.todaySchedule = true
      await timetableStore.fetchSchedules({ 
        date: new Date().toISOString().split('T')[0] 
      })
      // Filtrer pour aujourd'hui seulement
      const today = new Date().getDay()
      todaySchedule.value = timetableStore.schedules.filter(schedule => {
        const timeSlot = timetableStore.getTimeSlotById(schedule.time_slot)
        return timeSlot?.day_of_week === today
      })
      loading.value.todaySchedule = false
    }

    // Charger les alertes récentes
    if (showRiskStats.value) {
      loading.value.alerts = true
      await riskDetectionStore.fetchRecentAlerts()
      recentAlerts.value = riskDetectionStore.recentAlerts.slice(0, 5)
      loading.value.alerts = false
    }

    // Charger les échéances depuis le store des notes
    if (showGradesStats.value) {
      await gradesStore.fetchEvaluations({ limit: 10 })
      const upcoming = gradesStore.evaluations.filter(evaluation => {
        const evalDate = new Date(evaluation.date)
        const now = new Date()
        return evalDate > now
      }).slice(0, 5)
      
      upcomingDeadlines.value = upcoming.map(evaluation => ({
        id: evaluation.id,
        title: evaluation.title,
        subject_name: evaluation.subject_name || 'Matière',
        date: evaluation.date
      }))
    }

  } catch (error) {
    console.error('Erreur lors du chargement du dashboard:', error)
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'evaluation': return AcademicCapIcon
    case 'attendance': return UserGroupIcon
    case 'alert': return ExclamationTriangleIcon
    default: return ClockIcon
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'evaluation': return 'text-blue-500'
    case 'attendance': return 'text-green-500'
    case 'alert': return 'text-red-500'
    default: return 'text-gray-500'
  }
}

const getAlertBorderColor = (priority: string) => {
  switch (priority) {
    case 'urgent': return 'border-red-400'
    case 'high': return 'border-orange-400'
    case 'normal': return 'border-yellow-400'
    default: return 'border-gray-400'
  }
}

const getAlertVariant = (priority: string) => {
  switch (priority) {
    case 'urgent': return 'danger'
    case 'high': return 'warning'
    case 'normal': return 'info'
    default: return 'default'
  }
}

const getCourseStatus = (course: Schedule) => {
  const now = new Date()
  const startTime = new Date(`2024-01-01T${course.start_time}`)
  const endTime = new Date(`2024-01-01T${course.end_time}`)
  
  if (now < startTime) return 'À venir'
  if (now > endTime) return 'Terminé'
  return 'En cours'
}

const getDeadlineColor = (dateString: string) => {
  const deadline = new Date(dateString)
  const now = new Date()
  const diffDays = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffDays <= 1) return 'text-red-600'
  if (diffDays <= 3) return 'text-orange-600'
  return 'text-gray-600'
}

const goToAlert = (alert: Alert) => {
  router.push(`/risk-detection/profiles/${alert.risk_profile.id}`)
}

// Utilitaires
const formatDate = (date: Date) => {
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}

const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 60) return `il y a ${diffMins} min`
  if (diffHours < 24) return `il y a ${diffHours}h`
  return `il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`
}

const formatRelativeDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Aujourd\'hui'
  if (diffDays === 1) return 'Demain'
  if (diffDays < 7) return `Dans ${diffDays} jours`
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

// Lifecycle
onMounted(async () => {
  // Charger les données de base selon les permissions\n  const promises = []\n  \n  if (showGradesStats.value) {\n    promises.push(gradesStore.fetchEvaluations({ limit: 20 }))\n  }\n  \n  if (showTimetableStats.value) {\n    promises.push(\n      timetableStore.fetchTimeSlots(),\n      timetableStore.fetchSchedules()\n    )\n  }\n  \n  if (showAttendanceStats.value) {\n    promises.push(attendanceStore.getTodayAttendance())\n  }\n  \n  if (showRiskStats.value) {\n    promises.push(riskDetectionStore.fetchDashboard())\n  }\n  \n  await Promise.all(promises)\n  await loadDashboardData()
})
</script>