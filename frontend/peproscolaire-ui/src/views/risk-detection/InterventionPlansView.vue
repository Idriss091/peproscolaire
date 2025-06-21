<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900">
            Plans d'intervention
          </h1>
          <p class="text-gray-600">
            Gestion des plans d'intervention personnalisés
          </p>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <BaseButton
            variant="secondary"
            @click="showAnalysisModal = true"
          >
            <ChartBarIcon class="h-4 w-4 mr-2" />
            Analyser
          </BaseButton>
          
          <BaseButton
            variant="primary"
            @click="showCreateModal = true"
          >
            <PlusIcon class="h-4 w-4 mr-2" />
            Nouveau plan
          </BaseButton>
        </div>
      </div>

      <!-- Filters -->
      <BaseCard padding="md">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <!-- Search -->
          <BaseInput
            v-model="filters.search"
            placeholder="Rechercher un plan..."
            @input="debouncedSearch"
          >
            <template #prefix>
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </template>
          </BaseInput>

          <!-- Status filter -->
          <select
            v-model="filters.status"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Tous les statuts</option>
            <option value="draft">Brouillon</option>
            <option value="active">Actif</option>
            <option value="completed">Terminé</option>
            <option value="on_hold">En pause</option>
          </select>

          <!-- Priority filter -->
          <select
            v-model="filters.priority"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Toutes les priorités</option>
            <option value="urgent">Urgente</option>
            <option value="high">Haute</option>
            <option value="normal">Normale</option>
            <option value="low">Faible</option>
          </select>

          <!-- Date filter -->
          <select
            v-model="filters.date_range"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Toutes les dates</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
            <option value="quarter">Ce trimestre</option>
          </select>
        </div>
      </BaseCard>

      <!-- Statistics -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <BaseCard
          v-for="stat in interventionStats"
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

      <!-- Intervention plans list -->
      <div class="space-y-4">
        <div v-if="riskStore.isLoading.interventionPlans" class="flex justify-center py-8">
          <LoadingSpinner size="lg" />
        </div>

        <div v-else-if="interventionPlans.length === 0" class="text-center py-12">
          <DocumentTextIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">Aucun plan d'intervention</h3>
          <p class="mt-1 text-sm text-gray-500">
            Créez votre premier plan d'intervention personnalisé.
          </p>
          <div class="mt-6">
            <BaseButton
              variant="primary"
              @click="showCreateModal = true"
            >
              <PlusIcon class="h-4 w-4 mr-2" />
              Nouveau plan
            </BaseButton>
          </div>
        </div>

        <div v-else class="space-y-4">
          <TransitionGroup
            name="plan"
            tag="div"
            class="space-y-4"
          >
            <InterventionPlanCard
              v-for="plan in interventionPlans"
              :key="plan.id"
              :plan="plan"
              @view-details="viewPlan"
              @edit-plan="editPlan"
              @update-status="updatePlanStatus"
              @archive-plan="archivePlan"
            />
          </TransitionGroup>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > pageSize" class="mt-6">
          <TablePagination
            :current-page="currentPage"
            :total-items="pagination.count"
            :items-per-page="pageSize"
            @page-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <BaseModal
      v-model="showCreateModal"
      :title="editingPlan ? 'Modifier le plan' : 'Nouveau plan d\'intervention'"
      size="xl"
    >
      <InterventionPlanForm
        :plan="editingPlan"
        @save="handlePlanSave"
        @cancel="handlePlanCancel"
      />
    </BaseModal>

    <!-- Analysis Modal -->
    <BaseModal
      v-model="showAnalysisModal"
      title="Lancer une analyse"
      size="lg"
    >
      <AnalysisModal
        @close="showAnalysisModal = false"
        @analysis-started="handleAnalysisStarted"
      />
    </BaseModal>

    <!-- Plan Detail Modal -->
    <BaseModal
      v-model="showDetailModal"
      :title="`Plan: ${selectedPlan?.title || ''}`"
      size="xl"
    >
      <InterventionPlanDetail
        v-if="selectedPlan"
        :plan="selectedPlan"
        @close="showDetailModal = false"
        @edit="editPlan"
        @status-update="updatePlanStatus"
      />
    </BaseModal>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import AppLayout from '@/layouts/AppLayout.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import TablePagination from '@/components/ui/TablePagination.vue'
