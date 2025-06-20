<template>
  <BaseCard
    :class="[
      'transition-all duration-200 hover:shadow-lg cursor-pointer',
      getStatusClasses(plan.status)
    ]"
    @click="$emit('view-details', plan)"
  >
    <div class="space-y-4">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-3">
            <h3 class="text-lg font-medium text-gray-900 truncate">
              {{ plan.title }}
            </h3>
            <BaseBadge :variant="getStatusVariant(plan.status)" size="sm">
              {{ getStatusLabel(plan.status) }}
            </BaseBadge>
            <BaseBadge :variant="getPriorityVariant(plan.priority)" size="sm">
              {{ getPriorityLabel(plan.priority) }}
            </BaseBadge>
          </div>
          
          <!-- Student info -->
          <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
            <div class="flex items-center">
              <UserIcon class="h-4 w-4 mr-1" />
              <span>{{ plan.risk_profile.student.first_name }} {{ plan.risk_profile.student.last_name }}</span>
            </div>
            <div class="flex items-center">
              <CalendarIcon class="h-4 w-4 mr-1" />
              <span>Créé {{ formatDate(plan.created_at) }}</span>
            </div>
            <div v-if="plan.created_by" class="flex items-center">
              <UserCircleIcon class="h-4 w-4 mr-1" />
              <span>{{ plan.created_by.first_name }} {{ plan.created_by.last_name }}</span>
            </div>
          </div>
        </div>

        <!-- Quick actions -->
        <div class="flex-shrink-0 ml-4">
          <div class="flex space-x-2">
            <BaseButton
              size="sm"
              variant="ghost"
              @click.stop="$emit('edit-plan', plan)"
            >
              <PencilIcon class="h-4 w-4" />
            </BaseButton>
            
            <div class="relative">
              <BaseButton
                size="sm"
                variant="ghost"
                @click.stop="showDropdown = !showDropdown"
              >
                <EllipsisVerticalIcon class="h-4 w-4" />
              </BaseButton>
              
              <!-- Dropdown menu -->
              <div
                v-if="showDropdown"
                v-click-outside="() => showDropdown = false"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
              >
                <div class="py-1">
                  <button
                    v-for="action in statusActions"
                    :key="action.status"
                    @click.stop="handleStatusChange(action.status)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {{ action.label }}
                  </button>
                  <div class="border-t border-gray-100"></div>
                  <button
                    @click.stop="$emit('archive-plan', plan.id)"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Archiver
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Description -->
      <p v-if="plan.description" class="text-gray-700 text-sm line-clamp-2">
        {{ plan.description }}
      </p>

      <!-- Objectives -->
      <div v-if="plan.objectives && plan.objectives.length > 0" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-900">Objectifs principaux:</h4>
        <div class="space-y-1">
          <div
            v-for="(objective, index) in plan.objectives.slice(0, 2)"
            :key="index"
            class="flex items-center text-sm text-gray-600"
          >
            <CheckCircleIcon class="h-4 w-4 mr-2 text-green-500" />
            <span class="truncate">{{ objective.description }}</span>
          </div>
          <div v-if="plan.objectives.length > 2" class="text-xs text-gray-500">
            +{{ plan.objectives.length - 2 }} autres objectifs
          </div>
        </div>
      </div>

      <!-- Progress and timeline -->
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-500">Progression:</span>
          <div class="mt-1 flex items-center">
            <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${plan.progress_percentage || 0}%` }"
              ></div>
            </div>
            <span class="font-medium">{{ Math.round(plan.progress_percentage || 0) }}%</span>
          </div>
        </div>
        
        <div>
          <span class="text-gray-500">Échéance:</span>
          <div class="mt-1 flex items-center">
            <ClockIcon class="h-4 w-4 mr-1 text-gray-400" />
            <span :class="isOverdue ? 'text-red-600 font-medium' : 'text-gray-900'">
              {{ plan.target_date ? formatDate(plan.target_date) : 'Non définie' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Actions and participants -->
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-500">Actions:</span>
          <div class="mt-1">
            <span class="font-medium">{{ plan.actions?.length || 0 }}</span>
            <span class="text-gray-600 ml-1">
              ({{ plan.actions?.filter(a => a.status === 'completed').length || 0 }} terminées)
            </span>
          </div>
        </div>
        
        <div>
          <span class="text-gray-500">Participants:</span>
          <div class="mt-1 flex items-center">
            <div class="flex -space-x-1">
              <div
                v-for="(participant, index) in (plan.participants || []).slice(0, 3)"
                :key="participant.id"
                class="relative z-10 inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-300"
                :title="`${participant.first_name} ${participant.last_name}`"
              >
                <div class="h-full w-full rounded-full bg-primary-500 flex items-center justify-center text-xs text-white font-medium">
                  {{ participant.first_name[0] }}{{ participant.last_name[0] }}
                </div>
              </div>
              <div
                v-if="(plan.participants || []).length > 3"
                class="relative z-10 inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-200 flex items-center justify-center text-xs text-gray-600 font-medium"
              >
                +{{ (plan.participants || []).length - 3 }}
              </div>
            </div>
            <span v-if="!plan.participants || plan.participants.length === 0" class="text-gray-500">
              Aucun
            </span>
          </div>
        </div>
      </div>

      <!-- Recent activity -->
      <div v-if="plan.last_activity" class="pt-3 border-t border-gray-200">
        <div class="flex items-center text-xs text-gray-500">
          <ClockIcon class="h-3 w-3 mr-1" />
          <span>Dernière activité: {{ formatDate(plan.last_activity.created_at) }}</span>
          <span class="mx-2">•</span>
          <span>{{ plan.last_activity.description }}</span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  UserIcon,
  CalendarIcon,
  UserCircleIcon,
  PencilIcon,
  EllipsisVerticalIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { InterventionPlan } from '@/types'

interface Props {
  plan: InterventionPlan
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'view-details': [plan: InterventionPlan]
  'edit-plan': [plan: InterventionPlan]
  'update-status': [planId: string, status: string]
  'archive-plan': [planId: string]
}>()

// State
const showDropdown = ref(false)

// Computed
const isOverdue = computed(() => {
  if (!props.plan.target_date) return false
  return new Date(props.plan.target_date) < new Date()
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

const getStatusClasses = (status: string) => {
  switch (status) {
    case 'active':
      return 'border-l-4 border-l-green-500'
    case 'on_hold':
      return 'border-l-4 border-l-yellow-500'
    case 'completed':
      return 'border-l-4 border-l-blue-500'
    case 'draft':
      return 'border-l-4 border-l-gray-400'
    default:
      return ''
  }
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

const handleStatusChange = (status: string) => {
  showDropdown.value = false
  emit('update-status', props.plan.id, status)
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

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>