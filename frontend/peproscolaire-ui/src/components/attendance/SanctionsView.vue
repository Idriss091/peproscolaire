<template>
  <div class="space-y-6">
    <!-- Actions rapides -->
    <div class="flex justify-between items-center">
      <div class="flex gap-3">
        <BaseButton
          variant="primary"
          @click="showAddSanctionModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Ajouter une sanction
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          @click="exportSanctions"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter
        </BaseButton>
      </div>
      
      <div class="flex items-center gap-2">
        <BaseInput
          v-model="searchTerm"
          placeholder="Rechercher un élève..."
          size="sm"
          class="w-64"
        />
      </div>
    </div>

    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
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
            Type
          </label>
          <select
            v-model="filters.type"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            <option v-for="type in sanctionTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
        
        <BaseButton
          variant="primary"
          @click="loadSanctions"
          class="self-end"
        >
          Filtrer
        </BaseButton>
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
            <p class="text-sm font-medium text-gray-500">Total sanctions</p>
            <p class="text-2xl font-semibold text-gray-900">{{ sanctionsStats.total }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">En cours</p>
            <p class="text-2xl font-semibold text-gray-900">{{ sanctionsStats.active }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Terminées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ sanctionsStats.completed }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <XCircleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Annulées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ sanctionsStats.cancelled }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Liste des sanctions -->
    <BaseCard>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des sanctions...</p>
      </div>
      
      <div v-else-if="filteredSanctions.length === 0" class="text-center py-8">
        <ExclamationTriangleIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune sanction trouvée</p>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="sanction in filteredSanctions"
          :key="sanction.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
          :class="{
            'border-red-200 bg-red-50': sanction.severity >= 4,
            'border-yellow-200 bg-yellow-50': sanction.severity >= 2 && sanction.severity < 4,
            'border-gray-200 bg-gray-50': sanction.severity < 2
          }"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4">
              <!-- Avatar élève -->
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getStudentInitials(sanction.student_name) }}
                  </span>
                </div>
              </div>
              
              <!-- Informations -->
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h3 class="text-sm font-medium text-gray-900">
                    {{ sanction.student_name }}
                  </h3>
                  <span class="text-sm text-gray-500">
                    {{ sanction.class_name }}
                  </span>
                  <BaseBadge :variant="getSanctionStatusColor(sanction.status)">
                    {{ getSanctionStatusLabel(sanction.status) }}
                  </BaseBadge>
                </div>
                
                <div class="mt-1 flex items-center space-x-4 text-sm text-gray-600">
                  <span><strong>{{ sanction.type }}</strong></span>
                  <span class="flex items-center">
                    Gravité: 
                    <div class="ml-1 flex">
                      <div
                        v-for="i in 5"
                        :key="i"
                        class="w-2 h-2 rounded-full mr-1"
                        :class="i <= sanction.severity ? 'bg-red-500' : 'bg-gray-300'"
                      />
                    </div>
                  </span>
                </div>
                
                <p class="mt-2 text-sm text-gray-800">
                  <strong>Motif:</strong> {{ sanction.reason }}
                </p>
                
                <p class="mt-1 text-sm text-gray-700">
                  <strong>Sanction:</strong> {{ sanction.description }}
                </p>
                
                <div class="mt-2 grid grid-cols-2 gap-4 text-xs text-gray-500">
                  <div>
                    <span class="font-medium">Prononcée le:</span>
                    {{ formatDateTime(sanction.date_issued) }}
                  </div>
                  <div>
                    <span class="font-medium">Échéance:</span>
                    {{ formatDateTime(sanction.date_due) }}
                  </div>
                  <div>
                    <span class="font-medium">Professeur:</span>
                    {{ sanction.teacher_name }}
                  </div>
                  <div v-if="sanction.date_completed">
                    <span class="font-medium">Terminée le:</span>
                    {{ formatDateTime(sanction.date_completed) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center space-x-2">
              <BaseButton
                variant="outline"
                size="sm"
                @click="viewSanction(sanction)"
              >
                Voir
              </BaseButton>
              
              <BaseButton
                v-if="sanction.status === 'active'"
                variant="success"
                size="sm"
                @click="completeSanction(sanction.id)"
              >
                Terminer
              </BaseButton>
              
              <BaseButton
                v-if="sanction.status === 'active'"
                variant="warning"
                size="sm"
                @click="editSanction(sanction)"
              >
                Modifier
              </BaseButton>
              
              <BaseButton
                v-if="sanction.status === 'active'"
                variant="danger"
                size="sm"
                @click="cancelSanction(sanction.id)"
              >
                Annuler
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Modal d'ajout/modification -->
    <BaseModal
      :is-open="showAddSanctionModal"
      :title="editingSanction ? 'Modifier la sanction' : 'Ajouter une sanction'"
      @close="closeAddSanctionModal"
      size="lg"
    >
      <form @submit.prevent="saveSanction" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Élève *
            </label>
            <select
              v-model="sanctionForm.student"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner un élève</option>
              <option v-for="student in students" :key="student.id" :value="student.id">
                {{ student.first_name }} {{ student.last_name }} - {{ student.class_name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Type de sanction *
            </label>
            <select
              v-model="sanctionForm.type"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner un type</option>
              <option v-for="type in sanctionTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Gravité (1-5) *
            </label>
            <select
              v-model="sanctionForm.severity"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner</option>
              <option value="1">1 - Très faible</option>
              <option value="2">2 - Faible</option>
              <option value="3">3 - Moyenne</option>
              <option value="4">4 - Élevée</option>
              <option value="5">5 - Très élevée</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date d'échéance
            </label>
            <BaseInput
              v-model="sanctionForm.dateDue"
              type="date"
            />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Motif *
          </label>
          <textarea
            v-model="sanctionForm.reason"
            rows="3"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Décrire le motif de la sanction..."
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description de la sanction *
          </label>
          <textarea
            v-model="sanctionForm.description"
            rows="3"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Décrire précisément la sanction à effectuer..."
          />
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <BaseButton
            type="button"
            variant="secondary"
            @click="closeAddSanctionModal"
          >
            Annuler
          </BaseButton>
          
          <BaseButton
            type="submit"
            variant="primary"
            :loading="saving"
          >
            {{ editingSanction ? 'Modifier' : 'Ajouter' }}
          </BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedSanction"
      :is-open="!!selectedSanction"
      title="Détail de la sanction"
      @close="selectedSanction = null"
      size="lg"
    >
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Élève:</span>
            <p>{{ selectedSanction.student_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Classe:</span>
            <p>{{ selectedSanction.class_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Type:</span>
            <p>{{ selectedSanction.type }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Statut:</span>
            <BaseBadge :variant="getSanctionStatusColor(selectedSanction.status)">
              {{ getSanctionStatusLabel(selectedSanction.status) }}
            </BaseBadge>
          </div>
          <div>
            <span class="font-medium text-gray-700">Gravité:</span>
            <div class="flex items-center">
              <div class="flex mr-2">
                <div
                  v-for="i in 5"
                  :key="i"
                  class="w-3 h-3 rounded-full mr-1"
                  :class="i <= selectedSanction.severity ? 'bg-red-500' : 'bg-gray-300'"
                />
              </div>
              <span>{{ selectedSanction.severity }}/5</span>
            </div>
          </div>
          <div>
            <span class="font-medium text-gray-700">Professeur:</span>
            <p>{{ selectedSanction.teacher_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Date prononcée:</span>
            <p>{{ formatDateTime(selectedSanction.date_issued) }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Échéance:</span>
            <p>{{ formatDateTime(selectedSanction.date_due) }}</p>
          </div>
        </div>
        
        <div>
          <span class="font-medium text-gray-700">Motif:</span>
          <p class="mt-1 text-sm text-gray-600">{{ selectedSanction.reason }}</p>
        </div>
        
        <div>
          <span class="font-medium text-gray-700">Description de la sanction:</span>
          <p class="mt-1 text-sm text-gray-600">{{ selectedSanction.description }}</p>
        </div>
        
        <div v-if="selectedSanction.notes">
          <span class="font-medium text-gray-700">Notes:</span>
          <p class="mt-1 text-sm text-gray-600">{{ selectedSanction.notes }}</p>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <BaseButton
            variant="outline"
            @click="selectedSanction = null"
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
  PlusIcon,
  DocumentArrowDownIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
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
const saving = ref(false)
const searchTerm = ref('')
const showAddSanctionModal = ref(false)
const editingSanction = ref<any>(null)
const selectedSanction = ref<any>(null)

// Filtres
const filters = reactive({
  startDate: '',
  endDate: '',
  class: '',
  type: ''
})

// Formulaire
const sanctionForm = reactive({
  student: '',
  type: '',
  severity: '',
  reason: '',
  description: '',
  dateDue: ''
})

// Données
const sanctions = ref<any[]>([])
const students = ref<any[]>([])
const classes = computed(() => attendanceStore.classes)

// Types de sanctions
const sanctionTypes = [
  'Avertissement',
  'Blâme',
  'Exclusion temporaire',
  'Exclusion définitive',
  'Travail d\'intérêt général',
  'Retenue',
  'Convocation des parents',
  'Rapport disciplinaire',
  'Mise à pied',
  'Autre'
]

// Computed
const filteredSanctions = computed(() => {
  let filtered = sanctions.value
  
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(sanction => 
      sanction.student_name.toLowerCase().includes(term) ||
      sanction.reason.toLowerCase().includes(term) ||
      sanction.description.toLowerCase().includes(term)
    )
  }
  
  return filtered.sort((a, b) => new Date(b.date_issued).getTime() - new Date(a.date_issued).getTime())
})

const sanctionsStats = computed(() => ({
  total: sanctions.value.length,
  active: sanctions.value.filter(s => s.status === 'active').length,
  completed: sanctions.value.filter(s => s.status === 'completed').length,
  cancelled: sanctions.value.filter(s => s.status === 'cancelled').length
}))

// Méthodes
const loadSanctions = async () => {
  loading.value = true
  try {
    // TODO: Implémenter l'API pour charger les sanctions
    // Simulation pour la démo
    sanctions.value = [
      {
        id: '1',
        student_name: 'Pierre Martin',
        class_name: '6ème A',
        type: 'Retenue',
        severity: 3,
        reason: 'Comportement perturbateur répété en cours de mathématiques.',
        description: 'Retenue de 2 heures le mercredi après-midi avec travail supplémentaire.',
        date_issued: '2024-01-15',
        date_due: '2024-01-17',
        date_completed: null,
        status: 'active',
        teacher_name: 'M. Dupont',
        notes: ''
      },
      {
        id: '2',
        student_name: 'Sophie Blanc',
        class_name: '6ème B',
        type: 'Avertissement',
        severity: 2,
        reason: 'Bavardages persistants malgré plusieurs rappels.',
        description: 'Avertissement écrit avec notification aux parents.',
        date_issued: '2024-01-12',
        date_due: '2024-01-12',
        date_completed: '2024-01-12',
        status: 'completed',
        teacher_name: 'Mme Leroy',
        notes: 'Parents informés'
      },
      {
        id: '3',
        student_name: 'Marc Durand',
        class_name: '5ème A',
        type: 'Exclusion temporaire',
        severity: 5,
        reason: 'Violence physique envers un camarade.',
        description: 'Exclusion de 3 jours avec convocation des parents et suivi disciplinaire.',
        date_issued: '2024-01-10',
        date_due: '2024-01-13',
        date_completed: '2024-01-13',
        status: 'completed',
        teacher_name: 'M. Bernard',
        notes: 'Suivi psychologique recommandé'
      }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des sanctions:', error)
  } finally {
    loading.value = false
  }
}

const loadStudents = async () => {
  try {
    // TODO: Implémenter l'API pour charger les élèves
    students.value = [
      { id: '1', first_name: 'Marie', last_name: 'Dubois', class_name: '6ème A' },
      { id: '2', first_name: 'Pierre', last_name: 'Martin', class_name: '6ème A' },
      { id: '3', first_name: 'Sophie', last_name: 'Blanc', class_name: '6ème B' },
      { id: '4', first_name: 'Marc', last_name: 'Durand', class_name: '5ème A' }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des élèves:', error)
  }
}

const saveSanction = async () => {
  saving.value = true
  try {
    // TODO: Implémenter l'API pour sauvegarder la sanction
    console.log('Sauvegarder la sanction:', sanctionForm)
    
    // Simulation
    const newSanction = {
      id: Date.now().toString(),
      student_name: students.value.find(s => s.id === sanctionForm.student)?.first_name + ' ' + 
                    students.value.find(s => s.id === sanctionForm.student)?.last_name,
      class_name: students.value.find(s => s.id === sanctionForm.student)?.class_name,
      type: sanctionForm.type,
      severity: parseInt(sanctionForm.severity),
      reason: sanctionForm.reason,
      description: sanctionForm.description,
      date_issued: new Date().toISOString().split('T')[0],
      date_due: sanctionForm.dateDue,
      date_completed: null,
      status: 'active',
      teacher_name: authStore.user?.first_name + ' ' + authStore.user?.last_name,
      notes: ''
    }
    
    if (editingSanction.value) {
      const index = sanctions.value.findIndex(s => s.id === editingSanction.value.id)
      if (index !== -1) {
        sanctions.value[index] = { ...editingSanction.value, ...newSanction }
      }
    } else {
      sanctions.value.unshift(newSanction)
    }
    
    closeAddSanctionModal()
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error)
  } finally {
    saving.value = false
  }
}

const viewSanction = (sanction: any) => {
  selectedSanction.value = sanction
}

const editSanction = (sanction: any) => {
  editingSanction.value = sanction
  Object.assign(sanctionForm, {
    student: sanction.student_id || '',
    type: sanction.type,
    severity: sanction.severity.toString(),
    reason: sanction.reason,
    description: sanction.description,
    dateDue: sanction.date_due
  })
  showAddSanctionModal.value = true
}

const completeSanction = async (sanctionId: string) => {
  if (!confirm('Marquer cette sanction comme terminée ?')) {
    return
  }
  
  try {
    // TODO: Implémenter l'API pour terminer la sanction
    console.log('Terminer la sanction:', sanctionId)
    
    // Simulation
    const sanction = sanctions.value.find(s => s.id === sanctionId)
    if (sanction) {
      sanction.status = 'completed'
      sanction.date_completed = new Date().toISOString().split('T')[0]
    }
  } catch (error) {
    console.error('Erreur lors de la finalisation:', error)
  }
}

const cancelSanction = async (sanctionId: string) => {
  if (!confirm('Annuler cette sanction ? Cette action est irréversible.')) {
    return
  }
  
  try {
    // TODO: Implémenter l'API pour annuler la sanction
    console.log('Annuler la sanction:', sanctionId)
    
    // Simulation
    const sanction = sanctions.value.find(s => s.id === sanctionId)
    if (sanction) {
      sanction.status = 'cancelled'
    }
  } catch (error) {
    console.error('Erreur lors de l\'annulation:', error)
  }
}

const closeAddSanctionModal = () => {
  showAddSanctionModal.value = false
  editingSanction.value = null
  Object.assign(sanctionForm, {
    student: '',
    type: '',
    severity: '',
    reason: '',
    description: '',
    dateDue: ''
  })
}

const exportSanctions = async () => {
  try {
    const csvContent = generateSanctionsCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `sanctions-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateSanctionsCSV = () => {
  const headers = ['Élève', 'Classe', 'Type', 'Gravité', 'Motif', 'Description', 'Date prononcée', 'Échéance', 'Statut', 'Professeur']
  const rows = [headers.join(',')]
  
  sanctions.value.forEach(sanction => {
    const row = [
      sanction.student_name,
      sanction.class_name,
      sanction.type,
      sanction.severity,
      sanction.reason.replace(/,/g, ';'),
      sanction.description.replace(/,/g, ';'),
      formatDateTime(sanction.date_issued),
      formatDateTime(sanction.date_due),
      getSanctionStatusLabel(sanction.status),
      sanction.teacher_name
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getSanctionStatusColor = (status: string) => {
  const colors = {
    active: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getSanctionStatusLabel = (status: string) => {
  const labels = {
    active: 'En cours',
    completed: 'Terminée',
    cancelled: 'Annulée'
  }
  return labels[status as keyof typeof labels] || status
}

const getStudentInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
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
    loadSanctions(),
    loadStudents()
  ])
})
</script>