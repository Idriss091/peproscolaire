<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Configuration de génération -->
    <div class="lg:col-span-2 space-y-6">
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Configuration de la génération</h3>
        </template>
        
        <form @submit.prevent="generateAppreciations" class="space-y-6">
          <!-- Sélection des élèves -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Sélection des élèves
            </label>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm text-gray-600 mb-1">Classe</label>
                <select
                  v-model="form.selectedClass"
                  @change="loadClassStudents"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                >
                  <option value="">Sélectionner une classe</option>
                  <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                    {{ cls.name }}
                  </option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm text-gray-600 mb-1">Matière</label>
                <select
                  v-model="form.selectedSubject"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                >
                  <option value="">Toutes les matières</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <!-- Liste des élèves -->
            <div v-if="classStudents.length > 0" class="border border-gray-200 rounded-lg">
              <div class="p-3 bg-gray-50 border-b flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">
                  Élèves ({{ form.selectedStudents.length }}/{{ classStudents.length }})
                </span>
                <div class="flex space-x-2">
                  <BaseButton
                    type="button"
                    variant="outline"
                    size="xs"
                    @click="selectAllStudents"
                  >
                    Tout sélectionner
                  </BaseButton>
                  <BaseButton
                    type="button"
                    variant="outline"
                    size="xs"
                    @click="deselectAllStudents"
                  >
                    Désélectionner
                  </BaseButton>
                </div>
              </div>
              
              <div class="max-h-64 overflow-y-auto">
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
                      class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
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
                          Moyenne: {{ student.average || 'N/A' }}/20
                        </div>
                      </div>
                    </label>
                  </div>
                  
                  <BaseBadge
                    :variant="getPerformanceColor(student.average)"
                    size="sm"
                  >
                    {{ getPerformanceLabel(student.average) }}
                  </BaseBadge>
                </div>
              </div>
            </div>
          </div>

          <!-- Type d'appréciation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Type d'appréciation
            </label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="type in appreciationTypes"
                :key="type.id"
                class="relative border rounded-lg p-4 cursor-pointer hover:bg-gray-50"
                :class="form.appreciationType === type.id 
                  ? 'border-purple-500 bg-purple-50' 
                  : 'border-gray-200'"
                @click="form.appreciationType = type.id"
              >
                <div class="flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      :id="type.id"
                      v-model="form.appreciationType"
                      :value="type.id"
                      type="radio"
                      class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                    >
                  </div>
                  <div class="ml-3">
                    <label :for="type.id" class="font-medium text-sm text-gray-900 cursor-pointer">
                      {{ type.name }}
                    </label>
                    <p class="text-xs text-gray-600 mt-1">{{ type.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Période et contexte -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Période
              </label>
              <select
                v-model="form.period"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              >
                <option value="T1">Trimestre 1</option>
                <option value="T2">Trimestre 2</option>
                <option value="T3">Trimestre 3</option>
                <option value="semester1">Semestre 1</option>
                <option value="semester2">Semestre 2</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Ton de l'appréciation
              </label>
              <select
                v-model="form.tone"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              >
                <option value="encouraging">Encourageant</option>
                <option value="neutral">Neutre</option>
                <option value="constructive">Constructif</option>
                <option value="motivational">Motivant</option>
              </select>
            </div>
          </div>

          <!-- Options avancées -->
          <div class="border-t pt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-4">Options avancées</h4>
            
            <div class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex items-center">
                  <input
                    id="include-grades"
                    v-model="form.options.includeGrades"
                    type="checkbox"
                    class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  >
                  <label for="include-grades" class="ml-2 block text-sm text-gray-900">
                    Inclure les notes récentes
                  </label>
                </div>
                
                <div class="flex items-center">
                  <input
                    id="include-attendance"
                    v-model="form.options.includeAttendance"
                    type="checkbox"
                    class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  >
                  <label for="include-attendance" class="ml-2 block text-sm text-gray-900">
                    Considérer l'assiduité
                  </label>
                </div>
                
                <div class="flex items-center">
                  <input
                    id="include-behavior"
                    v-model="form.options.includeBehavior"
                    type="checkbox"
                    class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  >
                  <label for="include-behavior" class="ml-2 block text-sm text-gray-900">
                    Inclure le comportement
                  </label>
                </div>
                
                <div class="flex items-center">
                  <input
                    id="include-progress"
                    v-model="form.options.includeProgress"
                    type="checkbox"
                    class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  >
                  <label for="include-progress" class="ml-2 block text-sm text-gray-900">
                    Analyser les progrès
                  </label>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Longueur souhaitée
                </label>
                <select
                  v-model="form.options.length"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                >
                  <option value="short">Courte (50-80 mots)</option>
                  <option value="medium">Moyenne (80-120 mots)</option>
                  <option value="long">Détaillée (120-200 mots)</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Instructions supplémentaires (optionnel)
                </label>
                <textarea
                  v-model="form.customInstructions"
                  rows="3"
                  placeholder="Ex: Mettre l'accent sur les efforts fournis, mentionner les difficultés en géométrie..."
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t">
            <BaseButton
              type="button"
              variant="outline"
              @click="previewGeneration"
            >
              Aperçu
            </BaseButton>
            
            <BaseButton
              type="submit"
              variant="primary"
              :loading="generating"
              :disabled="!isFormValid"
            >
              <SparklesIcon class="w-4 h-4" />
              Générer {{ form.selectedStudents.length }} appréciation(s)
            </BaseButton>
          </div>
        </form>
      </BaseCard>
    </div>

    <!-- Aperçu et historique récent -->
    <div class="space-y-6">
      <!-- Aperçu de génération -->
      <BaseCard v-if="previewData">
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Aperçu</h3>
        </template>
        
        <div class="space-y-4">
          <div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h4 class="font-medium text-purple-900 mb-2">{{ previewData.student_name }}</h4>
            <p class="text-sm text-purple-800 leading-relaxed">{{ previewData.content }}</p>
          </div>
          
          <div class="flex justify-between text-xs text-gray-500">
            <span>{{ previewData.word_count }} mots</span>
            <span>Ton {{ previewData.tone }}</span>
          </div>
        </div>
      </BaseCard>

      <!-- Génération rapide -->
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Génération rapide</h3>
        </template>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Élève
            </label>
            <select
              v-model="quickForm.studentId"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
            >
              <option value="">Sélectionner un élève</option>
              <option v-for="student in allStudents" :key="student.id" :value="student.id">
                {{ student.first_name }} {{ student.last_name }} ({{ student.class_name }})
              </option>
            </select>
          </div>
          
          <BaseButton
            variant="primary"
            size="sm"
            :disabled="!quickForm.studentId"
            @click="quickGenerate"
            :loading="quickGenerating"
            class="w-full"
          >
            Génération express
          </BaseButton>
        </div>
      </BaseCard>

      <!-- Dernières générations -->
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Dernières générations</h3>
        </template>
        
        <div class="space-y-3">
          <div
            v-for="item in recentGenerations"
            :key="item.id"
            class="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="viewGeneration(item.id)"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-900">{{ item.student_name }}</span>
              <BaseBadge :variant="getStatusColor(item.status)" size="xs">
                {{ getStatusLabel(item.status) }}
              </BaseBadge>
            </div>
            <p class="text-xs text-gray-600 line-clamp-2">{{ item.preview }}</p>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-gray-500">{{ formatDateTime(item.created_at) }}</span>
              <div class="flex space-x-1">
                <BaseButton
                  variant="outline"
                  size="xs"
                  @click.stop="editGeneration(item.id)"
                >
                  Éditer
                </BaseButton>
                <BaseButton
                  variant="primary"
                  size="xs"
                  @click.stop="validateGeneration(item.id)"
                  v-if="item.status === 'draft'"
                >
                  Valider
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { SparklesIcon } from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'

// État local
const generating = ref(false)
const quickGenerating = ref(false)
const previewData = ref<any>(null)

// Formulaire principal
const form = reactive({
  selectedClass: '',
  selectedSubject: '',
  selectedStudents: [] as string[],
  appreciationType: 'bulletin',
  period: 'T1',
  tone: 'encouraging',
  customInstructions: '',
  options: {
    includeGrades: true,
    includeAttendance: true,
    includeBehavior: true,
    includeProgress: true,
    length: 'medium'
  }
})

// Formulaire rapide
const quickForm = reactive({
  studentId: ''
})

// Données
const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
])

