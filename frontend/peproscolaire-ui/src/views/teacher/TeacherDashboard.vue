<template>
  <div class="space-y-6">
    <!-- Welcome header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900">
        Bonjour {{ userFirstName }} 👋
      </h1>
      <p class="mt-1 text-gray-600">
        {{ currentDate }}
      </p>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        v-for="stat in stats"
        :key="stat.name"
        :title="stat.name"
        :value="stat.value"
        :icon="stat.icon"
        :color="stat.color"
        :loading="loading"
      />
    </div>

    <!-- Main content grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Today's schedule -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">
            Emploi du temps du jour
          </h2>
        </div>
        <div class="p-6">
          <div v-if="loadingSchedule" class="space-y-3">
            <div v-for="i in 3" :key="i" class="animate-pulse">
              <div class="h-20 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div v-else-if="todaySchedule.length === 0" class="text-center py-8">
            <CalendarIcon class="mx-auto h-12 w-12 text-gray-400" />
            <p class="mt-2 text-sm text-gray-500">
              Aucun cours aujourd'hui
            </p>
          </div>
          <div v-else class="space-y-3">
            <ScheduleItem
              v-for="item in todaySchedule"
              :key="item.id"
              :schedule="item"
              @click="goToTimetable"
            />
          </div>
        </div>
      </div>

      <!-- Pending attendance -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">
            Appels à faire
          </h2>
          <span 
            v-if="pendingAttendance.length > 0"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
          >
            {{ pendingAttendance.length }}
          </span>
        </div>
        <div class="p-6">
          <div v-if="loadingAttendance" class="space-y-3">
            <div v-for="i in 2" :key="i" class="animate-pulse">
              <div class="h-16 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div v-else-if="pendingAttendance.length === 0" class="text-center py-8">
            <CheckCircleIcon class="mx-auto h-12 w-12 text-green-400" />
            <p class="mt-2 text-sm text-gray-500">
              Tous les appels sont faits
            </p>
          </div>
          <div v-else class="space-y-3">
            <AttendanceCard
              v-for="attendance in pendingAttendance"
              :key="attendance.id"
              :attendance="attendance"
              @mark="goToAttendance(attendance)"
            />
          </div>
        </div>
      </div>

      <!-- Recent homework -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">
            Devoirs récents
          </h2>
          <router-link
            to="/teacher/homework"
            class="text-sm text-indigo-600 hover:text-indigo-500"
          >
            Voir tout
          </router-link>
        </div>
        <div class="p-6">
          <div v-if="loadingHomework" class="space-y-3">
            <div v-for="i in 3" :key="i" class="animate-pulse">
              <div class="h-12 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div v-else-if="recentHomework.length === 0" class="text-center py-8">
            <BookOpenIcon class="mx-auto h-12 w-12 text-gray-400" />
            <p class="mt-2 text-sm text-gray-500">
              Aucun devoir récent
            </p>
          </div>
          <div v-else class="space-y-3">
            <HomeworkItem
              v-for="homework in recentHomework"
              :key="homework.id"
              :homework="homework"
              @click="goToHomework(homework)"
            />
          </div>
        </div>
      </div>

      <!-- Student alerts -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">
            Alertes élèves
          </h2>
          <router-link
            to="/teacher/risk-detection"
            class="text-sm text-indigo-600 hover:text-indigo-500"
          >
            Voir tout
          </router-link>
        </div>
        <div class="p-6">
          <div v-if="loadingAlerts" class="space-y-3">
            <div v-for="i in 2" :key="i" class="animate-pulse">
              <div class="h-16 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div v-else-if="studentAlerts.length === 0" class="text-center py-8">
            <ShieldCheckIcon class="mx-auto h-12 w-12 text-green-400" />
            <p class="mt-2 text-sm text-gray-500">
              Aucune alerte active
            </p>
          </div>
          <div v-else class="space-y-3">
            <AlertCard
              v-for="alert in studentAlerts"
              :key="alert.id"
              :alert="alert"
              compact
              @click="goToRiskDetection(alert)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Recent messages -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-medium text-gray-900">
          Messages récents
        </h2>
        <router-link
          to="/teacher/messages"
          class="text-sm text-indigo-600 hover:text-indigo-500"
        >
          Voir tout
        </router-link>
      </div>
      <div class="p-6">
        <div v-if="loadingMessages" class="space-y-3">
          <div v-for="i in 3" :key="i" class="animate-pulse">
            <div class="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
        <div v-else-if="recentMessages.length === 0" class="text-center py-8">
          <EnvelopeIcon class="mx-auto h-12 w-12 text-gray-400" />
          <p class="mt-2 text-sm text-gray-500">
            Aucun message récent
          </p>
        </div>
        <div v-else class="divide-y divide-gray-200">
          <MessagePreview
            v-for="message in recentMessages"
            :key="message.id"
            :message="message"
            @click="goToMessage(message)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTimetableStore } from '@/stores/timetable'
