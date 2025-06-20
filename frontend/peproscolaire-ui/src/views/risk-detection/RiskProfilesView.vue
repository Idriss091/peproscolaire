<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900">
            Profils de risque
          </h1>
          <p class="text-gray-600">
            Gestion et suivi des élèves à risque de décrochage scolaire
          </p>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <BaseButton
            variant="primary"
            @click="showAnalysisModal = true"
          >
            <PlayIcon class="h-4 w-4 mr-2" />
            Lancer une analyse
          </BaseButton>
        </div>
      </div>

      <!-- Filters and search -->
      <BaseCard padding="md">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <!-- Search -->
          <BaseInput
            v-model="filters.search"
            placeholder="Rechercher un élève..."
            @input="debouncedSearch"
          >
            <template #prefix>
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </template>
          </BaseInput>

          <!-- Risk level filter -->
          <select
            v-model="filters.risk_level"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Tous les niveaux</option>
            <option value="critical">Critique</option>
            <option value="high">Élevé</option>
            <option value="moderate">Modéré</option>
            <option value="low">Faible</option>
            <option value="very_low">Très faible</option>
          </select>

          <!-- Monitoring filter -->
          <select
            v-model="filters.is_monitored"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Tous les statuts</option>
            <option value="true">Sous surveillance</option>
            <option value="false">Non surveillé</option>
          </select>

          <!-- Academic year filter -->
          <select
            v-model="filters.academic_year"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Toutes les années</option>
            <!-- Academic years will be loaded dynamically -->
          </select>
        </div>
      </BaseCard>

      <!-- Quick stats -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <BaseCard
          v-for="stat in quickStats"
          :key="stat.name"
          padding="md"
          class="hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <component
                :is="stat.icon"
                :class="[stat.iconColor, 'h-8 w-8']"
              />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  {{ stat.name }}
                </dt>
                <dd class="text-2xl font-semibold text-gray-900">
                  {{ stat.value }}
                </dd>
              </dl>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Risk profiles table -->
      <BaseCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              Profils de risque ({{ pagination.count }})
            </h3>
            
            <div class="flex items-center space-x-2">
              <BaseButton
                variant="ghost"
                size="sm"
                @click="refreshData"
                :loading="riskStore.isLoading.riskProfiles"
              >
                <ArrowPathIcon class="h-4 w-4" />
              </BaseButton>
            </div>
          </div>
        </template>

        <BaseTable
          :columns="tableColumns"
          :data="riskProfiles"
          :loading="riskStore.isLoading.riskProfiles"
          :sort-by="sortBy"
          :sort-order="sortOrder"
          :pagination="true"
          :current-page="currentPage"
          :total-items="pagination.count"
          :items-per-page="pageSize"
          @sort-change="handleSort"
          @row-click="handleRowClick"
          @page-change="handlePageChange"
          @size-change="handlePageSizeChange"
          empty-message="Aucun profil de risque trouvé"
        >
          <!-- Student column -->
          <template #cell-student="{ item }">
            <div class="flex items-center">
              <div class="flex-shrink-0 h-10 w-10">
                <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getStudentInitials(item.student) }}
                  </span>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-900">
                  {{ item.student.first_name }} {{ item.student.last_name }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ item.student.email }}
                </div>
              </div>
            </div>
          </template>

          <!-- Risk score column -->
          <template #cell-risk_score="{ item }">
            <div class="flex items-center">
              <div class="text-sm font-medium text-gray-900">
                {{ Math.round(item.risk_score) }}/100
              </div>
              <div class="ml-2 w-16 bg-gray-200 rounded-full h-2">
                <div
                  :class="[
                    'h-2 rounded-full transition-all duration-300',
                    getRiskScoreColor(item.risk_score)
                  ]"
                  :style="{ width: `${item.risk_score}%` }"
                />
              </div>
            </div>
          </template>

          <!-- Risk level column -->
          <template #cell-risk_level="{ item }">
            <BaseBadge :variant="getRiskLevelVariant(item.risk_level)">
              {{ getRiskLevelLabel(item.risk_level) }}
            </BaseBadge>
          </template>

          <!-- Last analysis column -->
          <template #cell-last_analysis="{ item }">
            <span class="text-sm text-gray-500">
              {{ formatDate(item.last_analysis) }}
            </span>
          </template>

          <!-- Monitoring status column -->
          <template #cell-is_monitored="{ item }">
            <BaseBadge
              :variant="item.is_monitored ? 'success' : 'secondary'"
              size="sm"
            >
              {{ item.is_monitored ? 'Surveillé' : 'Non surveillé' }}
            </BaseBadge>
          </template>

          <!-- Actions column -->
          <template #actions="{ item }">
            <div class="flex items-center space-x-3">
              <router-link
                :to="`/risk-detection/profiles/${item.id}`"
                class="text-primary-600 hover:text-primary-900 text-sm font-medium"
              >
                Voir
              </router-link>
              
              <button
                v-if="!item.is_monitored"
                @click.stop="startMonitoring(item)"
                class="text-green-600 hover:text-green-900 text-sm font-medium"
              >
                Surveiller
              </button>
              
              <button
                @click.stop="analyzeProfile(item)"
                class="text-blue-600 hover:text-blue-900 text-sm font-medium"
                :disabled="riskStore.isLoading.analyzeProfile"
              >
                Analyser
              </button>
            </div>
          </template>
        </BaseTable>
      </BaseCard>
    </div>

    <!-- Analysis Modal -->
    <BaseModal
      v-model="showAnalysisModal"
      title="Lancer une analyse de risque"
      size="md"
    >
      <AnalysisModal
        @close="showAnalysisModal = false"
        @analysis-started="handleAnalysisStarted"
      />
    </BaseModal>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseTable from '@/components/ui/BaseTable.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import AnalysisModal from '@/components/risk-detection/AnalysisModal.vue'
