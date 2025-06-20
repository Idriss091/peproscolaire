<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900">
            Alertes de risque
          </h1>
          <p class="text-gray-600">
            Gestion des alertes automatiques et notifications
          </p>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <BaseButton
            variant="secondary"
            @click="markAllAsRead"
            :disabled="!hasUnreadAlerts"
          >
            Marquer tout comme lu
          </BaseButton>
          
          <BaseButton
            variant="primary"
            @click="showConfigModal = true"
            v-if="authStore.canAccessAdminPanel"
          >
            <CogIcon class="h-4 w-4 mr-2" />
            Configurer
          </BaseButton>
        </div>
      </div>

      <!-- Filters -->
      <BaseCard padding="md">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <!-- Search -->
          <BaseInput
            v-model="filters.search"
            placeholder="Rechercher une alerte..."
            @input="debouncedSearch"
          >
            <template #prefix>
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </template>
          </BaseInput>

          <!-- Priority filter -->
          <select
            v-model="filters.priority"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Toutes les priorités</option>
            <option value="urgent">Urgente</option>
            <option value="high">Haute</option>
            <option value="normal">Normale</option>
            <option value="low">Faible</option>
          </select>

          <!-- Status filter -->
          <select
            v-model="filters.is_acknowledged"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Tous les statuts</option>
            <option value="false">Non traitées</option>
            <option value="true">Traitées</option>
          </select>

          <!-- Date filter -->
          <select
            v-model="filters.date_range"
            @change="handleFilterChange"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Toutes les dates</option>
            <option value="today">Aujourd'hui</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
          </select>
        </div>
      </BaseCard>

      <!-- Alert statistics -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <BaseCard
          v-for="stat in alertStats"
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

      <!-- Alerts list -->
      <div class="space-y-4">
        <div v-if="riskStore.isLoading.alerts" class="flex justify-center py-8">
          <LoadingSpinner size="lg" />
        </div>

        <div v-else-if="alerts.length === 0" class="text-center py-12">
          <BellIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">Aucune alerte</h3>
          <p class="mt-1 text-sm text-gray-500">
            Aucune alerte ne correspond à vos critères de recherche.
          </p>
        </div>

        <div v-else class="space-y-4">
          <TransitionGroup
            name="alert"
            tag="div"
            class="space-y-4"
          >
            <AlertCard
              v-for="alert in alerts"
              :key="alert.id"
              :alert="alert"
              :class="{ 'ring-2 ring-primary-500': highlightedAlert === alert.id }"
              @acknowledge="handleAcknowledge"
              @mark-read="handleMarkRead"
              @view-student="viewStudent"
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

    <!-- Alert Configuration Modal -->
    <BaseModal
      v-model="showConfigModal"
      title="Configuration des alertes"
      size="xl"
    >
      <AlertConfigurationPanel @close="showConfigModal = false" />
    </BaseModal>

    <!-- Acknowledge Modal -->
    <BaseModal
      v-model="showAcknowledgeModal"
      title="Traiter l'alerte"
      size="md"
    >
      <AcknowledgeModal
        :alert="selectedAlert"
        @close="showAcknowledgeModal = false"
        @acknowledged="handleAlertAcknowledged"
      />
    </BaseModal>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import TablePagination from '@/components/ui/TablePagination.vue'
import AlertCard from '@/components/risk-detection/AlertCard.vue'
import AlertConfigurationPanel from '@/components/risk-detection/AlertConfigurationPanel.vue'
import AcknowledgeModal from '@/components/risk-detection/AcknowledgeModal.vue'
import {
  MagnifyingGlassIcon,
  CogIcon,
  BellIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  FireIcon
} from '@heroicons/vue/24/outline'
import { toast } from 'vue-sonner'
import { debounce } from 'lodash-es'

const route = useRoute()
const router = useRouter()
const riskStore = useRiskDetectionStore()
const authStore = useAuthStore()

// State
const showConfigModal = ref(false)
const showAcknowledgeModal = ref(false)
const selectedAlert = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const highlightedAlert = ref(route.query.highlight as string || '')

const filters = ref({
  search: '',
  priority: '',
  is_acknowledged: '',
  date_range: ''
})

// Computed
const alerts = computed(() => riskStore.alerts)
const pagination = computed(() => riskStore.pagination.alerts)

const hasUnreadAlerts = computed(() => {
  return alerts.value.some(alert => !alert.is_acknowledged)
})

const alertStats = computed(() => [
  {
    name: 'Total des alertes',
    value: pagination.value.count,
    icon: BellIcon,
    iconColor: 'text-blue-600'
  },
  {
    name: 'Non traitées',
    value: alerts.value.filter(a => !a.is_acknowledged).length,
    icon: ExclamationTriangleIcon,
    iconColor: 'text-red-600'
  },
  {
    name: 'Urgentes',
    value: alerts.value.filter(a => a.priority === 'urgent').length,
    icon: FireIcon,
    iconColor: 'text-orange-600'
  },
  {
    name: 'Traitées',
    value: alerts.value.filter(a => a.is_acknowledged).length,
    icon: CheckCircleIcon,
    iconColor: 'text-green-600'
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

const handleAcknowledge = (alert: any) => {
  selectedAlert.value = alert
  showAcknowledgeModal.value = true
}

const handleMarkRead = async (alert: any) => {
  const success = await riskStore.markAlertRead(alert.id)
  if (success) {
    toast.success('Alerte marquée comme lue')
  }
}

const handleAlertAcknowledged = () => {
  showAcknowledgeModal.value = false
  selectedAlert.value = null
  fetchData()
  toast.success('Alerte traitée avec succès')
}

const markAllAsRead = async () => {
  // Implementation would batch mark all unread alerts
  const unreadAlerts = alerts.value.filter(a => !a.is_acknowledged)
  
  for (const alert of unreadAlerts) {
    await riskStore.markAlertRead(alert.id)
  }
  
  toast.success(`${unreadAlerts.length} alertes marquées comme lues`)
  fetchData()
}

const viewStudent = (studentId: string) => {
  router.push(`/risk-detection/profiles?student=${studentId}`)
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
      case 'today':
        startDate = now.toISOString().split('T')[0]
        break
      case 'week':
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        startDate = weekAgo.toISOString().split('T')[0]
        break
      case 'month':
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        startDate = monthAgo.toISOString().split('T')[0]
        break
    }
    
    if (startDate) {
      filterParams.created_at__gte = startDate
    }
  }

  await riskStore.fetchAlerts(filterParams)
}

// Lifecycle
onMounted(() => {
  fetchData()
  
  // Scroll to highlighted alert if specified
  if (highlightedAlert.value) {
    setTimeout(() => {
      const element = document.querySelector(`[data-alert-id="${highlightedAlert.value}"]`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 1000)
  }
})

// Watch for route changes
watch(() => route.query.highlight, (newHighlight) => {
  highlightedAlert.value = newHighlight as string || ''
})
</script>

<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: all 0.3s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>