const subjects = ref([
  { id: 'math', name: 'Mathématiques' },
  { id: 'french', name: 'Français' },
  { id: 'english', name: 'Anglais' },
  { id: 'history', name: 'Histoire-Géographie' }
])

const appreciationTypes = ref([
  {
    id: 'bulletin',
    name: 'Bulletin scolaire',
    description: 'Appréciation générale pour le bulletin trimestriel'
  },
  {
    id: 'subject',
    name: 'Matière spécifique',
    description: 'Appréciation ciblée sur une matière particulière'
  },
  {
    id: 'progress',
    name: 'Suivi de progrès',
    description: 'Commentaire sur l\'évolution de l\'élève'
  },
  {
    id: 'orientation',
    name: 'Conseil d\'orientation',
    description: 'Recommandations pour le parcours scolaire'
  }
])

const classStudents = ref<any[]>([])
const allStudents = ref<any[]>([])

const recentGenerations = ref([
  {
    id: '1',
    student_name: 'Marie Dubois',
    preview: 'Marie fait preuve d\'un excellent engagement dans son travail. Ses résultats sont très satisfaisants...',
    status: 'validated',
    created_at: '2024-01-15T10:30:00'
  },
  {
    id: '2',
    student_name: 'Pierre Martin',
    preview: 'Pierre montre des efforts constants en mathématiques. Il gagnerait à être plus régulier...',
    status: 'draft',
    created_at: '2024-01-15T09:15:00'
  }
])

