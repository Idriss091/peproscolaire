<template>
  <div class="space-y-6">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Code de la compétence -->
      <div>
        <label for="code" class="block text-sm font-medium text-gray-700 mb-1">
          Code de la compétence *
        </label>
        <BaseInput
          id="code"
          v-model="form.code"
          placeholder="Ex: N1.1, G2.3..."
          :error="errors.code"
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
          Description *
        </label>
        <textarea
          id="description"
          v-model="form.description"
          rows="3"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Description détaillée de la compétence..."
          required
        ></textarea>
        <p v-if="errors.description" class="mt-1 text-sm text-red-600">
          {{ errors.description }}
        </p>
      </div>

      <!-- Matière -->
      <div>
        <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">
          Matière *
        </label>
        <select
          id="subject"
          v-model="form.subject_id"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        >
          <option value="">Sélectionner une matière</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
        <p v-if="errors.subject_id" class="mt-1 text-sm text-red-600">
          {{ errors.subject_id }}
        </p>
      </div>

      <!-- Niveau et Domaine -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="level" class="block text-sm font-medium text-gray-700 mb-1">
            Niveau *
          </label>
          <select
            id="level"
            v-model="form.level"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          >
            <option value="">Sélectionner un niveau</option>
            <option value="6eme">6ème</option>
            <option value="5eme">5ème</option>
            <option value="4eme">4ème</option>
            <option value="3eme">3ème</option>
          </select>
          <p v-if="errors.level" class="mt-1 text-sm text-red-600">
            {{ errors.level }}
          </p>
        </div>

        <div>
          <label for="domain" class="block text-sm font-medium text-gray-700 mb-1">
            Domaine *
          </label>
          <select
            id="domain"
            v-model="form.domain"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          >
            <option value="">Sélectionner un domaine</option>
            <option value="nombres">Nombres et calculs</option>
            <option value="geometrie">Géométrie</option>
            <option value="mesures">Grandeurs et mesures</option>
            <option value="donnees">Organisation et gestion de données</option>
          </select>
          <p v-if="errors.domain" class="mt-1 text-sm text-red-600">
            {{ errors.domain }}
          </p>
        </div>
      </div>

      <!-- Critères d'évaluation -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Critères d'évaluation
        </label>
        <div class="space-y-2">
          <div
            v-for="(criterion, index) in form.criteria"
            :key="index"
            class="flex items-center space-x-2"
          >
            <BaseInput
              v-model="form.criteria[index]"
              placeholder="Critère d'évaluation..."
              class="flex-1"
            />
            <BaseButton
              type="button"
              variant="outline"
              size="sm"
              @click="removeCriterion(index)"
              :disabled="form.criteria.length <= 1"
            >
              Supprimer
            </BaseButton>
          </div>
          <BaseButton
            type="button"
            variant="secondary"
            size="sm"
            @click="addCriterion"
            class="flex items-center gap-2"
          >
            <PlusIcon class="w-4 h-4" />
            Ajouter un critère
          </BaseButton>
        </div>
      </div>

      <!-- Statut -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Statut
        </label>
        <div class="flex items-center space-x-4">
          <label class="flex items-center">
            <input
              type="radio"
              v-model="form.status"
              value="active"
              class="mr-2"
            />
            Active
          </label>
          <label class="flex items-center">
            <input
              type="radio"
              v-model="form.status"
              value="inactive"
              class="mr-2"
            />
            Inactive
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t">
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
          :disabled="loading"
        >
          <LoadingSpinner v-if="loading" class="w-4 h-4 mr-2" />
          Créer la compétence
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const emit = defineEmits(['close', 'saved'])

// État du formulaire
const loading = ref(false)
const form = reactive({
  code: '',
  description: '',
  subject_id: '',
  level: '',
  domain: '',
  criteria: [''],
  status: 'active'
})

const errors = ref<Record<string, string>>({})

// Données de référence
const subjects = ref([
  { id: '1', name: 'Mathématiques' },
  { id: '2', name: 'Français' },
  { id: '3', name: 'Sciences' },
  { id: '4', name: 'Histoire-Géographie' },
  { id: '5', name: 'Anglais' }
])

// Méthodes
const addCriterion = () => {
  form.criteria.push('')
}

const removeCriterion = (index: number) => {
  if (form.criteria.length > 1) {
    form.criteria.splice(index, 1)
  }
}

const validateForm = () => {
  errors.value = {}
  
  if (!form.code.trim()) {
    errors.value.code = 'Le code est requis'
  }
  
  if (!form.description.trim()) {
    errors.value.description = 'La description est requise'
  }
  
  if (!form.subject_id) {
    errors.value.subject_id = 'La matière est requise'
  }
  
  if (!form.level) {
    errors.value.level = 'Le niveau est requis'
  }
  
  if (!form.domain) {
    errors.value.domain = 'Le domaine est requis'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  try {
    // TODO: Appel API pour créer la compétence
    console.log('Création de la compétence:', form)
    
    // Simulation d'une requête API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la création:', error)
  } finally {
    loading.value = false
  }
}
</script>