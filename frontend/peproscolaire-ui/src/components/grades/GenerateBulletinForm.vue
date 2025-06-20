<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Classe *
        </label>
        <select
          v-model="form.class"
          @change="loadClassStudents"
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
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Année scolaire *
        </label>
        <select
          v-model="form.year"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner l'année</option>
          <option value="2023-2024">2023-2024</option>
          <option value="2024-2025">2024-2025</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Type de bulletin
        </label>
        <select
          v-model="form.type"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="standard">Standard</option>
          <option value="detailed">Détaillé</option>
          <option value="simplified">Simplifié</option>
        </select>
      </div>
    </div>

    <!-- Options de génération -->
    <div class="border-t pt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Options de génération</h4>
      
      <div class="space-y-4">
        <div class="flex items-center">
          <input
            id="include-absences"
            v-model="form.includeAbsences"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="include-absences" class="ml-2 block text-sm text-gray-900">
            Inclure les absences et retards
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="include-behavior"
            v-model="form.includeBehavior"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="include-behavior" class="ml-2 block text-sm text-gray-900">
            Inclure les observations de comportement
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="include-competences"
            v-model="form.includeCompetences"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="include-competences" class="ml-2 block text-sm text-gray-900">
            Inclure l'évaluation des compétences
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="auto-publish"
            v-model="form.autoPublish"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="auto-publish" class="ml-2 block text-sm text-gray-900">
            Publier automatiquement après génération
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
            Envoyer une notification aux parents
          </label>
        </div>
      </div>
    </div>

    <!-- Sélection des élèves -->
    <div v-if="classStudents.length > 0" class="border-t pt-6">
      <div class="flex justify-between items-center mb-4">
        <h4 class="text-sm font-medium text-gray-900">Élèves à inclure</h4>
        <div class="flex gap-2">
          <BaseButton
            type="button"
            variant="outline"
            size="sm"
            @click="selectAllStudents"
          >
            Tout sélectionner
          </BaseButton>
          <BaseButton
            type="button"
            variant="outline"
            size="sm"
            @click="deselectAllStudents"
          >
            Tout désélectionner
          </BaseButton>
        </div>
      </div>
      
      <div class="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
        <div class="divide-y divide-gray-200">
          <div
            v-for="student in classStudents"
            :key="student.id"
            class="flex items-center justify-between p-3 hover:bg-gray-50"
          >
            <div class="flex items-center">
              <input
                :id="`student-${student.id}`"
                v-model="form.selectedStudents"
                :value="student.id"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label :for="`student-${student.id}`" class="ml-3 flex items-center cursor-pointer">
                <div class="flex-shrink-0 h-8 w-8">
                  <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <span class="text-xs font-medium text-gray-700">
                      {{ getStudentInitials(student.first_name, student.last_name) }}
                    </span>
                  </div>
                </div>
                <div class="ml-3">
                  <div class="text-sm font-medium text-gray-900">
                    {{ student.first_name }} {{ student.last_name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ student.student_number }}
                  </div>
                </div>
              </label>
            </div>
            
            <div class="text-xs text-gray-500">
              <div>Moyenne: {{ student.average || 'N/A' }}/20</div>
              <div>{{ student.absences_count || 0 }} absences</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-2 text-sm text-gray-600">
        {{ form.selectedStudents.length }}/{{ classStudents.length }} élèves sélectionnés
      </div>
    </div>

    <!-- Aperçu -->
    <div v-if="form.class && form.period" class="bg-gray-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Aperçu de la génération</h4>
      <div class="text-sm text-gray-600 space-y-1">
        <p><strong>Classe:</strong> {{ getClassName(form.class) }}</p>
        <p><strong>Période:</strong> {{ form.period }}</p>
        <p><strong>Année:</strong> {{ form.year }}</p>
        <p><strong>Type:</strong> {{ getTypeLabel(form.type) }}</p>
        <p><strong>Élèves:</strong> {{ form.selectedStudents.length }} bulletin(s) à générer</p>
      </div>
    </div>

    <!-- Avertissement -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">
            Attention
          </h3>
          <div class="mt-2 text-sm text-yellow-700">
            <p>
              La génération de bulletins peut prendre quelques minutes selon le nombre d'élèves.
              Assurez-vous que toutes les notes de la période sont bien saisies.
            </p>
          </div>
        </div>
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
        :loading="generating"
        :disabled="!isFormValid"
      >
        Générer {{ form.selectedStudents.length }} bulletin(s)
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const generating = ref(false)

// Formulaire
const form = reactive({
  class: '',
  period: '',
  year: '2024-2025',
  type: 'standard',
  includeAbsences: true,
  includeBehavior: true,
  includeCompetences: false,
  autoPublish: false,
  sendNotification: false,
  selectedStudents: [] as string[]
})

// Données
const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
])

const classStudents = ref<any[]>([])

// Computed
const isFormValid = computed(() => {
  return form.class && 
         form.period && 
         form.year && 
         form.selectedStudents.length > 0
})

// Méthodes
const loadClassStudents = async () => {
  try {
    // TODO: Charger les vrais élèves depuis l'API
    classStudents.value = [
      {
        id: '1',
        first_name: 'Marie',
        last_name: 'Dubois',
        student_number: '001',
        average: 15.2,
        absences_count: 2
      },
      {
        id: '2',
        first_name: 'Pierre',
        last_name: 'Martin',
        student_number: '002',
        average: 11.8,
        absences_count: 5
      },
      {
        id: '3',
        first_name: 'Sophie',
        last_name: 'Blanc',
        student_number: '003',
        average: 14.5,
        absences_count: 1
      }
    ]
    
    // Sélectionner tous les élèves par défaut
    form.selectedStudents = classStudents.value.map(s => s.id)
  } catch (error) {
    console.error('Erreur lors du chargement des élèves:', error)
  }
}

const selectAllStudents = () => {
  form.selectedStudents = classStudents.value.map(s => s.id)
}

const deselectAllStudents = () => {
  form.selectedStudents = []
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  generating.value = true
  try {
    const bulletinData = {
      class_id: form.class,
      period: form.period,
      academic_year: form.year,
      type: form.type,
      student_ids: form.selectedStudents,
      options: {
        include_absences: form.includeAbsences,
        include_behavior: form.includeBehavior,
        include_competences: form.includeCompetences,
        auto_publish: form.autoPublish,
        send_notification: form.sendNotification
      }
    }
    
    // TODO: Utiliser l'API pour générer les bulletins
    console.log('Générer les bulletins:', bulletinData)
    
    // Simulation de génération
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la génération des bulletins:', error)
  } finally {
    generating.value = false
  }
}

// Utilitaires
const getStudentInitials = (firstName: string, lastName: string) => {
  return (firstName[0] + lastName[0]).toUpperCase()
}

const getClassName = (classId: string) => {
  return classes.value.find(c => c.id === classId)?.name || ''
}

const getTypeLabel = (type: string) => {
  const labels = {
    standard: 'Standard',
    detailed: 'Détaillé',
    simplified: 'Simplifié'
  }
  return labels[type as keyof typeof labels] || type
}
</script>