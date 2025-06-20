<template>
  <BaseModal
    :is-open="isOpen"
    :title="evaluation ? 'Modifier l\'évaluation' : 'Nouvelle évaluation'"
    size="lg"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Titre -->
        <div class="md:col-span-2">
          <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
            Titre de l'évaluation *
          </label>
          <BaseInput
            id="title"
            v-model="form.title"
            placeholder="Ex: Contrôle Chapitre 3 - Les fonctions"
            :error="errors.title"
            required
          />
        </div>

        <!-- Type d'évaluation -->
        <div>
          <label for="evaluation_type" class="block text-sm font-medium text-gray-700 mb-2">
            Type d'évaluation *
          </label>
          <select
            id="evaluation_type"
            v-model="form.evaluation_type"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :class="{ 'border-red-300': errors.evaluation_type }"
            required
          >
            <option value="">Sélectionner un type</option>
            <option 
              v-for="type in gradesStore.getActiveEvaluationTypes" 
              :key="type.id" 
              :value="type.id"
            >
              {{ type.name }} (coef. {{ type.coefficient }})
            </option>
          </select>
          <p v-if="errors.evaluation_type" class="mt-1 text-sm text-red-600">
            {{ errors.evaluation_type }}
          </p>
        </div>

        <!-- Matière -->
        <div>
          <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
            Matière *
          </label>
          <select
            id="subject"
            v-model="form.subject"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :class="{ 'border-red-300': errors.subject }"
            required
          >
            <option value="">Sélectionner une matière</option>
            <option 
              v-for="subject in subjects" 
              :key="subject.id" 
              :value="subject.id"
            >
              {{ subject.name }}
            </option>
          </select>
          <p v-if="errors.subject" class="mt-1 text-sm text-red-600">
            {{ errors.subject }}
          </p>
        </div>

        <!-- Classe -->
        <div>
          <label for="class_group" class="block text-sm font-medium text-gray-700 mb-2">
            Classe *
          </label>
          <select
            id="class_group"
            v-model="form.class_group"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :class="{ 'border-red-300': errors.class_group }"
            required
          >
            <option value="">Sélectionner une classe</option>
            <option 
              v-for="classItem in classes" 
              :key="classItem.id" 
              :value="classItem.id"
            >
              {{ classItem.name }} ({{ classItem.level_name }})
            </option>
          </select>
          <p v-if="errors.class_group" class="mt-1 text-sm text-red-600">
            {{ errors.class_group }}
          </p>
        </div>

        <!-- Date -->
        <div>
          <label for="date" class="block text-sm font-medium text-gray-700 mb-2">
            Date de l'évaluation *
          </label>
          <BaseInput
            id="date"
            v-model="form.date"
            type="date"
            :error="errors.date"
            required
          />
        </div>

        <!-- Note maximale -->
        <div>
          <label for="max_score" class="block text-sm font-medium text-gray-700 mb-2">
            Note maximale *
          </label>
          <BaseInput
            id="max_score"
            v-model.number="form.max_score"
            type="number"
            min="1"
            max="100"
            step="0.5"
            placeholder="20"
            :error="errors.max_score"
            required
          />
        </div>

        <!-- Coefficient -->
        <div>
          <label for="coefficient" class="block text-sm font-medium text-gray-700 mb-2">
            Coefficient *
          </label>
          <BaseInput
            id="coefficient"
            v-model.number="form.coefficient"
            type="number"
            min="0.1"
            max="10"
            step="0.1"
            placeholder="1"
            :error="errors.coefficient"
            required
          />
        </div>

        <!-- Statut de publication -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Statut
          </label>
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input
                v-model="form.is_published"
                type="radio"
                :value="false"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              >
              <span class="ml-2 text-sm text-gray-700">Brouillon</span>
            </label>
            <label class="flex items-center">
              <input
                v-model="form.is_published"
                type="radio"
                :value="true"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              >
              <span class="ml-2 text-sm text-gray-700">Publié</span>
            </label>
          </div>
        </div>

        <!-- Description -->
        <div class="md:col-span-2">
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Description optionnelle de l'évaluation..."
          ></textarea>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-6 border-t">
        <BaseButton
          type="button"
          variant="outline"
          @click="$emit('close')"
          :disabled="loading"
        >
          Annuler
        </BaseButton>
        
        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
        >
          {{ evaluation ? 'Mettre à jour' : 'Créer l\'évaluation' }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useGradesStore } from '@/stores/grades'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

import type { Evaluation, Subject, Class } from '@/types'

interface Props {
  isOpen: boolean
  evaluation?: Evaluation | null
}

