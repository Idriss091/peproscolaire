<template>
  <div class="space-y-6">
    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <BaseInput
          v-model="filters.startDate"
          type="date"
          label="Date de début"
        />
        
        <BaseInput
          v-model="filters.endDate"
          type="date"
          label="Date de fin"
        />
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Classe
          </label>
          <select
            v-model="filters.class"
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
            v-model="filters.status"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            <option value="justified">Justifiée</option>
            <option value="unjustified">Non justifiée</option>
            <option value="pending">En attente</option>
          </select>
        </div>
      </div>
      
      <div class="mt-4 flex justify-between items-center">
        <BaseButton
          variant="primary"
          @click="loadAbsences"
          class="flex items-center gap-2"
        >
          <MagnifyingGlassIcon class="w-4 h-4" />
          Rechercher
        </BaseButton>
        
        <div class="flex gap-2">
          <BaseButton
            variant="secondary"
            @click="exportAbsences"
            class="flex items-center gap-2"
          >
            <DocumentArrowDownIcon class="w-4 h-4" />
            Exporter
          </BaseButton>
          
          <BaseButton
            v-if="authStore.hasPermission('teacher_access')"
            variant="outline"
            @click="showJustifyModal = true"
            class="flex items-center gap-2"
          >
            <CheckCircleIcon class="w-4 h-4" />
            Justifier en masse
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <!-- Statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total absences</p>
            <p class="text-2xl font-semibold text-gray-900">{{ absencesStats.total }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Justifiées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ absencesStats.justified }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <XCircleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Non justifiées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ absencesStats.unjustified }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">En attente</p>
            <p class="text-2xl font-semibold text-gray-900">{{ absencesStats.pending }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Liste des absences -->
    <BaseCard>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des absences...</p>
      </div>
      
      <div v-else-if="absences.length === 0" class="text-center py-8">
        <ExclamationTriangleIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune absence trouvée</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input
                  type="checkbox"
                  @change="toggleSelectAll"
                  :checked="selectedAbsences.length === absences.length"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                >
              </th>
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
                Motif
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="absence in absences" :key="absence.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <input
                  type="checkbox"
                  :value="absence.id"
                  v-model="selectedAbsences"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                >
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ getStudentInitials(absence.student_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ absence.student_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      N° {{ absence.student_number }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ absence.class_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ formatDateTime(absence.date) }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ formatTime(absence.start_time) }} - {{ formatTime(absence.end_time) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <BaseBadge :variant="getStatusColor(absence.status)">
                  {{ getStatusLabel(absence.status) }}
                </BaseBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">
                  {{ absence.reason || '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex justify-center space-x-2">
                  <BaseButton
                    variant="outline"
                    size="sm"
                    @click="viewAbsence(absence)"
                  >
                    Voir
                  </BaseButton>
                  
                  <BaseButton
                    v-if="authStore.hasPermission('teacher_access') && absence.status !== 'justified'"
                    variant="primary"
                    size="sm"
                    @click="justifyAbsence(absence)"
                  >
                    Justifier
                  </BaseButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal de justification -->
    <BaseModal
      :is-open="showJustifyModal"
      title="Justifier les absences"
      @close="showJustifyModal = false"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Motif de justification
          </label>
          <textarea
            v-model="justificationReason"
            rows="3"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Saisir le motif de justification..."
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nombre d'absences sélectionnées: {{ selectedAbsences.length }}
          </label>
        </div>
        
        <div class="flex justify-end space-x-3">
          <BaseButton
            variant="secondary"
            @click="showJustifyModal = false"
          >
            Annuler
          </BaseButton>
          <BaseButton
            variant="primary"
            @click="confirmJustification"
            :disabled="!justificationReason.trim()"
          >
            Justifier
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedAbsence"
      :is-open="!!selectedAbsence"
      title="Détail de l'absence"
      @close="selectedAbsence = null"
    >
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Élève:</span>
            <p>{{ selectedAbsence.student_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Classe:</span>
            <p>{{ selectedAbsence.class_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Date:</span>
            <p>{{ formatDateTime(selectedAbsence.date) }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Horaires:</span>
            <p>{{ formatTime(selectedAbsence.start_time) }} - {{ formatTime(selectedAbsence.end_time) }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Statut:</span>
            <BaseBadge :variant="getStatusColor(selectedAbsence.status)">
              {{ getStatusLabel(selectedAbsence.status) }}
            </BaseBadge>
          </div>
          <div>
            <span class="font-medium text-gray-700">Motif:</span>
            <p>{{ selectedAbsence.reason || 'Aucun motif' }}</p>
          </div>
        </div>
        
        <div v-if="selectedAbsence.notes">
          <span class="font-medium text-gray-700">Notes:</span>
          <p class="mt-1 text-sm text-gray-600">{{ selectedAbsence.notes }}</p>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <BaseButton
            variant="outline"
            @click="selectedAbsence = null"
          >
            Fermer
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  MagnifyingGlassIcon,
  DocumentArrowDownIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useAttendanceStore } from '@/stores/attendance'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()

// État local
const loading = ref(false)
const selectedAbsences = ref<string[]>([])
const selectedAbsence = ref<any>(null)
const showJustifyModal = ref(false)
const justificationReason = ref('')

// Filtres
const filters = reactive({
  startDate: '',
  endDate: '',
  class: '',
  status: ''
})

// Données
const absences = ref<any[]>([])
const classes = computed(() => attendanceStore.classes)

// Statistiques
const absencesStats = computed(() => ({
  total: absences.value.length,
  justified: absences.value.filter(a => a.status === 'justified').length,
  unjustified: absences.value.filter(a => a.status === 'unjustified').length,
  pending: absences.value.filter(a => a.status === 'pending').length
}))

// Méthodes
const loadAbsences = async () => {
  loading.value = true
  try {
    // TODO: Implémenter l'API pour charger les absences
    // Simulation pour la démo
    absences.value = [
      {
        id: '1',
        student_name: 'Marie Dubois',
        student_number: '001',
        class_name: '6ème A',
        date: '2024-01-15',
        start_time: '08:00',
        end_time: '09:00',
        status: 'unjustified',
        reason: '',
        notes: ''
      },
      {
        id: '2',
        student_name: 'Pierre Martin',
        student_number: '002',
        class_name: '6ème A',
        date: '2024-01-14',
        start_time: '14:00',
        end_time: '15:00',
        status: 'justified',
        reason: 'Rendez-vous médical',
        notes: 'Certificat médical fourni'
      }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des absences:', error)
  } finally {
    loading.value = false
  }
}

const exportAbsences = async () => {
  try {
    const csvContent = generateAbsencesCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `absences-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateAbsencesCSV = () => {
  const headers = ['Élève', 'Classe', 'Date', 'Heure début', 'Heure fin', 'Statut', 'Motif']
  const rows = [headers.join(',')]
  
  absences.value.forEach(absence => {
    const row = [
      absence.student_name,
      absence.class_name,
      formatDateTime(absence.date),
      formatTime(absence.start_time),
      formatTime(absence.end_time),
      getStatusLabel(absence.status),
      absence.reason || ''
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

const toggleSelectAll = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    selectedAbsences.value = absences.value.map(a => a.id)
  } else {
    selectedAbsences.value = []
  }
}

const viewAbsence = (absence: any) => {
  selectedAbsence.value = absence
}

const justifyAbsence = (absence: any) => {
  selectedAbsences.value = [absence.id]
  showJustifyModal.value = true
}

const confirmJustification = async () => {
  loading.value = true
  try {
    // TODO: Implémenter l'API pour justifier les absences
    console.log('Justifier les absences:', selectedAbsences.value, justificationReason.value)
    
    // Simulation
    absences.value.forEach(absence => {
      if (selectedAbsences.value.includes(absence.id)) {
        absence.status = 'justified'
        absence.reason = justificationReason.value
      }
    })
    
    showJustifyModal.value = false
    selectedAbsences.value = []
    justificationReason.value = ''
  } catch (error) {
    console.error('Erreur lors de la justification:', error)
  } finally {
    loading.value = false
  }
}

// Utilitaires
const getStatusColor = (status: string) => {
  const colors = {
    justified: 'success',
    unjustified: 'danger',
    pending: 'warning'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    justified: 'Justifiée',
    unjustified: 'Non justifiée',
    pending: 'En attente'
  }
  return labels[status as keyof typeof labels] || status
}

const getStudentInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}

// Lifecycle
onMounted(async () => {
  // Définir les dates par défaut (dernier mois)
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(startDate.getMonth() - 1)
  
  filters.startDate = startDate.toISOString().split('T')[0]
  filters.endDate = endDate.toISOString().split('T')[0]
  
  await Promise.all([
    attendanceStore.fetchClasses(),
    loadAbsences()
  ])
})
</script>