// Computed
const isFormValid = computed(() => {
  return form.selectedStudents.length > 0 && 
         form.appreciationType && 
         form.period
})

// Méthodes
const loadClassStudents = async () => {
  if (!form.selectedClass) return
  
  try {
    // TODO: Charger les élèves depuis l'API
    classStudents.value = [
      {
        id: '1',
        first_name: 'Marie',
        last_name: 'Dubois',
        average: 15.2
      },
      {
        id: '2',
        first_name: 'Pierre',
        last_name: 'Martin',
        average: 11.8
      },
      {
        id: '3',
        first_name: 'Sophie',
        last_name: 'Blanc',
        average: 14.5
      }
    ]
    
    // Sélectionner tous par défaut
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

const previewGeneration = async () => {
  if (!isFormValid.value) return
  
  try {
    const sampleStudent = classStudents.value.find(s => form.selectedStudents.includes(s.id))
    if (sampleStudent && form.selectedSubject) {
      // Générer un aperçu avec l'API réelle
      const options: AppreciationOptions = {
        type: form.appreciationType as any,
        tone: mapToneToAPI(form.tone),
        length: form.options.length as any,
        focus_areas: getSelectedFocusAreas(),
        temperature: 0.7,
        max_tokens: getMaxTokensForLength(form.options.length)
      }
      
      const response = await aiStore.generateAppreciation(
        sampleStudent.id,
        form.selectedSubject,
        form.period,
        options
      )
      
      previewData.value = {
        student_name: `${sampleStudent.first_name} ${sampleStudent.last_name}`,
        content: response.appreciation.content,
        word_count: response.appreciation.content.split(' ').length,
        tone: form.tone,
        confidence: response.appreciation.confidence
      }
    }
  } catch (error) {
    console.error('Erreur lors de l\'aperçu:', error)
  }
}

const generateAppreciations = async () => {
  if (!isFormValid.value || !form.selectedSubject) return
  
  generating.value = true
  try {
    const options: AppreciationOptions = {
      type: form.appreciationType as any,
      tone: mapToneToAPI(form.tone),
      length: form.options.length as any,
      focus_areas: getSelectedFocusAreas(),
      temperature: 0.7,
      max_tokens: getMaxTokensForLength(form.options.length)
    }
    
    // Génération multiple via l'API réelle
    const response = await aiStore.generateMultipleAppreciations(
      form.selectedClass || undefined,
      form.selectedStudents.length > 0 ? form.selectedStudents : undefined,
      form.selectedSubject,
      form.period,
      options
    )
    
    console.log('Appréciations générées:', response)
    
    // Mettre à jour l'historique des générations
    updateRecentGenerations(response.results)
    
    // Réinitialiser le formulaire
    form.selectedStudents = []
    previewData.value = null
  } catch (error) {
    console.error('Erreur lors de la génération:', error)
  } finally {
    generating.value = false
  }
}

const quickGenerate = async () => {
  if (!quickForm.studentId) return
  
  quickGenerating.value = true
  try {
    // Génération rapide avec des paramètres par défaut
    const defaultOptions: AppreciationOptions = {
      type: 'bulletin',
      tone: 'bienveillant',
      length: 'standard',
      temperature: 0.7
    }
    
    const response = await aiStore.generateAppreciation(
      quickForm.studentId,
      form.selectedSubject || subjects.value[0]?.id || '',
      form.period,
      defaultOptions
    )
    
    console.log('Génération rapide réussie:', response)
    quickForm.studentId = ''
    
    // Ajouter à l'historique
    recentGenerations.value.unshift({
      id: Date.now().toString(),
      student_name: response.student.name,
      preview: response.appreciation.content.substring(0, 100) + '...',
      status: 'draft',
      created_at: new Date().toISOString()
    })
  } catch (error) {
    console.error('Erreur lors de la génération rapide:', error)
  } finally {
    quickGenerating.value = false
  }
}

const viewGeneration = (generationId: string) => {
  console.log('Voir génération:', generationId)
}

const editGeneration = (generationId: string) => {
  console.log('Éditer génération:', generationId)
}

const validateGeneration = (generationId: string) => {
  const generation = recentGenerations.value.find(g => g.id === generationId)
  if (generation) {
    generation.status = 'validated'
  }
}

// Utilitaires
const getStudentInitials = (firstName: string, lastName: string) => {
  return (firstName[0] + lastName[0]).toUpperCase()
}

const getPerformanceColor = (average: number) => {
  if (average >= 16) return 'success'
  if (average >= 14) return 'primary'
  if (average >= 12) return 'warning'
  if (average >= 10) return 'secondary'
  return 'danger'
}

const getPerformanceLabel = (average: number) => {
  if (average >= 16) return 'Excellent'
  if (average >= 14) return 'Bien'
  if (average >= 12) return 'Assez bien'
  if (average >= 10) return 'Passable'
  return 'Insuffisant'
}

const getStatusColor = (status: string) => {
  const colors = {
    draft: 'warning',
    validated: 'success',
    rejected: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: 'Brouillon',
    validated: 'Validé',
    rejected: 'Rejeté'
  }
  return labels[status as keyof typeof labels] || status
}

// Fonctions utilitaires pour l'API
const mapToneToAPI = (tone: string) => {
  const mapping = {
    encouraging: 'motivant',
    neutral: 'neutre',
    constructive: 'bienveillant',
    motivational: 'motivant'
  }
  return mapping[tone as keyof typeof mapping] || 'bienveillant'
}

const getSelectedFocusAreas = () => {
  const areas = []
  if (form.options.includeGrades) areas.push('notes')
  if (form.options.includeAttendance) areas.push('assiduité')
  if (form.options.includeBehavior) areas.push('comportement')
  if (form.options.includeProgress) areas.push('progrès')
  return areas
}

const getMaxTokensForLength = (length: string) => {
  const tokenLimits = {
    short: 100,
    medium: 150,
    long: 250
  }
  return tokenLimits[length as keyof typeof tokenLimits] || 150
}

const updateRecentGenerations = (results: any[]) => {
  results.forEach(result => {
    if (result.status === 'success' && result.appreciation) {
      recentGenerations.value.unshift({
        id: Date.now().toString() + Math.random(),
        student_name: result.student_name || 'Inconnue',
        preview: result.appreciation.content.substring(0, 100) + '...',
        status: 'draft',
        created_at: new Date().toISOString()
      })
    }
  })
  
  // Limiter à 50 éléments
  if (recentGenerations.value.length > 50) {
    recentGenerations.value = recentGenerations.value.slice(0, 50)
  }
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(async () => {
  try {
    // Charger les données initiales et l'historique des appréciations
    await aiStore.fetchModelStatus()
    
    // Charger l'historique des appréciations depuis le store
    recentGenerations.value = aiStore.appreciationHistory.map(item => ({
      id: item.id,
      student_name: item.student_name,
      preview: item.appreciation.content.substring(0, 100) + '...',
      status: 'validated', // Les appréciations de l'historique sont validées
      created_at: item.generated_at
    }))
    
    // TODO: Charger les classes, matières et élèves depuis l'API
    // Pour l'instant, on garde les données mock
    allStudents.value = [
      { id: '1', first_name: 'Marie', last_name: 'Dubois', class_name: '6ème A' },
      { id: '2', first_name: 'Pierre', last_name: 'Martin', class_name: '6ème A' },
      { id: '3', first_name: 'Sophie', last_name: 'Blanc', class_name: '6ème B' }
    ]
  } catch (error) {
    console.error('Erreur lors du chargement initial:', error)
  }
})
</script>