interface Emits {
  (e: 'close'): void
  (e: 'saved', evaluation: Evaluation): void
}

const props = withDefaults(defineProps<Props>(), {
  evaluation: null
})

const emit = defineEmits<Emits>()

const gradesStore = useGradesStore()

// État local
const loading = ref(false)
const subjects = ref<Subject[]>([])
const classes = ref<Class[]>([])

// Formulaire
const form = reactive({
  title: '',
  description: '',
  evaluation_type: '',
  subject: '',
  class_group: '',
  date: '',
  max_score: 20,
  coefficient: 1,
  is_published: false
})

// Erreurs
const errors = ref<Record<string, string>>({})

// Initialiser le formulaire
const initializeForm = () => {
  if (props.evaluation) {
    Object.assign(form, {
      title: props.evaluation.title,
      description: props.evaluation.description || '',
      evaluation_type: props.evaluation.evaluation_type,
      subject: props.evaluation.subject,
      class_group: props.evaluation.class_group,
      date: props.evaluation.date,
      max_score: props.evaluation.max_score,
      coefficient: props.evaluation.coefficient,
      is_published: props.evaluation.is_published
    })
  } else {
    // Réinitialiser pour une nouvelle évaluation
    Object.assign(form, {
      title: '',
      description: '',
      evaluation_type: '',
      subject: '',
      class_group: '',
      date: '',
      max_score: 20,
      coefficient: 1,
      is_published: false
    })
  }
  errors.value = {}
}

// Validation
const validateForm = () => {
  errors.value = {}
  
  if (!form.title.trim()) {
    errors.value.title = 'Le titre est requis'
  }
  
  if (!form.evaluation_type) {
    errors.value.evaluation_type = 'Le type d\'évaluation est requis'
  }
  
  if (!form.subject) {
    errors.value.subject = 'La matière est requise'
  }
  
  if (!form.class_group) {
    errors.value.class_group = 'La classe est requise'
  }
  
  if (!form.date) {
    errors.value.date = 'La date est requise'
  }
  
  if (!form.max_score || form.max_score <= 0) {
    errors.value.max_score = 'La note maximale doit être supérieure à 0'
  }
  
  if (!form.coefficient || form.coefficient <= 0) {
    errors.value.coefficient = 'Le coefficient doit être supérieur à 0'
  }
  
  // Validation de la date (ne peut pas être dans le passé pour une nouvelle évaluation)
  if (!props.evaluation && form.date) {
    const evalDate = new Date(form.date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (evalDate < today) {
      errors.value.date = 'La date ne peut pas être dans le passé'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

// Soumission
const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    let savedEvaluation: Evaluation
    
    if (props.evaluation) {
      // Mise à jour
      savedEvaluation = await gradesStore.updateEvaluation(props.evaluation.id, form)
    } else {
      // Création
      savedEvaluation = await gradesStore.createEvaluation(form)
    }
    
    emit('saved', savedEvaluation)
  } catch (error: any) {
    console.error('Erreur lors de la sauvegarde:', error)
    
    // Traiter les erreurs de validation du serveur
    if (error.response?.data) {
      const serverErrors = error.response.data
      if (typeof serverErrors === 'object') {
        Object.assign(errors.value, serverErrors)
      }
    }
  } finally {
    loading.value = false
  }
}

// Charger les données nécessaires
const loadData = async () => {
  try {
    // Charger les matières et classes
    // Ces appels dépendent de l'implémentation des stores correspondants
    // subjects.value = await timetableStore.fetchSubjects()
    // classes.value = await schoolsStore.fetchClasses()
    
    // Pour l'instant, utiliser des données mock
    subjects.value = [
      { id: '1', name: 'Mathématiques', short_name: 'Math', is_active: true, created_at: '' },
      { id: '2', name: 'Français', short_name: 'Fr', is_active: true, created_at: '' },
      { id: '3', name: 'Histoire-Géographie', short_name: 'HG', is_active: true, created_at: '' }
    ]
    
    classes.value = [
      { id: '1', name: 'A', level_name: '6ème', school: '', academic_year: '', level: '', max_students: 30, created_at: '' },
      { id: '2', name: 'B', level_name: '6ème', school: '', academic_year: '', level: '', max_students: 30, created_at: '' },
      { id: '3', name: 'A', level_name: '5ème', school: '', academic_year: '', level: '', max_students: 30, created_at: '' }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error)
  }
}

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

watch(() => props.evaluation, () => {
  if (props.isOpen) {
    initializeForm()
  }
})

// Lifecycle
onMounted(() => {
  loadData()
})
</script>