<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Vie scolaire</h1>
        <p class="text-gray-600">Gestion des présences, absences et comportements</p>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          variant="outline"
          @click="exportAttendance"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter
        </BaseButton>
        
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showAttendanceModal = true"
          class="flex items-center gap-2"
        >
          <UserGroupIcon class="w-4 h-4" />
          Faire l'appel
        </BaseButton>
      </div>
    </div>

    <!-- Statistiques rapides -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UserGroupIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Présents aujourd'hui</p>
            <p class="text-2xl font-semibold text-gray-900">{{ todayStats.present }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Absents aujourd'hui</p>
            <p class="text-2xl font-semibold text-gray-900">{{ todayStats.absent }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Retards aujourd'hui</p>
            <p class="text-2xl font-semibold text-gray-900">{{ todayStats.late }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <BellAlertIcon class="h-8 w-8 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Alertes actives</p>
            <p class="text-2xl font-semibold text-gray-900">{{ activeAlerts }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Onglets -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="border-b-2 py-2 px-1 text-sm font-medium"
          :class="activeTab === tab.id
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Contenu des onglets -->
    <div v-if="activeTab === 'attendance'">
      <!-- Onglet Présences -->
      <BaseCard>
        <div class="space-y-4">
          <!-- Filtres -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <BaseInput
              :model-value="filters.date"
              @update:model-value="attendanceStore.setFilters({ date: $event })"
              type="date"
              label="Date"
            />
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Classe
              </label>
              <select
                :value="filters.class"
                @change="attendanceStore.setFilters({ class: ($event.target as HTMLSelectElement).value })"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">Toutes les classes</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Statut
              </label>
              <select
                :value="filters.status"
                @change="attendanceStore.setFilters({ status: ($event.target as HTMLSelectElement).value })"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">Tous les statuts</option>
                <option value="present">Présent</option>
                <option value="absent">Absent</option>
                <option value="late">Retard</option>
                <option value="excused">Excusé</option>
              </select>
            </div>
            
            <BaseButton
              variant="primary"
              @click="loadAttendance"
              class="self-end"
            >
              Filtrer
            </BaseButton>
          </div>
          
          <!-- Liste des présences -->
          <div v-if="loading.attendance" class="text-center py-8">
            <LoadingSpinner />
            <p class="mt-2 text-gray-600">Chargement des présences...</p>
          </div>
          
          <div v-else-if="attendanceRecords.length === 0" class="text-center py-8">
            <UserGroupIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">Aucun enregistrement de présence trouvé</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Élève
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Classe
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date/Heure
                  </th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Commentaire
                  </th>
                  <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="record in attendanceRecords" :key="record.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      {{ record.student_name }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">
                      {{ record.class_name }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">
                      {{ formatDateTime(record.date) }}
                    </div>
                    <div v-if="record.arrival_time" class="text-xs text-gray-500">
                      Arrivée: {{ formatTime(record.arrival_time) }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <BaseBadge :variant="getStatusColor(record.status)">
                      {{ getStatusLabel(record.status) }}
                    </BaseBadge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">
                      {{ record.comment || '-' }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <BaseButton
                      variant="outline"
                      size="sm"
                      @click="editAttendance(record)"
                    >
                      Modifier
                    </BaseButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </BaseCard>
    </div>

    <div v-else-if="activeTab === 'absences'">
      <!-- Onglet Absences -->
      <AbsencesView />
    </div>

    <div v-else-if="activeTab === 'behavior'">
      <!-- Onglet Comportement -->
      <BehaviorView />
    </div>

    <div v-else-if="activeTab === 'sanctions'">
      <!-- Onglet Sanctions -->
      <SanctionsView />
    </div>

    <!-- Modal pour faire l'appel -->
    <BaseModal
      v-if="showAttendanceModal"
      :is-open="showAttendanceModal"
      title="Faire l'appel"
      size="lg"
      @close="showAttendanceModal = false"
    >
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Classe
            </label>
            <select
              v-model="attendanceForm.class"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner une classe</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <BaseInput
              v-model="attendanceForm.date"
              type="date"
            />
          </div>
        </div>
        
        <div v-if="!attendanceForm.class" class="text-center py-8 text-gray-500">
          Sélectionnez une classe pour commencer l'appel
        </div>
        
        <AttendanceSheet
          v-else-if="classStudents.length > 0"
          :students="classStudents"
          :class-info="selectedClassInfo"
          :date="attendanceForm.date"
          @save="handleAttendanceSave"
        />
        
        <div v-if="!attendanceForm.class || classStudents.length === 0" class="flex justify-end gap-3">
          <BaseButton
            variant="outline"
            @click="showAttendanceModal = false"
          >
            Annuler
          </BaseButton>
          <BaseButton
            variant="primary"
            :disabled="!attendanceForm.class"
            @click="startAttendanceCall"
          >
            Commencer l'appel
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import {
  UserGroupIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  BellAlertIcon,
  DocumentArrowDownIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useAttendanceStore } from '@/stores/attendance'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AbsencesView from '@/components/attendance/AbsencesView.vue'
import BehaviorView from '@/components/attendance/BehaviorView.vue'
import SanctionsView from '@/components/attendance/SanctionsView.vue'
import AttendanceSheet from '@/components/attendance/AttendanceSheet.vue'

import type { Attendance } from '@/types'

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()

// État local
const activeTab = ref('attendance')
const showAttendanceModal = ref(false)
const classStudents = ref<any[]>([])
const selectedClassInfo = ref<any>(null)

// Computed
const loading = computed(() => attendanceStore.loading)
const attendanceRecords = computed(() => attendanceStore.filteredAttendance)
const classes = computed(() => attendanceStore.classes)
const todayStats = computed(() => attendanceStore.todayStats)
const activeAlerts = ref(0)

// Filtres
const filters = computed(() => attendanceStore.filters)

// Formulaire d'appel
const attendanceForm = reactive({
  class: '',
  date: new Date().toISOString().split('T')[0]
})

// Onglets
const tabs = [
  { id: 'attendance', name: 'Présences' },
  { id: 'absences', name: 'Absences' },
  { id: 'behavior', name: 'Comportement' },
  { id: 'sanctions', name: 'Sanctions' }
]

// Méthodes
const loadAttendance = async () => {
  const params: any = {}
  
  if (filters.value.date) params.date = filters.value.date
  if (filters.value.class) params.class_group = filters.value.class
  if (filters.value.status) params.status = filters.value.status
  
  await attendanceStore.fetchAttendance(params)
}

const loadStats = async () => {
  await attendanceStore.fetchAttendanceStats(filters.value.date)
  // TODO: Charger les alertes actives
  activeAlerts.value = 3
}

const editAttendance = async (record: Attendance) => {
  try {
    // TODO: Ouvrir modal d'édition
    console.log('Éditer la présence:', record.id)
  } catch (error) {
    console.error('Erreur lors de l\'édition:', error)
  }
}

const startAttendanceCall = async () => {
  try {
    if (!attendanceForm.class) return
    
    // Charger les élèves de la classe sélectionnée
    await loadClassStudents(attendanceForm.class)
    
    // Charger les informations de la classe
    selectedClassInfo.value = classes.value.find(c => c.id === attendanceForm.class)
    
    console.log('Commencer l\'appel pour la classe:', attendanceForm.class)
  } catch (error) {
    console.error('Erreur lors du démarrage de l\'appel:', error)
  }
}

const loadClassStudents = async (classId: string) => {
  try {
    // TODO: Implémenter l'API pour charger les élèves d'une classe
    // Simulation pour la démo
    classStudents.value = [
      {
        id: '1',
        first_name: 'Marie',
        last_name: 'Dubois',
        student_number: '001'
      },
      {
        id: '2',
        first_name: 'Pierre',
        last_name: 'Martin',
        student_number: '002'
      },
      {
        id: '3',
        first_name: 'Sophie',
        last_name: 'Blanc',
        student_number: '003'
      }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des élèves:', error)
  }
}

const handleAttendanceSave = async (attendanceData: any) => {
  try {
    // TODO: Implémenter l'API pour sauvegarder l'appel
    console.log('Sauvegarder l\'appel:', attendanceData)
    
    // Simulation de sauvegarde
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    showAttendanceModal.value = false
    
    // Recharger les données d'attendance
    await loadAttendance()
  } catch (error) {
    console.error('Erreur lors de la sauvegarde de l\'appel:', error)
  }
}

const exportAttendance = async () => {
  try {
    await attendanceStore.exportAttendance({
      date_from: filters.value.date,
      date_to: filters.value.date,
      class_group: filters.value.class,
      format: 'csv'
    })
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

// Utilitaires
const getStatusColor = (status: string) => {
  return attendanceStore.getStatusColor(status)
}

const getStatusLabel = (status: string) => {
  return attendanceStore.getStatusLabel(status)
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR')
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}

// Lifecycle
onMounted(async () => {
  // Charger les données initiales
  await Promise.all([
    attendanceStore.fetchClasses(),
    attendanceStore.getTodayAttendance()
  ])
})
</script>