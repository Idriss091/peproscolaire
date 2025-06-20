<template>
  <div class="space-y-6">
    <!-- Actions rapides -->
    <div class="flex justify-between items-center">
      <div class="flex gap-3">
        <BaseButton
          variant="primary"
          @click="showAddBehaviorModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Ajouter un comportement
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          @click="exportBehaviors"
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
            <option value="positive">Positif</option>
            <option value="negative">Négatif</option>
            <option value="neutral">Neutre</option>
          </select>
        </div>
        
        <BaseButton
          variant="primary"
          @click="loadBehaviors"
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
            <ChatBubbleLeftEllipsisIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total</p>
            <p class="text-2xl font-semibold text-gray-900">{{ behaviorStats.total }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <HandThumbUpIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Positifs</p>
            <p class="text-2xl font-semibold text-gray-900">{{ behaviorStats.positive }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <HandThumbDownIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Négatifs</p>
            <p class="text-2xl font-semibold text-gray-900">{{ behaviorStats.negative }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <MinusIcon class="h-8 w-8 text-gray-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Neutres</p>
            <p class="text-2xl font-semibold text-gray-900">{{ behaviorStats.neutral }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Liste des comportements -->
    <BaseCard>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des comportements...</p>
      </div>
      
      <div v-else-if="filteredBehaviors.length === 0" class="text-center py-8">
        <ChatBubbleLeftEllipsisIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucun comportement trouvé</p>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="behavior in filteredBehaviors"
          :key="behavior.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
          :class="{
            'border-green-200 bg-green-50': behavior.type === 'positive',
            'border-red-200 bg-red-50': behavior.type === 'negative',
            'border-gray-200 bg-gray-50': behavior.type === 'neutral'
          }"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4">
              <!-- Avatar élève -->
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getStudentInitials(behavior.student_name) }}
                  </span>
                </div>
              </div>
              
              <!-- Informations -->
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h3 class="text-sm font-medium text-gray-900">
                    {{ behavior.student_name }}
                  </h3>
                  <span class="text-sm text-gray-500">
                    {{ behavior.class_name }}
                  </span>
                  <BaseBadge :variant="getBehaviorTypeColor(behavior.type)">
                    {{ getBehaviorTypeLabel(behavior.type) }}
                  </BaseBadge>
                </div>
                
                <div class="mt-1 text-sm text-gray-600">
                  <strong>{{ behavior.category }}</strong>
                  <span v-if="behavior.subject"> - {{ behavior.subject }}</span>
                </div>
                
                <p class="mt-2 text-sm text-gray-800">
                  {{ behavior.description }}
                </p>
                
                <div class="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                  <span>{{ formatDateTime(behavior.date) }}</span>
                  <span>{{ behavior.teacher_name }}</span>
                  <span v-if="behavior.severity">Gravité: {{ behavior.severity }}/5</span>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center space-x-2">
              <BaseButton
                variant="outline"
                size="sm"
                @click="editBehavior(behavior)"
              >
                Modifier
              </BaseButton>
              
              <BaseButton
                variant="danger"
                size="sm"
                @click="deleteBehavior(behavior.id)"
              >
                Supprimer
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Modal d'ajout/modification -->
    <BaseModal
      :is-open="showAddBehaviorModal"
      :title="editingBehavior ? 'Modifier le comportement' : 'Ajouter un comportement'"
      @close="closeAddBehaviorModal"
      size="lg"
    >
      <form @submit.prevent="saveBehavior" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Élève *
            </label>
            <select
              v-model="behaviorForm.student"
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
              Type *
            </label>
            <select
              v-model="behaviorForm.type"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner un type</option>
              <option value="positive">Positif</option>
              <option value="negative">Négatif</option>
              <option value="neutral">Neutre</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Catégorie *
            </label>
            <select
              v-model="behaviorForm.category"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner une catégorie</option>
              <option v-for="cat in behaviorCategories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Matière
            </label>
            <select
              v-model="behaviorForm.subject"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Aucune matière spécifique</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
                {{ subject.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </label>
            <BaseInput
              v-model="behaviorForm.date"
              type="date"
              required
            />
          </div>
          
          <div v-if="behaviorForm.type === 'negative'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Gravité (1-5)
            </label>
            <select
              v-model="behaviorForm.severity"
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
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            v-model="behaviorForm.description"
            rows="4"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Décrire le comportement observé..."
          />
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <BaseButton
            type="button"
            variant="secondary"
            @click="closeAddBehaviorModal"
          >
            Annuler
          </BaseButton>
          
          <BaseButton
            type="submit"
            variant="primary"
            :loading="saving"
          >
            {{ editingBehavior ? 'Modifier' : 'Ajouter' }}
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  PlusIcon,
  DocumentArrowDownIcon,
  ChatBubbleLeftEllipsisIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  MinusIcon
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
const showAddBehaviorModal = ref(false)
const editingBehavior = ref<any>(null)

// Filtres
const filters = reactive({
  startDate: '',
  endDate: '',
  class: '',
  type: ''
})

// Formulaire
const behaviorForm = reactive({
  student: '',
  type: '',
  category: '',
  subject: '',
  date: '',
  severity: '',
  description: ''
})

// Données
const behaviors = ref<any[]>([])
const students = ref<any[]>([])
const subjects = ref<any[]>([])
const classes = computed(() => attendanceStore.classes)

// Catégories de comportement
const behaviorCategories = [
  'Participation',
  'Respect des règles',
  'Travail en équipe',
  'Ponctualité',
  'Effort',
  'Aide aux autres',
  'Perturbation',
  'Insolence',
  'Tricherie',
  'Violence verbale',
  'Violence physique',
  'Dégradation',
  'Autre'
]

// Computed
const filteredBehaviors = computed(() => {
  let filtered = behaviors.value
  
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(behavior => 
      behavior.student_name.toLowerCase().includes(term) ||
      behavior.description.toLowerCase().includes(term)
    )
  }
  
  return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

const behaviorStats = computed(() => ({
  total: behaviors.value.length,
  positive: behaviors.value.filter(b => b.type === 'positive').length,
  negative: behaviors.value.filter(b => b.type === 'negative').length,
  neutral: behaviors.value.filter(b => b.type === 'neutral').length
}))

// Méthodes
const loadBehaviors = async () => {
  loading.value = true
  try {
    // TODO: Implémenter l'API pour charger les comportements
    // Simulation pour la démo
    behaviors.value = [
      {
        id: '1',
        student_name: 'Marie Dubois',
        class_name: '6ème A',
        type: 'positive',
        category: 'Participation',
        subject: 'Mathématiques',
        description: 'Excellente participation en cours, aide ses camarades.',
        date: '2024-01-15',
        teacher_name: 'M. Dupont',
        severity: null
      },
      {
        id: '2',
        student_name: 'Pierre Martin',
        class_name: '6ème A',
        type: 'negative',
        category: 'Perturbation',
        subject: 'Français',
        description: 'Bavardages répétés malgré les rappels à l\'ordre.',
        date: '2024-01-14',
        teacher_name: 'Mme Leroy',
        severity: 2
      },
      {
        id: '3',
        student_name: 'Sophie Blanc',
        class_name: '6ème B',
        type: 'positive',
        category: 'Effort',
        subject: 'Histoire',
        description: 'Gros efforts fournis, progression remarquable.',
        date: '2024-01-13',
        teacher_name: 'M. Bernard',
        severity: null
      }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des comportements:', error)
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
      { id: '3', first_name: 'Sophie', last_name: 'Blanc', class_name: '6ème B' }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des élèves:', error)
  }
}

const loadSubjects = async () => {
  try {
    // TODO: Implémenter l'API pour charger les matières
    subjects.value = [
      { id: '1', name: 'Mathématiques' },
      { id: '2', name: 'Français' },
      { id: '3', name: 'Histoire' },
      { id: '4', name: 'Sciences' }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des matières:', error)
  }
}

const saveBehavior = async () => {
  saving.value = true
  try {
    // TODO: Implémenter l'API pour sauvegarder le comportement
    console.log('Sauvegarder le comportement:', behaviorForm)
    
    // Simulation
    const newBehavior = {
      id: Date.now().toString(),
      student_name: students.value.find(s => s.id === behaviorForm.student)?.first_name + ' ' + 
                    students.value.find(s => s.id === behaviorForm.student)?.last_name,
      class_name: students.value.find(s => s.id === behaviorForm.student)?.class_name,
      type: behaviorForm.type,
      category: behaviorForm.category,
      subject: behaviorForm.subject,
      description: behaviorForm.description,
      date: behaviorForm.date,
      teacher_name: authStore.user?.first_name + ' ' + authStore.user?.last_name,
      severity: behaviorForm.severity ? parseInt(behaviorForm.severity) : null
    }
    
    if (editingBehavior.value) {
      const index = behaviors.value.findIndex(b => b.id === editingBehavior.value.id)
      if (index !== -1) {
        behaviors.value[index] = { ...editingBehavior.value, ...newBehavior }
      }
    } else {
      behaviors.value.unshift(newBehavior)
    }
    
    closeAddBehaviorModal()
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error)
  } finally {
    saving.value = false
  }
}

const editBehavior = (behavior: any) => {
  editingBehavior.value = behavior
  Object.assign(behaviorForm, {
    student: behavior.student_id || '',
    type: behavior.type,
    category: behavior.category,
    subject: behavior.subject || '',
    date: behavior.date,
    severity: behavior.severity?.toString() || '',
    description: behavior.description
  })
  showAddBehaviorModal.value = true
}

const deleteBehavior = async (behaviorId: string) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer ce comportement ?')) {
    return
  }
  
  try {
    // TODO: Implémenter l'API pour supprimer le comportement
    console.log('Supprimer le comportement:', behaviorId)
    
    // Simulation
    const index = behaviors.value.findIndex(b => b.id === behaviorId)
    if (index !== -1) {
      behaviors.value.splice(index, 1)
    }
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
  }
}

const closeAddBehaviorModal = () => {
  showAddBehaviorModal.value = false
  editingBehavior.value = null
  Object.assign(behaviorForm, {
    student: '',
    type: '',
    category: '',
    subject: '',
    date: '',
    severity: '',
    description: ''
  })
}

const exportBehaviors = async () => {
  try {
    const csvContent = generateBehaviorsCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `comportements-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateBehaviorsCSV = () => {
  const headers = ['Élève', 'Classe', 'Type', 'Catégorie', 'Matière', 'Description', 'Date', 'Professeur', 'Gravité']
  const rows = [headers.join(',')]
  
  behaviors.value.forEach(behavior => {
    const row = [
      behavior.student_name,
      behavior.class_name,
      getBehaviorTypeLabel(behavior.type),
      behavior.category,
      behavior.subject || '',
      behavior.description.replace(/,/g, ';'),
      formatDateTime(behavior.date),
      behavior.teacher_name,
      behavior.severity || ''
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getBehaviorTypeColor = (type: string) => {
  const colors = {
    positive: 'success',
    negative: 'danger',
    neutral: 'secondary'
  }
  return colors[type as keyof typeof colors] || 'secondary'
}

const getBehaviorTypeLabel = (type: string) => {
  const labels = {
    positive: 'Positif',
    negative: 'Négatif',
    neutral: 'Neutre'
  }
  return labels[type as keyof typeof labels] || type
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
  
  // Définir la date par défaut du formulaire
  behaviorForm.date = new Date().toISOString().split('T')[0]
  
  await Promise.all([
    attendanceStore.fetchClasses(),
    loadBehaviors(),
    loadStudents(),
    loadSubjects()
  ])
})
</script>