import {
  MagnifyingGlassIcon,
  PlayIcon,
  ArrowPathIcon,
  AcademicCapIcon,
  ShieldExclamationIcon,
  EyeIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import { toast } from 'vue-sonner'
import { debounce } from 'lodash-es'

const router = useRouter()
const riskStore = useRiskDetectionStore()
const authStore = useAuthStore()

// State
const showAnalysisModal = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('risk_score')
const sortOrder = ref<'asc' | 'desc'>('desc')

const filters = ref({
  search: '',
  risk_level: '',
  is_monitored: '',
  academic_year: ''
})

// Computed
const riskProfiles = computed(() => riskStore.riskProfiles)

const pagination = computed(() => riskStore.pagination.riskProfiles)

const quickStats = computed(() => [
  {
    name: 'Total des profils',
    value: pagination.value.count,
    icon: AcademicCapIcon,
    iconColor: 'text-blue-600'
  },
  {
    name: 'Risque élevé/critique',
    value: riskProfiles.value.filter(p => ['high', 'critical'].includes(p.risk_level)).length,
    icon: ShieldExclamationIcon,
    iconColor: 'text-red-600'
  },
  {
    name: 'Sous surveillance',
    value: riskProfiles.value.filter(p => p.is_monitored).length,
    icon: EyeIcon,
    iconColor: 'text-green-600'
  },
  {
    name: 'Score moyen',
    value: Math.round(riskProfiles.value.reduce((acc, p) => acc + p.risk_score, 0) / riskProfiles.value.length) || 0,
    icon: ChartBarIcon,
    iconColor: 'text-purple-600'
  }
])

const tableColumns = computed(() => [
  {
    key: 'student',
    label: 'Élève',
    sortable: false
  },
  {
    key: 'risk_score',
    label: 'Score de risque',
    sortable: true,
    sortType: 'number'
  },
  {
    key: 'risk_level',
    label: 'Niveau',
    sortable: true
  },
  {
    key: 'last_analysis',
    label: 'Dernière analyse',
    sortable: true,
    sortType: 'date'
  },
  {
    key: 'is_monitored',
    label: 'Surveillance',
    sortable: true
  }
])

// Methods
const formatDate = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const getStudentInitials = (student: any) => {
  const firstName = student.first_name?.[0] || ''
  const lastName = student.last_name?.[0] || ''
  return (firstName + lastName).toUpperCase()
}

const getRiskLevelVariant = (level: string) => {
  switch (level) {
    case 'critical':
      return 'danger'
    case 'high':
      return 'warning'
    case 'moderate':
      return 'info'
    case 'low':
      return 'success'
    default:
      return 'secondary'
  }
}

const getRiskLevelLabel = (level: string) => {
  const labels = {
    very_low: 'Très faible',
    low: 'Faible',
    moderate: 'Modéré',
    high: 'Élevé',
    critical: 'Critique'
  }
  return labels[level] || level
}

const getRiskScoreColor = (score: number) => {
  if (score >= 80) return 'bg-red-500'
  if (score >= 60) return 'bg-orange-500'
  if (score >= 40) return 'bg-yellow-500'
  if (score >= 20) return 'bg-blue-500'
  return 'bg-green-500'
}

const debouncedSearch = debounce(() => {
  currentPage.value = 1
  fetchData()
}, 300)

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
}

const handleSort = (sortData: { key: string; order: 'asc' | 'desc' }) => {
  sortBy.value = sortData.key
  sortOrder.value = sortData.order
  fetchData()
}

const handleRowClick = (item: any) => {
  router.push(`/risk-detection/profiles/${item.id}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchData()
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

const startMonitoring = async (profile: any) => {
  const success = await riskStore.startMonitoring(profile.id)
  if (success) {
    toast.success('Surveillance démarrée')
  } else {
    toast.error('Erreur lors du démarrage de la surveillance')
  }
}

const analyzeProfile = async (profile: any) => {
  const success = await riskStore.analyzeRiskProfile(profile.id)
  if (success) {
    toast.success('Analyse lancée')
  } else {
    toast.error('Erreur lors du lancement de l\'analyse')
  }
}

const refreshData = () => {
  fetchData()
}

const handleAnalysisStarted = () => {
  showAnalysisModal.value = false
  toast.success('Analyse lancée')
  // Refresh data after a short delay
  setTimeout(() => {
    fetchData()
  }, 2000)
}

const fetchData = async () => {
  const filterParams = {
    page: currentPage.value,
    page_size: pageSize.value,
    ordering: sortOrder.value === 'desc' ? `-${sortBy.value}` : sortBy.value,
    ...Object.fromEntries(
      Object.entries(filters.value).filter(([_, value]) => value !== '')
    )
  }

  await riskStore.fetchRiskProfiles(filterParams)
}

// Lifecycle
onMounted(() => {
  fetchData()
})

// Watch for auth changes
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    fetchData()
  }
})
</script>