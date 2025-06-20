<template>
  <div class="space-y-6">
    <!-- Alert summary -->
    <div class="bg-gray-50 rounded-lg p-4">
      <div class="flex items-start space-x-3">
        <div :class="getAlertIconClasses(alert?.priority)">
          <component :is="getAlertIcon(alert?.priority)" class="h-5 w-5" />
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-gray-900">
            {{ alert?.title }}
          </h3>
          <p class="text-sm text-gray-600 mt-1">
            {{ alert?.message }}
          </p>
          <div class="mt-2 text-xs text-gray-500">
            <span>{{ alert?.risk_profile.student.first_name }} {{ alert?.risk_profile.student.last_name }}</span>
            <span class="mx-2">•</span>
            <span>{{ formatDate(alert?.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions taken form -->
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="actions-taken" class="block text-sm font-medium text-gray-700 mb-2">
          Actions prises *
        </label>
        <textarea
          id="actions-taken"
          v-model="form.actions_taken"
          rows="4"
          required
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          placeholder="Décrivez les actions prises pour traiter cette alerte..."
        />
        <p class="mt-1 text-xs text-gray-500">
          Décrivez en détail les mesures prises ou les décisions arrêtées suite à cette alerte.
        </p>
      </div>

      <!-- Quick action templates -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Actions courantes
        </label>
        <div class="grid grid-cols-1 gap-2">
          <button
            v-for="template in actionTemplates"
            :key="template.id"
            type="button"
            class="text-left p-3 border border-gray-200 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
            @click="selectTemplate(template)"
          >
            <div class="font-medium text-sm text-gray-900">
              {{ template.title }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ template.description }}
            </div>
          </button>
        </div>
      </div>

      <!-- Additional options -->
      <div class="space-y-3">
        <div class="flex items-center">
          <input
            id="create-intervention"
            v-model="form.create_intervention"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="create-intervention" class="ml-2 block text-sm text-gray-900">
            Créer un plan d'intervention automatiquement
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="schedule-followup"
            v-model="form.schedule_followup"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="schedule-followup" class="ml-2 block text-sm text-gray-900">
            Programmer un suivi dans 7 jours
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="notify-parents"
            v-model="form.notify_parents"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="notify-parents" class="ml-2 block text-sm text-gray-900">
            Notifier les parents de la résolution
          </label>
        </div>
      </div>
    </form>

    <!-- Footer buttons -->
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        variant="primary"
        :loading="isLoading"
        :disabled="!form.actions_taken.trim()"
        @click="handleSubmit"
      >
        Traiter l'alerte
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  ExclamationTriangleIcon,
  FireIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Alert } from '@/types'

interface Props {
  alert: Alert | null
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  acknowledged: []
}>()

const riskStore = useRiskDetectionStore()

// State
const isLoading = ref(false)

const form = ref({
  actions_taken: '',
  create_intervention: false,
  schedule_followup: false,
  notify_parents: false
})

const actionTemplates = ref([
  {
    id: 1,
    title: 'Entretien individuel réalisé',
    description: 'Un entretien a été mené avec l\'élève pour comprendre les difficultés',
    text: 'Entretien individuel réalisé avec l\'élève le [DATE]. Discussion sur les difficultés rencontrées et identification des besoins de soutien. L\'élève s\'engage à [ACTIONS ÉLÈVE].'
  },
  {
    id: 2,
    title: 'Contact avec la famille',
    description: 'Les parents ont été contactés pour les informer de la situation',
    text: 'Contact téléphonique/mail avec la famille pour les informer de la situation et des préoccupations. Échange sur les observations à domicile et coordination des actions famille/école.'
  },
  {
    id: 3,
    title: 'Mise en place d\'un soutien',
    description: 'Des mesures de soutien scolaire ont été organisées',
    text: 'Mise en place d\'un dispositif de soutien scolaire : [DÉTAILS]. Planning et modalités définies avec l\'élève et sa famille.'
  },
  {
    id: 4,
    title: 'Orientation vers un professionnel',
    description: 'L\'élève a été orienté vers un conseiller ou psychologue',
    text: 'Orientation de l\'élève vers [PROFESSIONNEL] pour un accompagnement adapté. Prise de rendez-vous et information de la famille sur le suivi.'
  },
  {
    id: 5,
    title: 'Surveillance renforcée',
    description: 'Un suivi plus étroit a été mis en place',
    text: 'Mise en place d\'une surveillance renforcée avec points réguliers. Suivi hebdomadaire prévu avec [RÉFÉRENT] pour évaluer l\'évolution.'
  },
  {
    id: 6,
    title: 'Alerte non fondée',
    description: 'Après vérification, l\'alerte ne nécessite pas d\'action',
    text: 'Après vérification et échanges avec l\'élève et l\'équipe pédagogique, l\'alerte ne nécessite pas d\'action particulière à ce stade. Situation normale.'
  }
])

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
  const baseClasses = 'flex-shrink-0 rounded-full p-1'
  
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

const selectTemplate = (template: any) => {
  const currentDate = new Date().toLocaleDateString('fr-FR')
  form.value.actions_taken = template.text.replace('[DATE]', currentDate)
}

const handleSubmit = async () => {
  if (!props.alert || !form.value.actions_taken.trim()) return

  isLoading.value = true

  try {
    const success = await riskStore.acknowledgeAlert(
      props.alert.id,
      form.value.actions_taken
    )

    if (success) {
      // Handle additional options
      if (form.value.create_intervention) {
        // Logic to create intervention plan
        console.log('Creating intervention plan...')
      }

      if (form.value.schedule_followup) {
        // Logic to schedule follow-up
        console.log('Scheduling follow-up...')
      }

      if (form.value.notify_parents) {
        // Logic to notify parents
        console.log('Notifying parents...')
      }

      emit('acknowledged')
    }
  } finally {
    isLoading.value = false
  }
}
</script>