import InterventionPlanCard from '@/components/risk-detection/InterventionPlanCard.vue'
import InterventionPlanForm from '@/components/risk-detection/InterventionPlanForm.vue'
import InterventionPlanDetail from '@/components/risk-detection/InterventionPlanDetail.vue'
import AnalysisModal from '@/components/risk-detection/AnalysisModal.vue'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { toast } from 'vue-sonner'
import { debounce } from 'lodash-es'

const router = useRouter()
const riskStore = useRiskDetectionStore()

// State
const showCreateModal = ref(false)
const showAnalysisModal = ref(false)
const showDetailModal = ref(false)
const editingPlan = ref(null)
const selectedPlan = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)

const filters = ref({
  search: '',
  status: '',
  priority: '',
  date_range: ''
})

// Computed
const interventionPlans = computed(() => riskStore.interventionPlans)
const pagination = computed(() => riskStore.pagination.interventionPlans)

const interventionStats = computed(() => [
  {
    name: 'Total des plans',
    value: pagination.value.count,
    icon: ClipboardDocumentListIcon,
    iconColor: 'text-blue-600'
  },
  {
    name: 'Plans actifs',
    value: interventionPlans.value.filter(p => p.status === 'active').length,
    icon: CheckCircleIcon,
    iconColor: 'text-green-600'
  },
  {
    name: 'En attente',
    value: interventionPlans.value.filter(p => p.status === 'draft').length,
    icon: ClockIcon,
    iconColor: 'text-yellow-600'
  },
  {
    name: 'Priorités hautes',
    value: interventionPlans.value.filter(p => ['urgent', 'high'].includes(p.priority)).length,
    icon: ExclamationTriangleIcon,
    iconColor: 'text-red-600'
  }
])

// Methods
const debouncedSearch = debounce(() => {
  currentPage.value = 1
  fetchData()
}, 300)

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
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

const viewPlan = (plan: any) => {
  selectedPlan.value = plan
  showDetailModal.value = true
}

const editPlan = (plan: any) => {
  editingPlan.value = { ...plan }
  showCreateModal.value = true
}

const updatePlanStatus = async (planId: string, status: string) => {
  const success = await riskStore.updateInterventionPlanStatus(planId, status)
  if (success) {
    toast.success('Statut du plan mis à jour')
    fetchData()
  }
}

const archivePlan = async (planId: string) => {
  if (confirm('Êtes-vous sûr de vouloir archiver ce plan ?')) {
    const success = await riskStore.archiveInterventionPlan(planId)
    if (success) {
      toast.success('Plan archivé')
      fetchData()
    }
  }
}

const handlePlanSave = (planData: any) => {
  if (editingPlan.value) {
    // Update existing plan
    toast.success('Plan mis à jour')
  } else {
    // Create new plan
    toast.success('Plan créé avec succès')
  }
  
  handlePlanCancel()
  fetchData()
}

const handlePlanCancel = () => {
  showCreateModal.value = false
  editingPlan.value = null
}

const handleAnalysisStarted = () => {
  showAnalysisModal.value = false
  toast.success('Analyse lancée avec succès')
  // Optionally refresh data after analysis
  setTimeout(() => {
    fetchData()
  }, 2000)
}

const fetchData = async () => {
  const filterParams = {
    page: currentPage.value,
    page_size: pageSize.value,
    ordering: '-created_at',
    ...Object.fromEntries(
      Object.entries(filters.value).filter(([_, value]) => value !== '')
    )
  }

  // Handle date range filter
  if (filters.value.date_range) {
    const now = new Date()
    let startDate = ''
    
    switch (filters.value.date_range) {
      case 'week':
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        startDate = weekAgo.toISOString().split('T')[0]
        break
      case 'month':
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        startDate = monthAgo.toISOString().split('T')[0]
        break
      case 'quarter':
        const quarterAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        startDate = quarterAgo.toISOString().split('T')[0]
        break
    }
    
    if (startDate) {
      filterParams.created_at__gte = startDate
    }
  }

  await riskStore.fetchInterventionPlans(filterParams)
}

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.plan-enter-active,
.plan-leave-active {
  transition: all 0.3s ease;
}

.plan-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.plan-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>