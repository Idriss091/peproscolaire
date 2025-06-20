<template>
  <div class="space-y-6">
    <!-- Actions rapides -->
    <div class="flex justify-between items-center">
      <div class="flex gap-3">
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showGenerateBulletinModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Générer un bulletin
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          @click="exportBulletins"
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
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            Période
          </label>
          <select
            v-model="filters.period"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les périodes</option>
            <option value="T1">Trimestre 1</option>
            <option value="T2">Trimestre 2</option>
            <option value="T3">Trimestre 3</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Année scolaire
          </label>
          <select
            v-model="filters.year"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les années</option>
            <option value="2023-2024">2023-2024</option>
            <option value="2024-2025">2024-2025</option>
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
            <option value="draft">Brouillon</option>
            <option value="published">Publié</option>
            <option value="sent">Envoyé</option>
          </select>
        </div>
      </div>
    </BaseCard>

    <!-- Liste des bulletins -->
    <div class="space-y-4">
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des bulletins...</p>
      </div>
      
      <div v-else-if="filteredBulletins.length === 0" class="text-center py-8">
        <DocumentTextIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucun bulletin trouvé</p>
      </div>
      
      <div
        v-for="bulletin in filteredBulletins"
        :key="bulletin.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-3">
              <div class="flex-shrink-0 h-12 w-12">
                <div class="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-lg font-medium text-gray-700">
                    {{ getStudentInitials(bulletin.student_name) }}
                  </span>
                </div>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">{{ bulletin.student_name }}</h3>
                <p class="text-sm text-gray-600">{{ bulletin.class_name }} - {{ bulletin.period }}</p>
              </div>
              <BaseBadge :variant="getStatusColor(bulletin.status)">
                {{ getStatusLabel(bulletin.status) }}
              </BaseBadge>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Moyenne générale:</span>
                <div class="mt-1">
                  <span class="text-lg font-bold" :class="getAverageColorClass(bulletin.general_average)">
                    {{ bulletin.general_average }}/20
                  </span>
                </div>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Rang:</span>
                <p class="mt-1">{{ bulletin.rank }}/{{ bulletin.class_size }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Absences:</span>
                <p class="mt-1">{{ bulletin.absences_count }} demi-journées</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Retards:</span>
                <p class="mt-1">{{ bulletin.tardiness_count }}</p>
              </div>
            </div>
            
            <!-- Moyennes par matière -->
            <div class="mt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Moyennes par matière</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div v-for="subject in bulletin.subject_averages" :key="subject.subject_id" 
                     class="flex justify-between items-center text-xs p-2 bg-gray-50 rounded">
                  <span>{{ subject.subject_name }}:</span>
                  <span class="font-medium" :class="getAverageColorClass(subject.average)">
                    {{ subject.average }}/20
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Appréciation générale -->
            <div v-if="bulletin.general_comment" class="mt-4 p-3 bg-blue-50 rounded-lg">
              <h4 class="text-sm font-medium text-blue-900 mb-1">Appréciation générale</h4>
              <p class="text-sm text-blue-800">{{ bulletin.general_comment }}</p>
            </div>
          </div>
          
          <div class="flex flex-col items-end space-y-2 ml-4">
            <div class="text-xs text-gray-500">
              Généré le {{ formatDate(bulletin.created_at) }}
            </div>
            
            <div class="flex space-x-2">
              <BaseButton
                variant="outline"
                size="sm"
                @click="viewBulletin(bulletin)"
              >
                Voir
              </BaseButton>
              
              <BaseButton
                variant="primary"
                size="sm"
                @click="downloadBulletin(bulletin)"
              >
                PDF
              </BaseButton>
              
              <BaseButton
                v-if="bulletin.status === 'draft'"
                variant="success"
                size="sm"
                @click="publishBulletin(bulletin.id)"
              >
                Publier
              </BaseButton>
              
              <BaseButton
                v-if="bulletin.status === 'published'"
                variant="secondary"
                size="sm"
                @click="sendBulletin(bulletin.id)"
              >
                Envoyer
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de génération de bulletin -->
    <BaseModal
      :is-open="showGenerateBulletinModal"
      title="Générer des bulletins"
      @close="showGenerateBulletinModal = false"
      size="lg"
    >
      <GenerateBulletinForm
        @close="showGenerateBulletinModal = false"
        @saved="handleBulletinGenerated"
      />
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedBulletin"
      :is-open="!!selectedBulletin"
      :title="`Bulletin - ${selectedBulletin.student_name}`"
      @close="selectedBulletin = null"
      size="xl"
    >
      <BulletinDetailView
        :bulletin="selectedBulletin"
        @close="selectedBulletin = null"
        @download="downloadBulletin"
        @publish="publishBulletin"
        @send="sendBulletin"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  PlusIcon,
  DocumentArrowDownIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import GenerateBulletinForm from '@/components/grades/GenerateBulletinForm.vue'
import BulletinDetailView from '@/components/grades/BulletinDetailView.vue'

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const loading = ref(false)
const searchTerm = ref('')
const showGenerateBulletinModal = ref(false)
const selectedBulletin = ref<any>(null)

// Filtres
const filters = reactive({
  class: '',
  period: '',
  year: '',
  status: ''
})

// Données simulées
const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
])

