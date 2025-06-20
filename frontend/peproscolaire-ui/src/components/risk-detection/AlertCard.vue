<template>
  <BaseCard
    :class="[
      'transition-all duration-200 hover:shadow-lg cursor-pointer',
      !alert.is_acknowledged ? 'border-l-4 border-l-red-500' : '',
      !alert.is_read ? 'bg-blue-50' : 'bg-white'
    ]"
    @click="$emit('view-details', alert)"
  >
    <div class="flex items-start space-x-4">
      <!-- Alert icon -->
      <div :class="getAlertIconClasses(alert.priority)">
        <component :is="getAlertIcon(alert.priority)" class="h-6 w-6" />
      </div>

      <!-- Alert content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <!-- Alert title and priority -->
            <div class="flex items-center space-x-2">
              <h3 class="text-lg font-medium text-gray-900">
                {{ alert.title }}
              </h3>
              <BaseBadge :variant="getPriorityVariant(alert.priority)" size="sm">
                {{ getPriorityLabel(alert.priority) }}
              </BaseBadge>
              <BaseBadge
                v-if="!alert.is_acknowledged"
                variant="danger"
                size="sm"
              >
                Non traitée
              </BaseBadge>
            </div>

            <!-- Student info -->
            <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
              <div class="flex items-center">
                <UserIcon class="h-4 w-4 mr-1" />
                <span>{{ alert.risk_profile.student.first_name }} {{ alert.risk_profile.student.last_name }}</span>
              </div>
              <div class="flex items-center">
                <CalendarIcon class="h-4 w-4 mr-1" />
                <span>{{ formatDate(alert.created_at) }}</span>
              </div>
              <div v-if="alert.acknowledged_by" class="flex items-center">
                <CheckCircleIcon class="h-4 w-4 mr-1 text-green-500" />
                <span>Traitée par {{ alert.acknowledged_by.first_name }} {{ alert.acknowledged_by.last_name }}</span>
              </div>
            </div>

            <!-- Alert message -->
            <p class="mt-2 text-gray-700">
              {{ alert.message }}
            </p>

            <!-- Risk context -->
            <div v-if="alert.context_data" class="mt-3 grid grid-cols-2 gap-4 text-sm">
              <div v-if="alert.context_data.risk_score" class="flex items-center">
                <span class="text-gray-500">Score de risque:</span>
                <span class="ml-2 font-medium">{{ Math.round(alert.context_data.risk_score) }}/100</span>
              </div>
              <div v-if="alert.context_data.risk_factors" class="flex items-center">
                <span class="text-gray-500">Facteurs:</span>
                <span class="ml-2 font-medium">{{ Object.keys(alert.context_data.risk_factors).length }}</span>
              </div>
            </div>

            <!-- Actions taken -->
            <div v-if="alert.actions_taken" class="mt-3 p-3 bg-gray-50 rounded-md">
              <h4 class="text-sm font-medium text-gray-900 mb-1">Actions prises:</h4>
              <p class="text-sm text-gray-700">{{ alert.actions_taken }}</p>
            </div>
          </div>

          <!-- Quick actions -->
          <div class="flex-shrink-0 ml-4">
            <div class="flex flex-col space-y-2">
              <BaseButton
                v-if="!alert.is_acknowledged"
                size="sm"
                variant="primary"
                @click.stop="$emit('acknowledge', alert)"
              >
                Traiter
              </BaseButton>
              
              <BaseButton
                v-if="!alert.is_read"
                size="sm"
                variant="secondary"
                @click.stop="$emit('mark-read', alert)"
              >
                Marquer lu
              </BaseButton>
              
              <BaseButton
                size="sm"
                variant="ghost"
                @click.stop="$emit('view-student', alert.risk_profile.student.id)"
              >
                Voir l'élève
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification status -->
    <div v-if="alert.notifications_sent" class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center space-x-4 text-xs text-gray-500">
        <span class="flex items-center">
          <BellIcon class="h-3 w-3 mr-1" />
          Notifications envoyées:
        </span>
        <span v-if="alert.notifications_sent.student">Élève</span>
        <span v-if="alert.notifications_sent.parents">Parents ({{ alert.notifications_sent.parents }})</span>
        <span v-if="alert.notifications_sent.main_teacher">Professeur principal</span>
        <span v-if="alert.notifications_sent.additional">Autres ({{ alert.notifications_sent.additional }})</span>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  ExclamationTriangleIcon,
  FireIcon,
  InformationCircleIcon,
  UserIcon,
  CalendarIcon,
  CheckCircleIcon,
  BellIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Alert } from '@/types'

interface Props {
  alert: Alert
}

defineProps<Props>()

const emit = defineEmits<{
  'view-details': [alert: Alert]
  acknowledge: [alert: Alert]
  'mark-read': [alert: Alert]
  'view-student': [studentId: string]
}>()

// Methods
const formatDate = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const getAlertIcon = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return FireIcon
    case 'high':
      return ExclamationTriangleIcon
    default:
      return InformationCircleIcon
  }
}

const getAlertIconClasses = (priority: string) => {
  const baseClasses = 'flex-shrink-0 rounded-full p-2'
  
  switch (priority) {
    case 'urgent':
      return `${baseClasses} bg-red-100 text-red-600`
    case 'high':
      return `${baseClasses} bg-orange-100 text-orange-600`
    case 'normal':
      return `${baseClasses} bg-blue-100 text-blue-600`
    default:
      return `${baseClasses} bg-gray-100 text-gray-600`
  }
}

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
</script>