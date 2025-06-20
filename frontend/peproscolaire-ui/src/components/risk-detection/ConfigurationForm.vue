<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Basic information -->
    <div class="space-y-4">
      <BaseInput
        v-model="form.name"
        label="Nom de la configuration *"
        placeholder="Ex: Risque critique détecté"
        required
        :error="errors.name"
      />

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          v-model="form.description"
          rows="3"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          placeholder="Décrivez quand cette alerte doit être déclenchée..."
        />
      </div>
    </div>

    <!-- Alert configuration -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Configuration de l'alerte</h3>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Type d'alerte *
          </label>
          <select
            v-model="form.alert_type"
            required
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Choisir un type...</option>
            <option value="threshold_reached">Seuil atteint</option>
            <option value="risk_increase">Augmentation du risque</option>
            <option value="pattern_detected">Pattern détecté</option>
            <option value="intervention_needed">Intervention nécessaire</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Priorité *
          </label>
          <select
            v-model="form.priority"
            required
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Choisir une priorité...</option>
            <option value="low">Faible</option>
            <option value="normal">Normale</option>
            <option value="high">Haute</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Triggers -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Conditions de déclenchement</h3>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Niveau de risque minimum
          </label>
          <select
            v-model="form.risk_level_threshold"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Aucun seuil</option>
            <option value="very_low">Très faible</option>
            <option value="low">Faible</option>
            <option value="moderate">Modéré</option>
            <option value="high">Élevé</option>
            <option value="critical">Critique</option>
          </select>
        </div>

        <BaseInput
          v-model.number="form.risk_score_threshold"
          label="Score de risque minimum"
          type="number"
          min="0"
          max="100"
          placeholder="Ex: 70"
        />
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <BaseInput
          v-model.number="form.cooldown_days"
          label="Période de cooldown (jours) *"
          type="number"
          min="1"
          max="365"
          required
          placeholder="Ex: 7"
          help="Délai minimum entre deux alertes similaires pour le même élève"
        />

        <div class="flex items-center pt-6">
          <input
            id="is-active"
            v-model="form.is_active"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="is-active" class="ml-2 block text-sm text-gray-900">
            Configuration active
          </label>
        </div>
      </div>
    </div>

    <!-- Message template -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Modèle de message *
      </label>
      <textarea
        v-model="form.message_template"
        rows="4"
        required
        class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        placeholder="Ex: Alerte {priority}: {student_name} nécessite une attention (score: {risk_score})"
      />
      <p class="mt-1 text-sm text-gray-500">
        Variables disponibles: {student_name}, {risk_score}, {risk_level}, {priority}
      </p>
    </div>

    <!-- Notification settings -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Notifications</h3>
      
      <div class="space-y-3">
        <div class="flex items-center">
          <input
            id="notify-student"
            v-model="form.notify_student"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="notify-student" class="ml-2 block text-sm text-gray-900">
            Notifier l'élève
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
            Notifier les parents
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="notify-main-teacher"
            v-model="form.notify_main_teacher"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="notify-main-teacher" class="ml-2 block text-sm text-gray-900">
            Notifier le professeur principal
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="auto-create-intervention"
            v-model="form.auto_create_intervention"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="auto-create-intervention" class="ml-2 block text-sm text-gray-900">
            Créer automatiquement un plan d'intervention
          </label>
        </div>
      </div>
    </div>

    <!-- Footer buttons -->
    <div class="flex justify-end space-x-3 pt-6 border-t">
      <BaseButton
        variant="secondary"
        @click="$emit('cancel')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        variant="primary"
        type="submit"
        :loading="isLoading"
        :disabled="!isFormValid"
      >
        {{ isEditing ? 'Mettre à jour' : 'Créer' }}
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

interface Props {
  config?: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [config: any]
  cancel: []
}>()

// State
const isLoading = ref(false)
const errors = ref<Record<string, string>>({})

const form = ref({
  name: '',
  description: '',
  alert_type: '',
  priority: '',
  risk_level_threshold: '',
  risk_score_threshold: null as number | null,
  cooldown_days: 7,
  is_active: true,
  message_template: '',
  notify_student: false,
  notify_parents: true,
  notify_main_teacher: true,
  auto_create_intervention: false
})

// Computed
const isEditing = computed(() => !!props.config)

const isFormValid = computed(() => {
  return form.value.name.trim() !== '' &&
         form.value.alert_type !== '' &&
         form.value.priority !== '' &&
         form.value.cooldown_days > 0 &&
         form.value.message_template.trim() !== ''
})

// Methods
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.name.trim()) {
    errors.value.name = 'Le nom est requis'
  }
  
  if (!form.value.alert_type) {
    errors.value.alert_type = 'Le type d\'alerte est requis'
  }
  
  if (!form.value.priority) {
    errors.value.priority = 'La priorité est requise'
  }
  
  if (!form.value.message_template.trim()) {
    errors.value.message_template = 'Le modèle de message est requis'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  // Clean form data
  const configData = {
    ...form.value,
    risk_score_threshold: form.value.risk_score_threshold || null,
    risk_level_threshold: form.value.risk_level_threshold || null
  }
  
  setTimeout(() => {
    emit('save', configData)
    isLoading.value = false
  }, 1000)
}

// Lifecycle
onMounted(() => {
  if (props.config) {
    // Pre-fill form with existing configuration
    Object.assign(form.value, {
      name: props.config.name || '',
      description: props.config.description || '',
      alert_type: props.config.alert_type || '',
      priority: props.config.priority || '',
      risk_level_threshold: props.config.risk_level_threshold || '',
      risk_score_threshold: props.config.risk_score_threshold || null,
      cooldown_days: props.config.cooldown_days || 7,
      is_active: props.config.is_active ?? true,
      message_template: props.config.message_template || '',
      notify_student: props.config.notify_student || false,
      notify_parents: props.config.notify_parents || true,
      notify_main_teacher: props.config.notify_main_teacher || true,
      auto_create_intervention: props.config.auto_create_intervention || false
    })
  }
})
</script>