const bulletins = ref([
  {
    id: '1',
    student_name: 'Marie Dubois',
    class_name: '6ème A',
    period: 'T1',
    year: '2024-2025',
    status: 'published',
    general_average: 15.2,
    rank: 3,
    class_size: 25,
    absences_count: 2,
    tardiness_count: 1,
    created_at: '2024-01-20',
    general_comment: 'Très bon trimestre, élève sérieuse et appliquée. Continuez ainsi !',
    subject_averages: [
      { subject_id: '1', subject_name: 'Mathématiques', average: 16.5 },
      { subject_id: '2', subject_name: 'Français', average: 14.8 },
      { subject_id: '3', subject_name: 'Histoire-Géo', average: 15.0 },
      { subject_id: '4', subject_name: 'Sciences', average: 14.2 }
    ]
  },
  {
    id: '2',
    student_name: 'Pierre Martin',
    class_name: '6ème A',
    period: 'T1',
    year: '2024-2025',
    status: 'draft',
    general_average: 11.8,
    rank: 18,
    class_size: 25,
    absences_count: 5,
    tardiness_count: 3,
    created_at: '2024-01-20',
    general_comment: 'Trimestre difficile. Des efforts sont nécessaires pour progresser.',
    subject_averages: [
      { subject_id: '1', subject_name: 'Mathématiques', average: 10.5 },
      { subject_id: '2', subject_name: 'Français', average: 12.2 },
      { subject_id: '3', subject_name: 'Histoire-Géo', average: 13.0 },
      { subject_id: '4', subject_name: 'Sciences', average: 11.5 }
    ]
  }
])

// Computed
const filteredBulletins = computed(() => {
  let filtered = bulletins.value

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(bulletin => 
      bulletin.student_name.toLowerCase().includes(term)
    )
  }

  if (filters.class) {
    filtered = filtered.filter(bulletin => bulletin.class_name.includes(filters.class))
  }

  if (filters.period) {
    filtered = filtered.filter(bulletin => bulletin.period === filters.period)
  }

  if (filters.year) {
    filtered = filtered.filter(bulletin => bulletin.year === filters.year)
  }

  if (filters.status) {
    filtered = filtered.filter(bulletin => bulletin.status === filters.status)
  }

  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// Méthodes
const loadBulletins = async () => {
  loading.value = true
  try {
    await gradesStore.fetchBulletins(filters)
  } catch (error) {
    console.error('Erreur lors du chargement des bulletins:', error)
  } finally {
    loading.value = false
  }
}

const viewBulletin = (bulletin: any) => {
  selectedBulletin.value = bulletin
}

const downloadBulletin = async (bulletin: any) => {
  try {
    // TODO: Implémenter la génération PDF
    console.log('Télécharger le bulletin PDF:', bulletin.id)
    
    // Simulation de téléchargement
    const link = document.createElement('a')
    link.href = '#' // URL du PDF
    link.download = `bulletin-${bulletin.student_name}-${bulletin.period}.pdf`
    link.click()
  } catch (error) {
    console.error('Erreur lors du téléchargement:', error)
  }
}

const publishBulletin = async (bulletinId: string) => {
  try {
    // TODO: Publier le bulletin
    console.log('Publier le bulletin:', bulletinId)
    
    const bulletin = bulletins.value.find(b => b.id === bulletinId)
    if (bulletin) {
      bulletin.status = 'published'
    }
  } catch (error) {
    console.error('Erreur lors de la publication:', error)
  }
}

const sendBulletin = async (bulletinId: string) => {
  try {
    // TODO: Envoyer le bulletin aux parents
    console.log('Envoyer le bulletin:', bulletinId)
    
    const bulletin = bulletins.value.find(b => b.id === bulletinId)
    if (bulletin) {
      bulletin.status = 'sent'
    }
  } catch (error) {
    console.error('Erreur lors de l\'envoi:', error)
  }
}

const handleBulletinGenerated = () => {
  showGenerateBulletinModal.value = false
  loadBulletins()
}

const exportBulletins = async () => {
  try {
    const csvContent = generateBulletinsCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `bulletins-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateBulletinsCSV = () => {
  const headers = ['Élève', 'Classe', 'Période', 'Moyenne générale', 'Rang', 'Absences', 'Retards', 'Statut']
  const rows = [headers.join(',')]
  
  filteredBulletins.value.forEach(bulletin => {
    const row = [
      bulletin.student_name,
      bulletin.class_name,
      bulletin.period,
      bulletin.general_average,
      `${bulletin.rank}/${bulletin.class_size}`,
      bulletin.absences_count,
      bulletin.tardiness_count,
      getStatusLabel(bulletin.status)
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getStudentInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const getStatusColor = (status: string) => {
  const colors = {
    draft: 'secondary',
    published: 'success',
    sent: 'primary'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: 'Brouillon',
    published: 'Publié',
    sent: 'Envoyé'
  }
  return labels[status as keyof typeof labels] || status
}

const getAverageColorClass = (average: number) => {
  if (average >= 16) return 'text-green-600'
  if (average >= 14) return 'text-blue-600'
  if (average >= 12) return 'text-yellow-600'
  if (average >= 10) return 'text-orange-600'
  return 'text-red-600'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  loadBulletins()
})
</script>