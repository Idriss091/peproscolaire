<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-medium text-gray-900">
          Configurations d'alerte
        </h3>
        <p class="text-sm text-gray-500">
          Gérez les règles de déclenchement automatique des alertes
        </p>
      </div>
      
      <BaseButton
        variant="primary"
        @click="showCreateModal = true"
      >
        <PlusIcon class="h-4 w-4 mr-2" />
        Nouvelle configuration
      </BaseButton>
    </div>

    <!-- Configurations list -->
    <div class="space-y-4">
      <div v-if="isLoading" class="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>

      <div v-else-if="configurations.length === 0" class="text-center py-8">
        <CogIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">Aucune configuration</h3>
        <p class="mt-1 text-sm text-gray-500">
          Créez votre première configuration d'alerte.
        </p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="config in configurations"
          :key="config.id"
          class="py-4 flex items-center justify-between"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <h4 class="text-sm font-medium text-gray-900">
                {{ config.name }}
              </h4>
              <BaseBadge
                :variant="config.is_active ? 'success' : 'secondary'"
                size="sm"
              >
                {{ config.is_active ? 'Active' : 'Inactive' }}
              </BaseBadge>
              <BaseBadge :variant="getPriorityVariant(config.priority)" size="sm">
                {{ getPriorityLabel(config.priority) }}
              </BaseBadge>
            </div>
            
            <p class="text-sm text-gray-500 mt-1">
              {{ config.description }}
            </p>
            
            <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500">
              <span v-if="config.risk_level_threshold">
                Niveau: {{ getRiskLevelLabel(config.risk_level_threshold) }}+
              </span>
              <span v-if="config.risk_score_threshold">
                Score: {{ config.risk_score_threshold }}+
              </span>
              <span>
                Cooldown: {{ config.cooldown_days }}j
              </span>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <BaseButton
              size="sm"
              variant="ghost"
              @click="testConfiguration(config)"
              :loading="testingConfigs.includes(config.id)"
            >
              Tester
            </BaseButton>
            
            <BaseButton
              size="sm"
              variant="ghost"
              @click="editConfiguration(config)"
            >
              Modifier
            </BaseButton>
            
            <BaseButton
              size="sm"
              variant="ghost"
              @click="toggleConfiguration(config)"
            >
              {{ config.is_active ? 'Désactiver' : 'Activer' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex justify-end pt-4 border-t">
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Fermer
      </BaseButton>
    </div>

    <!-- Create/Edit Modal -->
    <BaseModal
      v-model="showCreateModal"
      :title="editingConfig ? 'Modifier la configuration' : 'Nouvelle configuration'"
      size="lg"
    >
      <ConfigurationForm
        :config="editingConfig"
        @save="handleConfigSave"
        @cancel="handleConfigCancel"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ConfigurationForm from './ConfigurationForm.vue'
import {
  PlusIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import { toast } from 'vue-sonner'

const emit = defineEmits<{
  close: []
}>()

const riskStore = useRiskDetectionStore()

// State
const isLoading = ref(false)
const showCreateModal = ref(false)
const editingConfig = ref(null)
const testingConfigs = ref<string[]>([])

// Mock configurations - à remplacer par les vraies données
const configurations = ref([
  {
    id: '1',
    name: 'Risque critique détecté',
    description: 'Alerte lorsqu\'un élève atteint un niveau de risque critique',
    alert_type: 'risk_increase',
    risk_level_threshold: 'critical',
    risk_score_threshold: 80,
    priority: 'urgent',
    is_active: true,
    cooldown_days: 7,
    message_template: 'Alerte critique: {student_name} nécessite une intervention immédiate (score: {risk_score})'
  },
  {
    id: '2',
    name: 'Augmentation rapide du risque',
    description: 'Détecte une augmentation significative du score de risque',
    alert_type: 'threshold_reached',
    risk_score_threshold: 60,
    priority: 'high',
    is_active: true,
    cooldown_days: 14,
    message_template: 'Le score de risque de {student_name} a atteint {risk_score}/100'
  },
  {
    id: '3',
    name: 'Pattern d\'absence détecté',
    description: 'Alerte lors de la détection de patterns d\'absence préoccupants',
    alert_type: 'pattern_detected',
    priority: 'normal',
    is_active: false,
    cooldown_days: 30,
    message_template: 'Pattern d\'absence détecté pour {student_name}'
  }
])

// Methods
const getPriorityVariant = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return 'danger'
    case 'high':
      return 'warning'
    case 'normal':
      return 'info'
    default:
      return 'secondary'
  }
}

const getPriorityLabel = (priority: string) => {
  const labels = {
    urgent: 'Urgente',
    high: 'Haute',
    normal: 'Normale',
    low: 'Faible'
  }
  return labels[priority] || priority
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

const testConfiguration = async (config: any) => {
  testingConfigs.value.push(config.id)
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    toast.success(`Configuration "${config.name}" testée avec succès`)
  } catch (error) {
    toast.error('Erreur lors du test de la configuration')
  } finally {
    testingConfigs.value = testingConfigs.value.filter(id => id !== config.id)
  }
}

const editConfiguration = (config: any) => {
  editingConfig.value = { ...config }
  showCreateModal.value = true
}

const toggleConfiguration = async (config: any) => {
  try {
    config.is_active = !config.is_active
    toast.success(`Configuration ${config.is_active ? 'activée' : 'désactivée'}`)
  } catch (error) {
    config.is_active = !config.is_active // Revert on error
    toast.error('Erreur lors de la modification')
  }
}

const handleConfigSave = (configData: any) => {
  if (editingConfig.value) {
    // Update existing config
    const index = configurations.value.findIndex(c => c.id === editingConfig.value.id)
    if (index !== -1) {
      configurations.value[index] = { ...configData, id: editingConfig.value.id }
    }
    toast.success('Configuration mise à jour')
  } else {
    // Create new config
    const newConfig = {
      ...configData,
      id: Math.random().toString(36).substr(2, 9)
    }
    configurations.value.push(newConfig)
    toast.success('Configuration créée')
  }
  
  handleConfigCancel()
}

const handleConfigCancel = () => {
  showCreateModal.value = false
  editingConfig.value = null
}

// Lifecycle
onMounted(() => {
  // Load configurations
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
})
</script>