<template>
  <div class="space-y-6">
    <div class="text-sm text-gray-600">
      Lancez une analyse de risque pour un élève spécifique ou une classe complète.
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Analysis type -->
      <div>
        <label class="text-base font-medium text-gray-900">Type d'analyse</label>
        <fieldset class="mt-4">
          <div class="space-y-4">
            <div class="flex items-center">
              <input
                id="student-analysis"
                v-model="form.type"
                value="student"
                type="radio"
                class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
              />
              <label for="student-analysis" class="ml-3 block text-sm font-medium text-gray-700">
                Élève spécifique
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="class-analysis"
                v-model="form.type"
                value="class"
                type="radio"
                class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
              />
              <label for="class-analysis" class="ml-3 block text-sm font-medium text-gray-700">
                Classe complète
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="bulk-analysis"
                v-model="form.type"
                value="bulk"
                type="radio"
                class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
              />
              <label for="bulk-analysis" class="ml-3 block text-sm font-medium text-gray-700">
                Analyse globale
              </label>
            </div>
          </div>
        </fieldset>
      </div>

      <!-- Student selection -->
      <div v-if="form.type === 'student'" class="space-y-4">
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
              {{ student.email }}
            </div>
          </button>
        </div>

        <div v-if="form.student_id" class="flex items-center p-3 bg-blue-50 rounded-md">
          <UserIcon class="h-5 w-5 text-blue-600 mr-3" />
          <div class="flex-1">
            <div class="font-medium text-blue-900">
              {{ selectedStudent?.first_name }} {{ selectedStudent?.last_name }}
            </div>
            <div class="text-sm text-blue-600">
              {{ selectedStudent?.email }}
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

      <!-- Class selection -->
      <div v-if="form.type === 'class'">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Sélectionner une classe
        </label>
        <select
          v-model="form.class_id"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="">Choisir une classe...</option>
          <option
            v-for="classItem in availableClasses"
            :key="classItem.id"
            :value="classItem.id"
          >
            {{ classItem.name }} - {{ classItem.level }}
          </option>
        </select>
      </div>

      <!-- Bulk analysis options -->
      <div v-if="form.type === 'bulk'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Type d'analyse globale
          </label>
          <select
            v-model="form.bulk_type"
            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="daily">Analyse quotidienne</option>
            <option value="patterns">Détection de patterns</option>
          </select>
        </div>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div class="flex">
            <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-yellow-800">
                Attention
              </h3>
              <div class="mt-1 text-sm text-yellow-700">
                L'analyse globale peut prendre plusieurs minutes selon le nombre d'élèves.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Force update option -->
      <div class="flex items-center">
        <input
          id="force-update"
          v-model="form.force_update"
          type="checkbox"
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label for="force-update" class="ml-2 block text-sm text-gray-900">
          Forcer la mise à jour (ignorer les analyses récentes)
        </label>
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
        :disabled="!isFormValid"
        @click="handleSubmit"
      >
        Lancer l'analyse
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import {
  MagnifyingGlassIcon,
  UserIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { debounce } from 'lodash-es'

const emit = defineEmits<{
  close: []
  'analysis-started': []
}>()

const riskStore = useRiskDetectionStore()

// State
const isLoading = ref(false)
const studentSearch = ref('')
const searchResults = ref<any[]>([])
const selectedStudent = ref<any>(null)

const form = ref({
  type: 'student',
  student_id: '',
  class_id: '',
  bulk_type: 'daily',
  force_update: false
})

// Mock data - À remplacer par des vraies données
const availableClasses = ref([
  { id: '1', name: '6ème A', level: 'Sixième' },
  { id: '2', name: '5ème B', level: 'Cinquième' },
  { id: '3', name: '4ème C', level: 'Quatrième' },
  { id: '4', name: '3ème D', level: 'Troisième' }
])

// Computed
const isFormValid = computed(() => {
  switch (form.value.type) {
    case 'student':
      return !!form.value.student_id
    case 'class':
      return !!form.value.class_id
    case 'bulk':
      return !!form.value.bulk_type
    default:
      return false
  }
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
      email: 'jean.dupont@example.com'
    },
    {
      id: '2',
      first_name: 'Marie',
      last_name: 'Martin',
      email: 'marie.martin@example.com'
    },
    {
      id: '3',
      first_name: 'Pierre',
      last_name: 'Durand',
      email: 'pierre.durand@example.com'
    }
  ]

  searchResults.value = mockStudents.filter(student =>
    `${student.first_name} ${student.last_name}`.toLowerCase().includes(studentSearch.value.toLowerCase()) ||
    student.email.toLowerCase().includes(studentSearch.value.toLowerCase())
  )
}, 300)

const selectStudent = (student: any) => {
  selectedStudent.value = student
  form.value.student_id = student.id
  searchResults.value = []
  studentSearch.value = ''
}

const clearStudent = () => {
  selectedStudent.value = null
  form.value.student_id = ''
  studentSearch.value = ''
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  isLoading.value = true

  try {
    let success = false

    if (form.value.type === 'bulk') {
      success = await riskStore.triggerAnalysis({
        type: form.value.bulk_type,
        force_update: form.value.force_update
      })
    } else {
      const analysisData: any = {
        force_update: form.value.force_update
      }

      if (form.value.type === 'student') {
        analysisData.student_id = form.value.student_id
      } else if (form.value.type === 'class') {
        analysisData.class_id = form.value.class_id
      }

      success = await riskStore.triggerAnalysis(analysisData)
    }

    if (success) {
      emit('analysis-started')
    }
  } finally {
    isLoading.value = false
  }
}
</script>