import { useAttendanceStore } from '@/stores/attendance'
import { useHomeworkStore } from '@/stores/homework'
import { useMessagingStore } from '@/stores/messaging'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import StatCard from '@/components/dashboard/StatCard.vue'
import ScheduleItem from '@/components/timetable/ScheduleItem.vue'
import AttendanceCard from '@/components/attendance/AttendanceCard.vue'
import HomeworkItem from '@/components/homework/HomeworkItem.vue'
import AlertCard from '@/components/risk-detection/AlertCard.vue'
import MessagePreview from '@/components/messaging/MessagePreview.vue'
import {
  CalendarIcon,
  CheckCircleIcon,
  BookOpenIcon,
  ShieldCheckIcon,
  EnvelopeIcon,
  UserGroupIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const timetableStore = useTimetableStore()
const attendanceStore = useAttendanceStore()
const homeworkStore = useHomeworkStore()
const messagingStore = useMessagingStore()
const riskDetectionStore = useRiskDetectionStore()

// User info
const userFirstName = computed(() => authStore.user?.first_name || '')
const currentDate = computed(() => 
  format(new Date(), "EEEE d MMMM yyyy", { locale: fr })
)

// Loading states
const loading = ref(true)
const loadingSchedule = ref(true)
const loadingAttendance = ref(true)
const loadingHomework = ref(true)
const loadingMessages = ref(true)
const loadingAlerts = ref(true)

// Data
const todaySchedule = ref([])
const pendingAttendance = ref([])
const recentHomework = ref([])
const recentMessages = ref([])
const studentAlerts = ref([])

// Stats
const stats = computed(() => [
  {
    name: 'Classes aujourd\'hui',
    value: todaySchedule.value.length,
    icon: CalendarIcon,
    color: 'blue'
  },
  {
    name: 'Appels en attente',
    value: pendingAttendance.value.length,
    icon: ClipboardDocumentCheckIcon,
    color: pendingAttendance.value.length > 0 ? 'red' : 'green'
  },
  {
    name: 'Élèves suivis',
    value: '124',
    icon: UserGroupIcon,
    color: 'indigo'
  },
  {
    name: 'Alertes actives',
    value: studentAlerts.value.length,
    icon: ExclamationTriangleIcon,
    color: studentAlerts.value.length > 0 ? 'yellow' : 'green'
  }
])

// Load data
onMounted(async () => {
  // Load today's schedule
  loadingSchedule.value = true
  try {
    await timetableStore.fetchTodaySchedule()
    todaySchedule.value = timetableStore.todaySchedule
  } catch (error) {
    console.error('Failed to load schedule:', error)
  } finally {
    loadingSchedule.value = false
  }

  // Load pending attendance
  loadingAttendance.value = true
  try {
    await attendanceStore.fetchPendingAttendance()
    pendingAttendance.value = attendanceStore.pendingAttendance
  } catch (error) {
    console.error('Failed to load attendance:', error)
  } finally {
    loadingAttendance.value = false
  }

  // Load recent homework
  loadingHomework.value = true
  try {
    await homeworkStore.fetchRecentHomework()
    recentHomework.value = homeworkStore.recentHomework.slice(0, 5)
  } catch (error) {
    console.error('Failed to load homework:', error)
  } finally {
    loadingHomework.value = false
  }

  // Load recent messages
  loadingMessages.value = true
  try {
    await messagingStore.fetchMessages({ folder: 'inbox', limit: 5 })
    recentMessages.value = messagingStore.messages.slice(0, 5)
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    loadingMessages.value = false
  }

  // Load student alerts
  loadingAlerts.value = true
  try {
    await riskDetectionStore.fetchAlerts({ is_resolved: false, limit: 5 })
    studentAlerts.value = riskDetectionStore.alerts.slice(0, 5)
  } catch (error) {
    console.error('Failed to load alerts:', error)
  } finally {
    loadingAlerts.value = false
  }

  loading.value = false
})

// Navigation helpers
const goToTimetable = () => router.push('/teacher/timetable')
const goToAttendance = (attendance: any) => {
  router.push(`/teacher/attendance?class=${attendance.class_id}`)
}
const goToHomework = (homework: any) => {
  router.push(`/teacher/homework/${homework.id}`)
}
const goToMessage = (message: any) => {
  router.push(`/teacher/messages/${message.id}`)
}
const goToRiskDetection = (alert: any) => {
  router.push(`/teacher/risk-detection/students/${alert.student_id}`)
}
</script>