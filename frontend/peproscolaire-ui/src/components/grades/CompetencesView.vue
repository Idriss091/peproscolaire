<template>
  <div class="space-y-6">
    <!-- Actions rapides -->
    <div class="flex justify-between items-center">
      <div class="flex gap-3">
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showAddCompetenceModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Nouvelle compétence
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          @click="exportCompetences"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter
        </BaseButton>
      </div>
      
      <div class="flex items-center gap-2">
        <BaseInput
          v-model="searchTerm"
          placeholder="Rechercher une compétence..."
          size="sm"
          class="w-64"
        />
      </div>
    </div>

    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Matière
          </label>
          <select
            v-model="filters.subject"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les matières</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Niveau
          </label>
          <select
            v-model="filters.level"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les niveaux</option>
            <option value="6eme">6ème</option>
            <option value="5eme">5ème</option>
            <option value="4eme">4ème</option>
            <option value="3eme">3ème</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Domaine
          </label>
          <select
            v-model="filters.domain"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les domaines</option>
            <option value="nombres">Nombres et calculs</option>
            <option value="geometrie">Géométrie</option>
            <option value="mesures">Grandeurs et mesures</option>
            <option value="donnees">Organisation et gestion de données</option>
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
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>
    </BaseCard>

    <!-- Liste des compétences par domaine -->
    <div class="space-y-6">
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des compétences...</p>
      </div>
      
      <div v-else-if="groupedCompetences.length === 0" class="text-center py-8">
        <AcademicCapIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune compétence trouvée</p>
      </div>
      
      <div v-for="group in groupedCompetences" :key="group.domain" class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">{{ group.domainLabel }}</h3>
          <BaseBadge variant="secondary">{{ group.competences.length }} compétences</BaseBadge>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div
            v-for="competence in group.competences"
            :key="competence.id"
            class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow cursor-pointer"
            @click="viewCompetence(competence)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <h4 class="text-sm font-medium text-gray-900">{{ competence.code }}</h4>
                  <BaseBadge :variant="getStatusColor(competence.status)">
                    {{ getStatusLabel(competence.status) }}
                  </BaseBadge>
                  <BaseBadge variant="secondary" size="sm">
                    {{ competence.level }}
                  </BaseBadge>
                </div>
                
                <p class="text-sm text-gray-600 mb-3">{{ competence.description }}</p>
                
                <div class="flex items-center space-x-4 text-xs text-gray-500">
                  <span>{{ competence.subject_name }}</span>
                  <span>•</span>
                  <span>{{ competence.evaluations_count || 0 }} évaluations</span>
                  <span>•</span>
                  <span>{{ competence.students_count || 0 }} élèves évalués</span>
                </div>
                
                <!-- Barre de progression moyenne -->
                <div class="mt-3">
                  <div class="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Maîtrise moyenne</span>
                    <span>{{ competence.average_mastery || 0 }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getMasteryColorClass(competence.average_mastery || 0)"
                      :style="{ width: `${competence.average_mastery || 0}%` }"
                    />
                  </div>
                </div>
              </div>
              
              <div class="flex flex-col items-end space-y-2 ml-4">
                <BaseButton
                  variant="outline"
                  size="sm"
                  @click.stop="editCompetence(competence)"
                >
                  Modifier
                </BaseButton>
                
                <BaseButton
                  variant="primary"
                  size="sm"
                  @click.stop="evaluateCompetence(competence)"
                >
                  Évaluer
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal d'ajout de compétence -->
    <BaseModal
      :is-open="showAddCompetenceModal"
      title="Nouvelle compétence"
      @close="showAddCompetenceModal = false"
      size="lg"
    >
      <AddCompetenceForm
        @close="showAddCompetenceModal = false"
        @saved="handleCompetenceSaved"
      />
    </BaseModal>

    <!-- Modal de modification -->
    <BaseModal
      v-if="editingCompetence"
      :is-open="!!editingCompetence"
      title="Modifier la compétence"
      @close="editingCompetence = null"
      size="lg"
    >
      <EditCompetenceForm
        :competence="editingCompetence"
        @close="editingCompetence = null"
        @saved="handleCompetenceUpdated"
      />
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedCompetence"
      :is-open="!!selectedCompetence"
      :title="selectedCompetence.code"
      @close="selectedCompetence = null"
      size="xl"
    >
      <CompetenceDetailView
        :competence="selectedCompetence"
        @close="selectedCompetence = null"
        @edit="editCompetence"
        @evaluate="evaluateCompetence"
      />
    </BaseModal>

    <!-- Modal d'évaluation -->
    <BaseModal
      v-if="evaluatingCompetence"
      :is-open="!!evaluatingCompetence"
      title="Évaluer la compétence"
      @close="evaluatingCompetence = null"
      size="lg"
    >
      <EvaluateCompetenceForm
        :competence="evaluatingCompetence"
        @close="evaluatingCompetence = null"
        @saved="handleCompetenceEvaluated"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  PlusIcon,
  DocumentArrowDownIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AddCompetenceForm from '@/components/grades/AddCompetenceForm.vue'
import EditCompetenceForm from '@/components/grades/EditCompetenceForm.vue'
import CompetenceDetailView from '@/components/grades/CompetenceDetailView.vue'
import EvaluateCompetenceForm from '@/components/grades/EvaluateCompetenceForm.vue'

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const loading = ref(false)
const searchTerm = ref('')
const showAddCompetenceModal = ref(false)
const selectedCompetence = ref<any>(null)
const editingCompetence = ref<any>(null)
const evaluatingCompetence = ref<any>(null)

// Filtres
const filters = reactive({
  subject: '',
  level: '',
  domain: '',
  status: ''
})

// Données simulées
const subjects = ref([
  { id: '1', name: 'Mathématiques' },
  { id: '2', name: 'Français' },
  { id: '3', name: 'Sciences' }
])

const competences = ref([
  {
    id: '1',
    code: 'N1.1',
    description: 'Utiliser et représenter les grands nombres entiers, des fractions simples, les nombres décimaux',
    subject_id: '1',
    subject_name: 'Mathématiques',
    level: '6ème',
    domain: 'nombres',
    status: 'active',
    evaluations_count: 3,
    students_count: 25,
    average_mastery: 75
  },
  {
    id: '2',
    code: 'G1.1',
    description: 'Reconnaître, nommer, décrire, reproduire, représenter, construire des figures géométriques',
    subject_id: '1',
    subject_name: 'Mathématiques',
    level: '6ème',
    domain: 'geometrie',
    status: 'active',
    evaluations_count: 2,
    students_count: 25,
    average_mastery: 68
  },
  {
    id: '3',
    code: 'M1.1',
    description: 'Comparer, estimer, mesurer des grandeurs géométriques avec des nombres entiers et des nombres décimaux',
    subject_id: '1',
    subject_name: 'Mathématiques',
    level: '6ème',
    domain: 'mesures',
    status: 'active',
    evaluations_count: 1,
    students_count: 25,
    average_mastery: 82
  }
])

const domains = {
  nombres: 'Nombres et calculs',
  geometrie: 'Géométrie',
  mesures: 'Grandeurs et mesures',
  donnees: 'Organisation et gestion de données'
}

// Computed
const filteredCompetences = computed(() => {
  let filtered = competences.value

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(competence => 
      competence.code.toLowerCase().includes(term) ||
      competence.description.toLowerCase().includes(term)
    )
  }

  if (filters.subject) {
    filtered = filtered.filter(competence => competence.subject_id === filters.subject)
  }

  if (filters.level) {
    filtered = filtered.filter(competence => competence.level === filters.level)
  }

  if (filters.domain) {
    filtered = filtered.filter(competence => competence.domain === filters.domain)
  }

  if (filters.status) {
    filtered = filtered.filter(competence => competence.status === filters.status)
  }

  return filtered
})

