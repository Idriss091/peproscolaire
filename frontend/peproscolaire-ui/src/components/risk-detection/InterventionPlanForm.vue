<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Basic Information -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Informations générales</h3>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <BaseInput
          v-model="form.title"
          label="Titre du plan *"
          placeholder="Ex: Plan d'accompagnement - Jean Dupont"
          required
          :error="errors.title"
        />

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

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          v-model="form.description"
          rows="3"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          placeholder="Décrivez les raisons et objectifs de ce plan d'intervention..."
        />
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <BaseInput
          v-model="form.start_date"
          label="Date de début"
          type="date"
          :error="errors.start_date"
        />

        <BaseInput
          v-model="form.target_date"
          label="Date cible"
          type="date"
          :error="errors.target_date"
        />
      </div>
    </div>

    <!-- Student Selection -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Élève concerné</h3>
      
      <div v-if="!form.risk_profile_id" class="space-y-4">
        <BaseInput
          v-model="studentSearch"
          label="Rechercher un élève"
          placeholder="Tapez le nom de l'élève..."
          @input="searchStudents"
        >
          <template #prefix>
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </template>
        </BaseInput>

        <div v-if="searchResults.length > 0" class="border border-gray-200 rounded-md max-h-40 overflow-y-auto">
          <button
            v-for="student in searchResults"
            :key="student.id"
            type="button"
            class="w-full text-left px-4 py-2 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none border-b border-gray-100 last:border-b-0"
            @click="selectStudent(student)"
          >
            <div class="font-medium text-gray-900">
              {{ student.first_name }} {{ student.last_name }}
            </div>
            <div class="text-sm text-gray-500">
              {{ student.email }} - Score de risque: {{ student.risk_score || 'N/A' }}
            </div>
          </button>
        </div>
      </div>

      <div v-if="selectedStudent" class="flex items-center p-3 bg-blue-50 rounded-md">
        <UserIcon class="h-5 w-5 text-blue-600 mr-3" />
        <div class="flex-1">
          <div class="font-medium text-blue-900">
            {{ selectedStudent.first_name }} {{ selectedStudent.last_name }}
          </div>
          <div class="text-sm text-blue-600">
            {{ selectedStudent.email }}
            <span v-if="selectedStudent.risk_score" class="ml-2">
              • Score de risque: {{ Math.round(selectedStudent.risk_score) }}/100
            </span>
          </div>
        </div>
        <button
          type="button"
          @click="clearStudent"
          class="text-blue-600 hover:text-blue-800"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>
    </div>

    <!-- Objectives -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Objectifs</h3>
        <BaseButton
          type="button"
          variant="secondary"
          size="sm"
          @click="addObjective"
        >
          <PlusIcon class="h-4 w-4 mr-1" />
          Ajouter
        </BaseButton>
      </div>

      <div v-if="form.objectives.length === 0" class="text-center py-6 border-2 border-dashed border-gray-300 rounded-md">
        <DocumentTextIcon class="mx-auto h-8 w-8 text-gray-400" />
        <p class="mt-2 text-sm text-gray-500">Aucun objectif défini</p>
        <BaseButton
          type="button"
          variant="secondary"
          size="sm"
          class="mt-2"
          @click="addObjective"
        >
          Ajouter le premier objectif
        </BaseButton>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(objective, index) in form.objectives"
          :key="index"
          class="flex items-start space-x-3 p-3 border border-gray-200 rounded-md"
        >
          <div class="flex-1 space-y-2">
            <BaseInput
              v-model="objective.description"
              placeholder="Description de l'objectif..."
              required
            />
            <div class="grid grid-cols-2 gap-2">
              <BaseInput
                v-model="objective.target_date"
                type="date"
                placeholder="Date cible"
              />
              <select
                v-model="objective.priority"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="low">Priorité faible</option>
                <option value="normal">Priorité normale</option>
                <option value="high">Priorité haute</option>
              </select>
            </div>
          </div>
          <BaseButton
            type="button"
            variant="ghost"
            size="sm"
            @click="removeObjective(index)"
          >
            <TrashIcon class="h-4 w-4 text-red-500" />
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Actions à mettre en œuvre</h3>
        <BaseButton
          type="button"
          variant="secondary"
          size="sm"
          @click="addAction"
        >
          <PlusIcon class="h-4 w-4 mr-1" />
          Ajouter
        </BaseButton>
      </div>

      <div v-if="form.actions.length === 0" class="text-center py-6 border-2 border-dashed border-gray-300 rounded-md">
        <ClipboardDocumentListIcon class="mx-auto h-8 w-8 text-gray-400" />
        <p class="mt-2 text-sm text-gray-500">Aucune action définie</p>
        <BaseButton
          type="button"
          variant="secondary"
          size="sm"
          class="mt-2"
          @click="addAction"
        >
          Ajouter la première action
        </BaseButton>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(action, index) in form.actions"
          :key="index"
          class="flex items-start space-x-3 p-3 border border-gray-200 rounded-md"
        >
          <div class="flex-1 space-y-2">
            <BaseInput
              v-model="action.title"
              placeholder="Titre de l'action..."
              required
            />
            <textarea
              v-model="action.description"
              rows="2"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Description détaillée de l'action..."
            />
            <div class="grid grid-cols-3 gap-2">
              <BaseInput
                v-model="action.due_date"
                type="date"
                placeholder="Échéance"
              />
              <select
                v-model="action.priority"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="low">Priorité faible</option>
                <option value="normal">Priorité normale</option>
                <option value="high">Priorité haute</option>
              </select>
              <select
                v-model="action.status"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="pending">En attente</option>
                <option value="in_progress">En cours</option>
                <option value="completed">Terminée</option>
              </select>
            </div>
          </div>
          <BaseButton
            type="button"
            variant="ghost"
            size="sm"
            @click="removeAction(index)"
          >
            <TrashIcon class="h-4 w-4 text-red-500" />
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Participants -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Participants</h3>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Responsable principal
          </label>
          <select
            v-model="form.responsible_person_id"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="">Sélectionner un responsable...</option>
            <option
              v-for="staff in availableStaff"
              :key="staff.id"
              :value="staff.id"
            >
              {{ staff.first_name }} {{ staff.last_name }} - {{ staff.role }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Autres participants
          </label>
          <select
            multiple
            v-model="form.participant_ids"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option
              v-for="staff in availableStaff"
              :key="staff.id"
              :value="staff.id"
            >
              {{ staff.first_name }} {{ staff.last_name }} - {{ staff.role }}
            </option>
          </select>
          <p class="mt-1 text-xs text-gray-500">
            Maintenez Ctrl/Cmd pour sélectionner plusieurs participants
          </p>
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
        {{ isEditing ? 'Mettre à jour' : 'Créer le plan' }}
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  MagnifyingGlassIcon,
  UserIcon,
  XMarkIcon,
  PlusIcon,
  TrashIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon
} from '@heroicons/vue/24/outline'
import { debounce } from 'lodash-es'

