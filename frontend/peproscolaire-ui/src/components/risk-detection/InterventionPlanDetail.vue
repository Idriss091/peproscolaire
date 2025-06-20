<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center space-x-3">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ plan.title }}
          </h2>
          <BaseBadge :variant="getStatusVariant(plan.status)" size="md">
            {{ getStatusLabel(plan.status) }}
          </BaseBadge>
          <BaseBadge :variant="getPriorityVariant(plan.priority)" size="md">
            {{ getPriorityLabel(plan.priority) }}
          </BaseBadge>
        </div>
        
        <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
          <span>Créé {{ formatDate(plan.created_at) }}</span>
          <span v-if="plan.created_by">
            par {{ plan.created_by.first_name }} {{ plan.created_by.last_name }}
          </span>
          <span v-if="plan.last_updated">
            • Modifié {{ formatDate(plan.last_updated) }}
          </span>
        </div>
      </div>
      
      <div class="flex space-x-2">
        <BaseButton
          variant="secondary"
          size="sm"
          @click="$emit('edit', plan)"
        >
          <PencilIcon class="h-4 w-4 mr-1" />
          Modifier
        </BaseButton>
        
        <div class="relative">
          <BaseButton
            variant="ghost"
            size="sm"
            @click="showStatusMenu = !showStatusMenu"
          >
            <EllipsisVerticalIcon class="h-4 w-4" />
          </BaseButton>
          
          <!-- Status menu -->
          <div
            v-if="showStatusMenu"
            v-click-outside="() => showStatusMenu = false"
            class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10"
          >
            <div class="py-1">
              <button
                v-for="action in statusActions"
                :key="action.status"
                @click="handleStatusChange(action.status)"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Student info -->
    <BaseCard>
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
            <UserIcon class="h-6 w-6 text-primary-600" />
          </div>
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-medium text-gray-900">
            {{ plan.risk_profile.student.first_name }} {{ plan.risk_profile.student.last_name }}
          </h3>
          <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
            <span>{{ plan.risk_profile.student.email }}</span>
            <span v-if="plan.risk_profile.current_risk_score">
              Score de risque: {{ Math.round(plan.risk_profile.current_risk_score) }}/100
            </span>
            <span v-if="plan.risk_profile.risk_level">
              Niveau: {{ getRiskLevelLabel(plan.risk_profile.risk_level) }}
            </span>
          </div>
        </div>
        <BaseButton
          variant="ghost"
          size="sm"
          @click="viewStudentProfile"
        >
          Voir le profil
        </BaseButton>
      </div>
    </BaseCard>

    <!-- Description -->
    <BaseCard v-if="plan.description">
      <h3 class="text-lg font-medium text-gray-900 mb-3">Description</h3>
      <p class="text-gray-700 whitespace-pre-line">{{ plan.description }}</p>
    </BaseCard>

    <!-- Progress overview -->
    <BaseCard>
      <h3 class="text-lg font-medium text-gray-900 mb-4">Progression générale</h3>
      
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">Progression</span>
            <span class="text-sm font-semibold text-gray-900">
              {{ Math.round(plan.progress_percentage || 0) }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${plan.progress_percentage || 0}%` }"
            ></div>
          </div>
        </div>
        
        <div>
          <span class="text-sm font-medium text-gray-700">Dates</span>
          <div class="mt-2 space-y-1 text-sm text-gray-600">
            <div v-if="plan.start_date">
              Début: {{ formatDateShort(plan.start_date) }}
            </div>
            <div v-if="plan.target_date">
              Cible: {{ formatDateShort(plan.target_date) }}
              <span v-if="isOverdue" class="text-red-600 font-medium ml-1">
                (En retard)
              </span>
            </div>
          </div>
        </div>
        
        <div>
          <span class="text-sm font-medium text-gray-700">Participants</span>
          <div class="mt-2 flex items-center space-x-2">
            <div class="flex -space-x-1">
              <div
                v-for="participant in (plan.participants || []).slice(0, 4)"
                :key="participant.id"
                class="relative z-10 inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-300"
                :title="`${participant.first_name} ${participant.last_name}`"
              >
                <div class="h-full w-full rounded-full bg-primary-500 flex items-center justify-center text-xs text-white font-medium">
                  {{ participant.first_name[0] }}{{ participant.last_name[0] }}
                </div>
              </div>
              <div
                v-if="(plan.participants || []).length > 4"
                class="relative z-10 inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-200 flex items-center justify-center text-xs text-gray-600 font-medium"
              >
                +{{ (plan.participants || []).length - 4 }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Objectives -->
    <BaseCard>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Objectifs</h3>
        <span class="text-sm text-gray-500">
          {{ completedObjectives }}/{{ plan.objectives?.length || 0 }} terminés
        </span>
      </div>
      
      <div v-if="!plan.objectives || plan.objectives.length === 0" class="text-center py-6">
        <DocumentTextIcon class="mx-auto h-8 w-8 text-gray-400" />
        <p class="mt-2 text-sm text-gray-500">Aucun objectif défini</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="(objective, index) in plan.objectives"
          :key="index"
          class="flex items-start space-x-3 p-3 border border-gray-200 rounded-md"
        >
          <div class="flex-shrink-0 pt-0.5">
            <input
              type="checkbox"
              :checked="objective.status === 'completed'"
              @change="toggleObjective(index)"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900">
              {{ objective.description }}
            </p>
            <div class="mt-1 flex items-center space-x-4 text-xs text-gray-500">
              <span v-if="objective.target_date">
                Cible: {{ formatDateShort(objective.target_date) }}
              </span>
              <span class="capitalize">
                Priorité {{ objective.priority }}
              </span>
              <BaseBadge
                :variant="objective.status === 'completed' ? 'success' : 'secondary'"
                size="xs"
              >
                {{ objective.status === 'completed' ? 'Terminé' : 'En cours' }}
              </BaseBadge>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Actions -->
    <BaseCard>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Actions</h3>
        <span class="text-sm text-gray-500">
          {{ completedActions }}/{{ plan.actions?.length || 0 }} terminées
        </span>
      </div>
      
      <div v-if="!plan.actions || plan.actions.length === 0" class="text-center py-6">
        <ClipboardDocumentListIcon class="mx-auto h-8 w-8 text-gray-400" />
        <p class="mt-2 text-sm text-gray-500">Aucune action définie</p>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="(action, index) in plan.actions"
          :key="index"
          class="border border-gray-200 rounded-md p-4"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 pt-0.5">
              <input
                type="checkbox"
                :checked="action.status === 'completed'"
                @change="toggleAction(index)"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="text-sm font-medium text-gray-900">
                {{ action.title }}
              </h4>
              <p v-if="action.description" class="mt-1 text-sm text-gray-600">
                {{ action.description }}
              </p>
              <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                <span v-if="action.due_date">
                  Échéance: {{ formatDateShort(action.due_date) }}
                  <span v-if="isActionOverdue(action)" class="text-red-600 font-medium ml-1">
                    (En retard)
                  </span>
                </span>
                <span class="capitalize">
                  Priorité {{ action.priority }}
                </span>
                <BaseBadge
                  :variant="getActionStatusVariant(action.status)"
                  size="xs"
                >
                  {{ getActionStatusLabel(action.status) }}
                </BaseBadge>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Notes and comments -->
    <BaseCard v-if="plan.notes">
      <h3 class="text-lg font-medium text-gray-900 mb-3">Notes</h3>
      <div class="space-y-3">
        <div
          v-for="note in plan.notes"
          :key="note.id"
          class="p-3 bg-gray-50 rounded-md"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <p class="text-sm text-gray-700">{{ note.content }}</p>
              <div class="mt-1 text-xs text-gray-500">
                {{ note.author.first_name }} {{ note.author.last_name }} • {{ formatDate(note.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Footer -->
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Fermer
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  UserIcon,
  PencilIcon,
  EllipsisVerticalIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow, format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { InterventionPlan } from '@/types'

interface Props {
  plan: InterventionPlan
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  edit: [plan: InterventionPlan]
  'status-update': [planId: string, status: string]
}>()

// State
const showStatusMenu = ref(false)

// Computed
const isOverdue = computed(() => {
  if (!props.plan.target_date) return false
  return new Date(props.plan.target_date) < new Date()
})

const completedObjectives = computed(() => {
  return props.plan.objectives?.filter(obj => obj.status === 'completed').length || 0
})

const completedActions = computed(() => {
  return props.plan.actions?.filter(action => action.status === 'completed').length || 0
})

const statusActions = computed(() => {
  const actions = []
  
  if (props.plan.status === 'draft') {
    actions.push({ status: 'active', label: 'Activer le plan' })
  }
  
  if (props.plan.status === 'active') {
    actions.push(
      { status: 'on_hold', label: 'Mettre en pause' },
      { status: 'completed', label: 'Marquer comme terminé' }
    )
  }
  
  if (props.plan.status === 'on_hold') {
    actions.push(
      { status: 'active', label: 'Reprendre le plan' },
      { status: 'completed', label: 'Marquer comme terminé' }
    )
  }
  
  if (props.plan.status === 'completed') {
    actions.push({ status: 'active', label: 'Réactiver le plan' })
  }
  
  return actions
})

// Methods
const formatDate = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const formatDateShort = (dateString: string) => {
  return format(new Date(dateString), 'dd/MM/yyyy', { locale: fr })
}

const getStatusVariant = (status: string) => {
  switch (status) {
    case 'active':
      return 'success'
    case 'on_hold':
      return 'warning'
    case 'completed':
      return 'info'
    case 'draft':
      return 'secondary'
    default:
      return 'secondary'
  }
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: 'Brouillon',
    active: 'Actif',
    on_hold: 'En pause',
    completed: 'Terminé'
  }
  return labels[status] || status
}

const getPriorityVariant = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return 'danger'
    case 'high':
      return 'warning'
    case 'normal':
      return 'info'
    case 'low':
      return 'secondary'
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

const getActionStatusVariant = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'in_progress':
      return 'info'
    case 'pending':
      return 'secondary'
    default:
      return 'secondary'
  }
}

const getActionStatusLabel = (status: string) => {
  const labels = {
    pending: 'En attente',
    in_progress: 'En cours',
    completed: 'Terminée'
  }
  return labels[status] || status
}

const isActionOverdue = (action: any) => {
  if (!action.due_date || action.status === 'completed') return false
  return new Date(action.due_date) < new Date()
}

const handleStatusChange = (status: string) => {
  showStatusMenu.value = false
  emit('status-update', props.plan.id, status)
}

const toggleObjective = (index: number) => {
  // In a real app, this would make an API call
  const objective = props.plan.objectives[index]
  objective.status = objective.status === 'completed' ? 'pending' : 'completed'
}

const toggleAction = (index: number) => {
  // In a real app, this would make an API call
  const action = props.plan.actions[index]
  action.status = action.status === 'completed' ? 'pending' : 'completed'
}

const viewStudentProfile = () => {
  // Navigate to student profile
  console.log('Navigate to student profile')
}

// Click outside directive
const vClickOutside = {
  mounted(el: HTMLElement, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>