const groupedCompetences = computed(() => {
  const groups: any = {}
  
  filteredCompetences.value.forEach(competence => {
    if (!groups[competence.domain]) {
      groups[competence.domain] = {
        domain: competence.domain,
        domainLabel: domains[competence.domain as keyof typeof domains] || competence.domain,
        competences: []
      }
    }
    groups[competence.domain].competences.push(competence)
  })
  
  return Object.values(groups).sort((a: any, b: any) => a.domainLabel.localeCompare(b.domainLabel))
})

// Méthodes
const loadCompetences = async () => {
  loading.value = true
  try {
    // TODO: Charger depuis l'API
    await new Promise(resolve => setTimeout(resolve, 500))
  } catch (error) {
    console.error('Erreur lors du chargement des compétences:', error)
  } finally {
    loading.value = false
  }
}

const viewCompetence = (competence: any) => {
  selectedCompetence.value = competence
}

const editCompetence = (competence: any) => {
  editingCompetence.value = competence
}

const evaluateCompetence = (competence: any) => {
  evaluatingCompetence.value = competence
}

const handleCompetenceSaved = () => {
  showAddCompetenceModal.value = false
  loadCompetences()
}

const handleCompetenceUpdated = () => {
  editingCompetence.value = null
  loadCompetences()
}

const handleCompetenceEvaluated = () => {
  evaluatingCompetence.value = null
  loadCompetences()
}

const exportCompetences = async () => {
  try {
    const csvContent = generateCompetencesCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `competences-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateCompetencesCSV = () => {
  const headers = ['Code', 'Description', 'Matière', 'Niveau', 'Domaine', 'Statut', 'Évaluations', 'Maîtrise moyenne']
  const rows = [headers.join(',')]
  
  filteredCompetences.value.forEach(competence => {
    const row = [
      competence.code,
      competence.description.replace(/,/g, ';'),
      competence.subject_name,
      competence.level,
      domains[competence.domain as keyof typeof domains],
      getStatusLabel(competence.status),
      competence.evaluations_count,
      `${competence.average_mastery}%`
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getStatusColor = (status: string) => {
  const colors = {
    active: 'success',
    inactive: 'secondary'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: 'Active',
    inactive: 'Inactive'
  }
  return labels[status as keyof typeof labels] || status
}

const getMasteryColorClass = (mastery: number) => {
  if (mastery >= 80) return 'bg-green-500'
  if (mastery >= 60) return 'bg-blue-500'
  if (mastery >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Lifecycle
onMounted(() => {
  loadCompetences()
})
</script>