interface Props {
  plan?: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [plan: any]
  cancel: []
}>()

// State
const isLoading = ref(false)
const errors = ref<Record<string, string>>({})
const studentSearch = ref('')
const searchResults = ref<any[]>([])
const selectedStudent = ref<any>(null)

const form = ref({
  title: '',
  description: '',
  priority: 'normal',
  start_date: '',
  target_date: '',
  risk_profile_id: '',
  responsible_person_id: '',
  participant_ids: [] as string[],
  objectives: [] as any[],
  actions: [] as any[]
})

// Mock data - À remplacer par de vraies données
const availableStaff = ref([
  { id: '1', first_name: 'Marie', last_name: 'Dubois', role: 'Professeur principal' },
  { id: '2', first_name: 'Jean', last_name: 'Martin', role: 'Conseiller d\'éducation' },
  { id: '3', first_name: 'Sophie', last_name: 'Leroy', role: 'Psychologue scolaire' },
  { id: '4', first_name: 'Pierre', last_name: 'Durand', role: 'Directeur' }
])

// Computed
const isEditing = computed(() => !!props.plan)

const isFormValid = computed(() => {
  return form.value.title.trim() !== '' &&
         form.value.priority !== '' &&
         form.value.risk_profile_id !== ''
})

// Methods
const searchStudents = debounce(async () => {
  if (studentSearch.value.length < 2) {
    searchResults.value = []
    return
  }

  // Mock search - À remplacer par une vraie recherche API
  const mockStudents = [
    {
      id: '1',
      first_name: 'Jean',
      last_name: 'Dupont',
      email: 'jean.dupont@example.com',
      risk_score: 75
    },
    {
      id: '2',
      first_name: 'Marie',
      last_name: 'Martin',
      email: 'marie.martin@example.com',
      risk_score: 82
    },
    {
      id: '3',
      first_name: 'Pierre',
      last_name: 'Durand',
      email: 'pierre.durand@example.com',
      risk_score: 65
    }
  ]

  searchResults.value = mockStudents.filter(student =>
    `${student.first_name} ${student.last_name}`.toLowerCase().includes(studentSearch.value.toLowerCase()) ||
    student.email.toLowerCase().includes(studentSearch.value.toLowerCase())
  )
}, 300)

const selectStudent = (student: any) => {
  selectedStudent.value = student
  form.value.risk_profile_id = student.id
  searchResults.value = []
  studentSearch.value = ''
}

const clearStudent = () => {
  selectedStudent.value = null
  form.value.risk_profile_id = ''
  studentSearch.value = ''
}

const addObjective = () => {
  form.value.objectives.push({
    description: '',
    target_date: '',
    priority: 'normal',
    status: 'pending'
  })
}

const removeObjective = (index: number) => {
  form.value.objectives.splice(index, 1)
}

const addAction = () => {
  form.value.actions.push({
    title: '',
    description: '',
    due_date: '',
    priority: 'normal',
    status: 'pending'
  })
}

const removeAction = (index: number) => {
  form.value.actions.splice(index, 1)
}

const validateForm = () => {
  errors.value = {}
  
  if (!form.value.title.trim()) {
    errors.value.title = 'Le titre est requis'
  }
  
  if (!form.value.risk_profile_id) {
    errors.value.risk_profile_id = 'Vous devez sélectionner un élève'
  }
  
  if (form.value.start_date && form.value.target_date) {
    if (new Date(form.value.start_date) > new Date(form.value.target_date)) {
      errors.value.target_date = 'La date cible doit être postérieure à la date de début'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  setTimeout(() => {
    emit('save', form.value)
    isLoading.value = false
  }, 1000)
}

// Lifecycle
onMounted(() => {
  if (props.plan) {
    // Pre-fill form with existing plan data
    Object.assign(form.value, {
      title: props.plan.title || '',
      description: props.plan.description || '',
      priority: props.plan.priority || 'normal',
      start_date: props.plan.start_date || '',
      target_date: props.plan.target_date || '',
      risk_profile_id: props.plan.risk_profile?.id || '',
      responsible_person_id: props.plan.responsible_person?.id || '',
      participant_ids: props.plan.participants?.map(p => p.id) || [],
      objectives: props.plan.objectives || [],
      actions: props.plan.actions || []
    })
    
    if (props.plan.risk_profile?.student) {
      selectedStudent.value = props.plan.risk_profile.student
    }
  }
})
</script>