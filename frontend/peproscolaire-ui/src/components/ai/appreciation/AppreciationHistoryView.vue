<template>
  <div class="space-y-6">
    <!-- Filtres -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Rechercher
          </label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Nom de l'élève..."
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Statut
          </label>
          <select
            v-model="selectedStatus"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
          >
            <option value="">Tous les statuts</option>
            <option value="draft">Brouillon</option>
            <option value="validated">Validé</option>
            <option value="rejected">Rejeté</option>
            <option value="published">Publié</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            v-model="selectedType"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
          >
            <option value="">Tous les types</option>
            <option value="bulletin">Bulletin</option>
            <option value="subject">Matière</option>
            <option value="progress">Progrès</option>
            <option value="orientation">Orientation</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Période
          </label>
          <select
            v-model="selectedPeriod"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
          >
            <option value="">Toutes les périodes</option>
            <option value="today">Aujourd'hui</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
            <option value="quarter">Ce trimestre</option>
          </select>
        </div>
        
        <div class="flex items-end">
          <BaseButton
            variant="outline"
            @click="exportHistory"
            class="w-full"
          >
            <DocumentArrowDownIcon class="w-4 h-4" />
            Exporter
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Actions groupées -->
    <div v-if="selectedAppreciations.length > 0" 
         class="flex items-center justify-between bg-purple-50 p-4 rounded-lg border border-purple-200">
      <div class="flex items-center space-x-3">
        <span class="text-sm font-medium text-purple-900">
          {{ selectedAppreciations.length }} appréciation(s) sélectionnée(s)
        </span>
      </div>
      <div class="flex space-x-2">
        <BaseButton
          variant="primary"
          size="sm"
          @click="bulkValidate"
        >
          Valider en masse
        </BaseButton>
        <BaseButton
          variant="outline"
          size="sm"
          @click="bulkExport"
        >
          Exporter la sélection
        </BaseButton>
        <BaseButton
          variant="secondary"
          size="sm"
          @click="selectedAppreciations = []"
        >
          Désélectionner
        </BaseButton>
      </div>
    </div>

    <!-- Liste des appréciations -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Appréciations générées ({{ filteredAppreciations.length }})
          </h3>
          <div class="flex items-center space-x-2">
            <select
              v-model="sortBy"
              class="text-sm border-gray-300 rounded"
            >
              <option value="created_at">Date de création</option>
              <option value="student_name">Nom de l'élève</option>
              <option value="status">Statut</option>
              <option value="type">Type</option>
            </select>
            <BaseButton
              variant="outline"
              size="sm"
              @click="refreshHistory"
              :loading="loading"
            >
              <ArrowPathIcon class="w-4 h-4" />
            </BaseButton>
          </div>
        </div>
      </template>
      
      <div v-if="loading" class="p-8 text-center">
        <div class="inline-flex items-center space-x-2 text-gray-600">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
          <span>Chargement de l'historique...</span>
        </div>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="appreciation in filteredAppreciations"
          :key="appreciation.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3 flex-1">
              <input
                v-model="selectedAppreciations"
                :value="appreciation.id"
                type="checkbox"
                class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded mt-1"
              >
              
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h4 class="text-lg font-medium text-gray-900">{{ appreciation.student_name }}</h4>
                  <BaseBadge :variant="getStatusColor(appreciation.status)" size="sm">
                    {{ getStatusLabel(appreciation.status) }}
                  </BaseBadge>
                  <BaseBadge variant="secondary" size="sm">
                    {{ getTypeLabel(appreciation.type) }}
                  </BaseBadge>
                </div>
                
                <div class="flex items-center space-x-4 mb-3 text-sm text-gray-500">
                  <span>{{ appreciation.class_name }}</span>
                  <span>{{ appreciation.subject_name || 'Général' }}</span>
                  <span>{{ appreciation.period }}</span>
                  <span>{{ formatDateTime(appreciation.created_at) }}</span>
                </div>
                
                <div class="bg-gray-50 rounded-lg p-3 mb-3">
                  <p class="text-sm text-gray-700 leading-relaxed">{{ appreciation.content }}</p>
                </div>
                
                <div class="flex items-center justify-between text-xs text-gray-500">
                  <div class="flex items-center space-x-4">
                    <span>{{ appreciation.word_count }} mots</span>
                    <span>Ton {{ appreciation.tone }}</span>
                    <span v-if="appreciation.ai_confidence">Confiance IA: {{ appreciation.ai_confidence }}%</span>
                  </div>
                  
                  <div v-if="appreciation.validated_by" class="flex items-center space-x-1">
                    <CheckCircleIcon class="w-3 h-3 text-green-500" />
                    <span>Validé par {{ appreciation.validated_by }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="flex flex-col space-y-2 ml-4">
              <BaseButton
                variant="outline"
                size="sm"
                @click="editAppreciation(appreciation.id)"
              >
                <PencilIcon class="w-3 h-3" />
                Éditer
              </BaseButton>
              
              <BaseButton
                v-if="appreciation.status === 'draft'"
                variant="success"
                size="sm"
                @click="validateAppreciation(appreciation.id)"
              >
                <CheckIcon class="w-3 h-3" />
                Valider
              </BaseButton>
              
              <BaseButton
                v-if="appreciation.status === 'validated'"
                variant="primary"
                size="sm"
                @click="publishAppreciation(appreciation.id)"
              >
                <ShareIcon class="w-3 h-3" />
                Publier
              </BaseButton>
              
              <BaseButton
                variant="outline"
                size="sm"
                @click="copyAppreciation(appreciation.id)"
              >
                <DocumentDuplicateIcon class="w-3 h-3" />
                Copier
              </BaseButton>
              
              <BaseButton
                variant="outline"
                size="sm"
                @click="deleteAppreciation(appreciation.id)"
                class="text-red-600 hover:text-red-700"
              >
                <TrashIcon class="w-3 h-3" />
              </BaseButton>
            </div>
          </div>
        </div>
        
        <div v-if="filteredAppreciations.length === 0" class="text-center py-8 text-gray-500">
          <DocumentTextIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Aucune appréciation ne correspond aux critères</p>
        </div>
      </div>
    </BaseCard>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between">
      <div class="text-sm text-gray-700">
        Affichage de {{ (currentPage - 1) * pageSize + 1 }} à 
        {{ Math.min(currentPage * pageSize, totalAppreciations) }} sur {{ totalAppreciations }} appréciations
      </div>
      <div class="flex space-x-1">
        <BaseButton
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          Précédent
        </BaseButton>
        <BaseButton
          v-for="page in visiblePages"
          :key="page"
          :variant="page === currentPage ? 'primary' : 'outline'"
          size="sm"
          @click="currentPage = page"
        >
          {{ page }}
        </BaseButton>
        <BaseButton
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Suivant
        </BaseButton>
      </div>
    </div>

    <!-- Modal d'édition -->
    <BaseModal
      :is-open="showEditModal"
      title="Éditer l'appréciation"
      @close="showEditModal = false"
      size="lg"
    >
      <EditAppreciationForm
        v-if="selectedAppreciationId"
        :appreciation-id="selectedAppreciationId"
        @close="showEditModal = false"
        @saved="handleAppreciationUpdated"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  DocumentArrowDownIcon,
  ArrowPathIcon,
  PencilIcon,
  CheckIcon,
  ShareIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  DocumentTextIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import EditAppreciationForm from '@/components/ai/appreciation/EditAppreciationForm.vue'

// État local
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedType = ref('')
const selectedPeriod = ref('')
const selectedAppreciations = ref<string[]>([])
const sortBy = ref('created_at')
const currentPage = ref(1)
const pageSize = ref(10)
const showEditModal = ref(false)
const selectedAppreciationId = ref<string | null>(null)

// Données simulées
const appreciations = ref([
  {
    id: '1',
    student_name: 'Marie Dubois',
    class_name: '6ème A',
    subject_name: null,
    type: 'bulletin',
    period: 'T1',
    status: 'validated',
    content: 'Marie fait preuve d\'un excellent engagement dans son travail. Ses résultats sont très satisfaisants et témoignent d\'une bonne compréhension des notions abordées. Elle participe activement en classe et fait preuve d\'une belle autonomie dans ses apprentissages.',
    word_count: 45,
    tone: 'encouraging',
    ai_confidence: 92,
    created_at: '2024-01-15T10:30:00',
    validated_by: 'M. Dupont'
  },
  {
    id: '2',
    student_name: 'Pierre Martin',
    class_name: '6ème A',
    subject_name: 'Mathématiques',
    type: 'subject',
    period: 'T1',
    status: 'draft',
    content: 'Pierre montre des efforts constants en mathématiques. Il gagnerait à être plus régulier dans ses devoirs et à approfondir certaines notions. Avec de la persévérance, il peut améliorer ses résultats.',
    word_count: 32,
    tone: 'constructive',
    ai_confidence: 87,
    created_at: '2024-01-15T09:15:00',
    validated_by: null
  },
  {
    id: '3',
    student_name: 'Sophie Blanc',
    class_name: '6ème B',
    subject_name: null,
    type: 'progress',
    period: 'T1',
    status: 'published',
    content: 'Sophie a montré de nets progrès ce trimestre. Son travail devient plus organisé et ses résultats s\'améliorent progressivement. Il faut continuer dans cette voie positive.',
    word_count: 28,
    tone: 'motivational',
    ai_confidence: 89,
    created_at: '2024-01-14T16:20:00',
    validated_by: 'Mme Martin'
  }
])

// Computed
const filteredAppreciations = computed(() => {
  let filtered = [...appreciations.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(app =>
      app.student_name.toLowerCase().includes(query) ||
      app.content.toLowerCase().includes(query)
    )
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(app => app.status === selectedStatus.value)
  }

  if (selectedType.value) {
    filtered = filtered.filter(app => app.type === selectedType.value)
  }

  // Tri
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_at':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'student_name':
        return a.student_name.localeCompare(b.student_name)
      case 'status':
        return a.status.localeCompare(b.status)
      case 'type':
        return a.type.localeCompare(b.type)
      default:
        return 0
    }
  })

  return filtered
})

