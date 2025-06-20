<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nom de l'évaluation *
        </label>
        <BaseInput
          v-model="form.name"
          required
          placeholder="Ex: Contrôle Chapitre 1"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Matière *
        </label>
        <select
          v-model="form.subject"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une matière</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Classe *
        </label>
        <select
          v-model="form.class"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une classe</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Type d'évaluation *
        </label>
        <select
          v-model="form.type"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner un type</option>
          <option value="controle">Contrôle</option>
          <option value="devoir">Devoir</option>
          <option value="interrogation">Interrogation</option>
          <option value="examen">Examen</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Date *
        </label>
        <BaseInput
          v-model="form.date"
          type="date"
          required
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Note maximum *
        </label>
        <BaseInput
          v-model="form.maxValue"
          type="number"
          min="1"
          max="100"
          required
          placeholder="20"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Coefficient *
        </label>
        <BaseInput
          v-model="form.coefficient"
          type="number"
          min="0.5"
          max="10"
          step="0.5"
          required
          placeholder="1"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Durée
        </label>
        <BaseInput
          v-model="form.duration"
          placeholder="Ex: 1h, 45min"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Période *
        </label>
        <select
          v-model="form.period"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une période</option>
          <option value="T1">Trimestre 1</option>
          <option value="T2">Trimestre 2</option>
          <option value="T3">Trimestre 3</option>
        </select>
      </div>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Description
      </label>
      <textarea
        v-model="form.description"
        rows="3"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        placeholder="Description détaillée de l'évaluation..."
      />
    </div>
    
    <!-- Options avancées -->
    <div class="border-t pt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Options avancées</h4>
      
      <div class="space-y-4">
        <div class="flex items-center">
          <input
            id="is-published"
            v-model="form.isPublished"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="is-published" class="ml-2 block text-sm text-gray-900">
            Publier immédiatement aux élèves
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="send-notification"
            v-model="form.sendNotification"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="send-notification" class="ml-2 block text-sm text-gray-900">
            Envoyer une notification aux élèves
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="allow-retake"
            v-model="form.allowRetake"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="allow-retake" class="ml-2 block text-sm text-gray-900">
            Autoriser le rattrapage
          </label>
        </div>
      </div>
    </div>
    
    <!-- Aperçu -->
    <div class="bg-gray-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Aperçu</h4>
      <div class="text-sm text-gray-600">
        <p><strong>{{ form.name || 'Nom de l\'évaluation' }}</strong></p>
        <p>{{ getSubjectName(form.subject) }} - {{ getClassName(form.class) }}</p>
        <p>{{ formatDate(form.date) }} - Note sur {{ form.maxValue }}, coefficient {{ form.coefficient }}</p>
        <p v-if="form.description">{{ form.description }}</p>
      </div>
    </div>
    
    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
      <BaseButton
        type="button"
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        type="submit"
        variant="primary"
        :loading="saving"
        :disabled="!isFormValid"
      >
        Créer l'évaluation
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const saving = ref(false)

// Formulaire
const form = reactive({
  name: '',
  subject: '',
  class: '',
  type: '',
  date: '',
  maxValue: '20',
  coefficient: '1',
  duration: '',
  period: '',
  description: '',
  isPublished: false,
  sendNotification: false,
  allowRetake: false
})

// Données
const subjects = ref([
  { id: '1', name: 'Mathématiques' },
  { id: '2', name: 'Français' },
  { id: '3', name: 'Histoire-Géographie' },
  { id: '4', name: 'Sciences' }
])

const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
])

// Computed
const isFormValid = computed(() => {
  return form.name && 
         form.subject && 
         form.class && 
         form.type && 
         form.date && 
         form.maxValue && 
         form.coefficient &&
         form.period
})

// Méthodes
const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  try {
    const evaluationData = {
      name: form.name,
      description: form.description,
      subject_id: form.subject,
      class_id: form.class,
      type: form.type,
      date: form.date,
      max_value: parseInt(form.maxValue),
      coefficient: parseFloat(form.coefficient),
      duration: form.duration || null,
      period: form.period,
      is_published: form.isPublished,
      send_notification: form.sendNotification,
      allow_retake: form.allowRetake,
      teacher_id: authStore.user?.id,
      status: 'planned'
    }
    
    await gradesStore.addEvaluation(evaluationData)
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la création de l\'évaluation:', error)
  } finally {
    saving.value = false
  }
}

// Utilitaires
const getSubjectName = (subjectId: string) => {
  return subjects.value.find(s => s.id === subjectId)?.name || ''
}

const getClassName = (classId: string) => {
  return classes.value.find(c => c.id === classId)?.name || ''
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  // Définir la date par défaut (demain)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  form.date = tomorrow.toISOString().split('T')[0]
})
</script>