const totalAppreciations = computed(() => filteredAppreciations.value.length)
const totalPages = computed(() => Math.ceil(totalAppreciations.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Méthodes
const refreshHistory = async () => {
  loading.value = true
  try {
    // TODO: Charger l'historique depuis l'API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
  } finally {
    loading.value = false
  }
}

const editAppreciation = (appreciationId: string) => {
  selectedAppreciationId.value = appreciationId
  showEditModal.value = true
}

const validateAppreciation = (appreciationId: string) => {
  const appreciation = appreciations.value.find(a => a.id === appreciationId)
  if (appreciation) {
    appreciation.status = 'validated'
    appreciation.validated_by = 'Utilisateur actuel'
  }
}

const publishAppreciation = (appreciationId: string) => {
  const appreciation = appreciations.value.find(a => a.id === appreciationId)
  if (appreciation) {
    appreciation.status = 'published'
  }
}

const copyAppreciation = (appreciationId: string) => {
  const appreciation = appreciations.value.find(a => a.id === appreciationId)
  if (appreciation) {
    navigator.clipboard.writeText(appreciation.content)
  }
}

const deleteAppreciation = (appreciationId: string) => {
  const index = appreciations.value.findIndex(a => a.id === appreciationId)
  if (index > -1) {
    appreciations.value.splice(index, 1)
  }
}

const bulkValidate = () => {
  selectedAppreciations.value.forEach(id => {
    validateAppreciation(id)
  })
  selectedAppreciations.value = []
}

const bulkExport = () => {
  // TODO: Exporter les appréciations sélectionnées
  console.log('Export des appréciations:', selectedAppreciations.value)
}

const exportHistory = () => {
  // TODO: Exporter tout l'historique
  console.log('Export de l\'historique')
}

const handleAppreciationUpdated = () => {
  showEditModal.value = false
  refreshHistory()
}

// Utilitaires
const getStatusColor = (status: string) => {
  const colors = {
    draft: 'warning',
    validated: 'success',
    rejected: 'danger',
    published: 'primary'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: 'Brouillon',
    validated: 'Validé',
    rejected: 'Rejeté',
    published: 'Publié'
  }
  return labels[status as keyof typeof labels] || status
}

const getTypeLabel = (type: string) => {
  const labels = {
    bulletin: 'Bulletin',
    subject: 'Matière',
    progress: 'Progrès',
    orientation: 'Orientation'
  }
  return labels[type as keyof typeof labels] || type
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  refreshHistory()
})
</script>