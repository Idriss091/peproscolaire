<template>
  <div class="homework-view">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold text-gray-900">Devoirs</h1>
          <div class="flex space-x-2">
            <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
              {{ publishedHomework?.length || 0 }} publiés
            </span>
            <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
              {{ overdueHomework?.length || 0 }} en retard
            </span>
            <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
              {{ gradedSubmissions?.length || 0 }} notés
            </span>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Recherche -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un devoir..."
              class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          </div>
          
          <!-- Actions -->
          <button
            @click="showCreateModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            <PlusIcon class="h-5 w-5" />
            <span>Nouveau devoir</span>
          </button>
          
          <button
            @click="showAIAssistantModal = true"
            class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            <SparklesIcon class="h-5 w-5" />
            <span>Assistant IA</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Filtres et onglets -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab.key
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="ml-2 text-xs opacity-75">
              ({{ tab.count }})
            </span>
          </button>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Filtres -->
          <select
            v-model="statusFilter"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            <option value="draft">Brouillons</option>
            <option value="published">Publiés</option>
            <option value="archived">Archivés</option>
          </select>
          
          <select
            v-model="subjectFilter"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Toutes les matières</option>
            <option value="math">Mathématiques</option>
            <option value="french">Français</option>
            <option value="science">Sciences</option>
            <option value="history">Histoire</option>
          </select>
          
          <input
            v-model="dueDateFilter"
            type="date"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="flex-1 overflow-hidden">
      <!-- Vue des devoirs -->
      <div v-if="activeTab === 'homework'" class="h-full overflow-y-auto">
        <div v-if="loading.homework" class="p-8 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Chargement des devoirs...</p>
        </div>
        
        <div v-else-if="filteredHomework.length === 0" class="p-8 text-center">
          <BookOpenIcon class="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">Aucun devoir trouvé</h3>
          <p class="text-gray-500">Aucun devoir ne correspond à vos critères de recherche</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          <div
            v-for="homeworkItem in filteredHomework"
            :key="homeworkItem.id"
            @click="selectHomework(homeworkItem)"
            class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
          >
            <div class="flex items-start justify-between mb-4">
              <div>
                <h3 class="font-medium text-gray-900 mb-1">{{ homeworkItem.title }}</h3>
                <p class="text-sm text-gray-500">{{ homeworkItem.subject }} • {{ homeworkItem.class_group }}</p>
              </div>
              
              <div class="flex flex-col items-end space-y-2">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getHomeworkStatusColor(homeworkItem.status)
                  ]"
                >
                  {{ getHomeworkStatusLabel(homeworkItem.status) }}
                </span>
                
                <div v-if="isHomeworkOverdue(homeworkItem)" class="flex items-center text-red-600">
                  <ExclamationTriangleIcon class="h-4 w-4 mr-1" />
                  <span class="text-xs">En retard</span>
                </div>
              </div>
            </div>
            
            <p class="text-sm text-gray-600 mb-4 line-clamp-3">{{ homeworkItem.description }}</p>
            
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Date limite:</span>
                <span :class="['font-medium', isHomeworkOverdue(homeworkItem) ? 'text-red-600' : 'text-gray-900']">
                  {{ formatDate(homeworkItem.due_date) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Type:</span>
                <span class="font-medium">{{ homeworkItem.homework_type }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Rendus:</span>
                <span class="font-medium">
                  {{ homeworkItem.submission_count || 0 }} 
                  <span class="text-xs text-green-600">({{ homeworkItem.graded_count || 0 }} notés)</span>
                </span>
              </div>
              <div v-if="homeworkItem.estimated_duration" class="flex justify-between">
                <span class="text-gray-600">Durée estimée:</span>
                <span class="font-medium">{{ homeworkItem.estimated_duration }}min</span>
              </div>
            </div>
            
            <!-- Indicateurs et actions -->
            <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <div class="flex space-x-1">
                <span v-if="homeworkItem.is_graded" class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                  Noté
                </span>
                <span v-if="homeworkItem.ai_generated" class="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">
                  IA
                </span>
                <span v-if="homeworkItem.attachments?.length > 0" class="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                  {{ homeworkItem.attachments.length }} fichier(s)
                </span>
              </div>
              
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500">{{ getDaysUntilDue(homeworkItem) }} jours</span>
                <ChevronRightIcon class="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vue des rendus -->
      <div v-else-if="activeTab === 'submissions'" class="h-full overflow-y-auto">
        <div class="p-6">
          <!-- Filtres des rendus -->
          <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <select
                v-model="submissionStatusFilter"
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tous les statuts</option>
                <option value="draft">Brouillons</option>
                <option value="submitted">Soumis</option>
                <option value="graded">Notés</option>
                <option value="revision_requested">Révision demandée</option>
              </select>
              
              <select
                v-model="submissionHomeworkFilter"
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tous les devoirs</option>
                <option v-for="hw in homework" :key="hw.id" :value="hw.id">
                  {{ hw.title }}
                </option>
              </select>
              
              <input
                v-model="submissionStudentFilter"
                type="text"
                placeholder="Rechercher un élève..."
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
              
              <div class="flex space-x-2">
                <button
                  @click="bulkGradeMode = !bulkGradeMode"
                  :class="[
                    'px-4 py-2 rounded-lg text-sm flex items-center justify-center space-x-2',
                    bulkGradeMode 
                      ? 'bg-orange-600 text-white' 
                      : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                  ]"
                >
                  <span>{{ bulkGradeMode ? 'Annuler' : 'Notation en masse' }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Liste des rendus -->
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th v-if="bulkGradeMode" class="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        @change="toggleAllSubmissions"
                        class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Élève
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Devoir
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Note
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Soumis le
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="submission in filteredSubmissions" :key="submission.id" class="hover:bg-gray-50">
                    <td v-if="bulkGradeMode" class="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        :value="submission.id"
                        v-model="selectedSubmissions"
                        class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                          <span class="text-white text-xs">
                            {{ getStudentInitials(submission.student) }}
                          </span>
                        </div>
                        <div>
                          <div class="text-sm font-medium text-gray-900">
                            {{ submission.student.first_name }} {{ submission.student.last_name }}
                          </div>
                          <div class="text-sm text-gray-500">{{ submission.student.class_group }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ submission.homework_title }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          getSubmissionStatusColor(submission.status)
                        ]"
                      >
                        {{ getSubmissionStatusLabel(submission.status) }}
                      </span>
                      <span v-if="submission.is_late" class="ml-2 text-xs text-red-600">(Retard)</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div v-if="submission.points_earned !== null" class="text-sm">
                        <span class="font-medium">{{ submission.points_earned }}</span>
                        <span class="text-gray-500">/ {{ submission.points_max }}</span>
                      </div>
                      <span v-else class="text-sm text-gray-400">Non noté</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDateTime(submission.submitted_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center space-x-2">
                        <button
                          @click="viewSubmission(submission)"
                          class="text-blue-600 hover:text-blue-900"
                        >
                          <EyeIcon class="h-4 w-4" />
                        </button>
                        <button
                          v-if="submission.status === 'submitted'"
                          @click="gradeSubmission(submission)"
                          class="text-green-600 hover:text-green-900"
                        >
                          <PencilIcon class="h-4 w-4" />
                        </button>
                        <button
                          v-if="submission.attachments?.length > 0"
                          @click="downloadSubmissionFiles(submission)"
                          class="text-purple-600 hover:text-purple-900"
                        >
                          <ArrowDownTrayIcon class="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- Actions de notation en masse -->
          <div v-if="bulkGradeMode && selectedSubmissions.length > 0" 
               class="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <div class="flex items-center justify-between">
              <span class="text-sm text-orange-800">
                {{ selectedSubmissions.length }} rendu(s) sélectionné(s)
              </span>
              <div class="flex items-center space-x-3">
                <input
                  v-model="bulkGradePoints"
                  type="number"
                  placeholder="Note"
                  class="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                />
                <button
                  @click="applyBulkGrade"
                  class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded text-sm"
                >
                  Appliquer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vue calendrier -->
      <div v-else-if="activeTab === 'calendar'" class="h-full overflow-y-auto p-6">
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Calendrier des devoirs</h3>
          <p class="text-gray-500">Vue calendrier à implémenter</p>
        </div>
      </div>

      <!-- Vue statistiques -->
      <div v-else-if="activeTab === 'stats'" class="h-full overflow-y-auto p-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <!-- Cartes statistiques -->
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Total Devoirs</p>
                <p class="text-3xl font-bold text-gray-900">{{ homework?.length || 0 }}</p>
              </div>
              <div class="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <BookOpenIcon class="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">En retard</p>
                <p class="text-3xl font-bold text-red-600">{{ overdueHomework?.length || 0 }}</p>
              </div>
              <div class="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Rendus notés</p>
                <p class="text-3xl font-bold text-green-600">{{ gradedSubmissions?.length || 0 }}</p>
              </div>
              <div class="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircleIcon class="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Note moyenne</p>
                <p class="text-3xl font-bold text-purple-600">{{ averageGrade || '0' }}/20</p>
              </div>
              <div class="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <TrophyIcon class="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Graphiques et rapports -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Répartition par statut</h3>
            <div class="space-y-3">
              <div v-for="(count, status) in homeworkByStatus" :key="status" class="flex items-center justify-between">
                <span class="text-sm text-gray-600 capitalize">{{ status }}</span>
                <span class="text-sm font-medium">{{ count }}</span>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Actions rapides</h3>
            <div class="space-y-3">
              <button
                @click="exportHomework"
                class="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <h4 class="font-medium text-gray-900">Exporter les devoirs</h4>
                <p class="text-sm text-gray-500">Générer un rapport Excel</p>
              </button>
              
              <button
                @click="getUpcomingDeadlines"
                class="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <h4 class="font-medium text-gray-900">Échéances à venir</h4>
                <p class="text-sm text-gray-500">Voir les prochaines dates limites</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal détail devoir -->
    <div v-if="showDetailModal && currentHomework" 
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium">{{ currentHomework.title }}</h3>
          <button @click="showDetailModal = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <!-- Contenu du devoir détaillé -->
          <div class="p-6">
            <h3 class="text-lg font-medium">Détails du devoir</h3>
            <p class="text-gray-600 mt-2">Composant en cours de développement...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal assistant IA -->
    <div v-if="showAIAssistantModal" 
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium">Assistant IA - Génération de devoir</h3>
          <button @click="showAIAssistantModal = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        
        <div class="p-6">
          <p class="text-gray-600">Assistant IA en cours de développement...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useHomeworkStore } from '@/stores/homework'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  SparklesIcon,
  BookOpenIcon,
  ExclamationTriangleIcon,
  ChevronRightIcon,
  EyeIcon,
  PencilIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  TrophyIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

// Store
const homeworkStore = useHomeworkStore()

// État réactif - utilisons storeToRefs pour la réactivité

const {
  homeworks,
  submissions,
  loading,
  error,
  publishedHomework,
  draftHomework,
  archivedHomework,
  upcomingHomework,
  overdueHomework
} = storeToRefs(homeworkStore)

// Alias pour compatibilité
const homework = computed(() => homeworks.value || [])
const gradedSubmissions = computed(() => (submissions.value || []).filter(s => s.grade !== null))
const averageGrade = computed(() => {
  const graded = gradedSubmissions.value
  if (graded.length === 0) return 0
  const sum = graded.reduce((acc, s) => acc + (s.grade || 0), 0)
  return (sum / graded.length).toFixed(1)
})

// État local
const activeTab = ref('homework')
const searchQuery = ref('')
const statusFilter = ref('')
const subjectFilter = ref('')
const dueDateFilter = ref('')
const submissionStatusFilter = ref('')
const submissionHomeworkFilter = ref('')
const submissionStudentFilter = ref('')
const bulkGradeMode = ref(false)
const selectedSubmissions = ref<string[]>([])
const bulkGradePoints = ref<number>()
const showDetailModal = ref(false)
const showCreateModal = ref(false)
const showAIAssistantModal = ref(false)

// Onglets
const tabs = computed(() => [
  {
    key: 'homework',
    label: 'Devoirs',
    count: homework?.length || 0
  },
  {
    key: 'submissions',
    label: 'Rendus',
    count: submissions?.length || 0
  },
  {
    key: 'calendar',
    label: 'Calendrier',
    count: 0
  },
  {
    key: 'stats',
    label: 'Statistiques',
    count: 0
  }
])

// Filtrage des devoirs
const filteredHomework = computed(() => {
  let filtered = homework.value || []

  if (statusFilter.value) {
    filtered = filtered.filter(hw => hw.status === statusFilter.value)
  }

  if (subjectFilter.value) {
    filtered = filtered.filter(hw => hw.subject === subjectFilter.value)
  }

  if (dueDateFilter.value) {
    filtered = filtered.filter(hw => hw.due_date === dueDateFilter.value)
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(hw =>
      hw.title.toLowerCase().includes(query) ||
      hw.description.toLowerCase().includes(query) ||
      hw.subject.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Filtrage des rendus
const filteredSubmissions = computed(() => {
  let filtered = submissions.value || []

  if (submissionStatusFilter.value) {
    filtered = filtered.filter(sub => sub.status === submissionStatusFilter.value)
  }

  if (submissionHomeworkFilter.value) {
    filtered = filtered.filter(sub => sub.homework === submissionHomeworkFilter.value)
  }

  if (submissionStudentFilter.value.trim()) {
    const query = submissionStudentFilter.value.toLowerCase()
    filtered = filtered.filter(sub =>
      `${sub.student.first_name} ${sub.student.last_name}`.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Méthodes
const selectHomework = async (homeworkItem: any) => {
  await homeworkStore.fetchHomeworkItem(homeworkItem.id)
  await homeworkStore.fetchSubmissions(homeworkItem.id)
  showDetailModal.value = true
}

const viewSubmission = async (submission: any) => {
  await homeworkStore.fetchSubmission(submission.id)
  // Ouvrir modal de détail du rendu
}

const gradeSubmission = async (submission: any) => {
  // Ouvrir modal de notation
}

const downloadSubmissionFiles = async (submission: any) => {
  // Télécharger les fichiers du rendu
}

const toggleAllSubmissions = (event: Event) => {
  const checked = (event.target as HTMLInputElement).checked
  if (checked) {
    selectedSubmissions.value = filteredSubmissions.value.map(sub => sub.id)
  } else {
    selectedSubmissions.value = []
  }
}

const applyBulkGrade = async () => {
  if (!bulkGradePoints.value || selectedSubmissions.value.length === 0) return

  try {
    const gradeData = selectedSubmissions.value.map(id => ({
      submission_id: id,
      points_earned: bulkGradePoints.value!
    }))

    await homeworkStore.bulkGradeSubmissions(gradeData)
    selectedSubmissions.value = []
    bulkGradePoints.value = undefined
    bulkGradeMode.value = false
  } catch (error) {
    console.error('Erreur lors de la notation en masse:', error)
  }
}

const exportHomework = async () => {
  try {
    await homeworkStore.exportHomework()
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const getUpcomingDeadlines = async () => {
  try {
    await homeworkStore.getUpcomingDeadlines()
  } catch (error) {
    console.error('Erreur lors du chargement des échéances:', error)
  }
}

const handleAIGenerated = (generatedHomework: any) => {
  // Traiter le devoir généré par l'IA
  showAIAssistantModal.value = false
  // Ouvrir modal de création avec les données pré-remplies
}

// Utilitaires
const getStudentInitials = (student: any) => {
  return `${student.first_name[0]}${student.last_name[0]}`.toUpperCase()
}

const getHomeworkStatusColor = (status: string) => {
  const colors = {
    'draft': 'bg-gray-100 text-gray-800',
    'published': 'bg-green-100 text-green-800',
    'archived': 'bg-blue-100 text-blue-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getHomeworkStatusLabel = (status: string) => {
  const labels = {
    'draft': 'Brouillon',
    'published': 'Publié',
    'archived': 'Archivé'
  }
  return labels[status] || status
}

const getSubmissionStatusColor = (status: string) => {
  const colors = {
    'draft': 'bg-gray-100 text-gray-800',
    'submitted': 'bg-blue-100 text-blue-800',
    'graded': 'bg-green-100 text-green-800',
    'revision_requested': 'bg-yellow-100 text-yellow-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getSubmissionStatusLabel = (status: string) => {
  const labels = {
    'draft': 'Brouillon',
    'submitted': 'Soumis',
    'graded': 'Noté',
    'revision_requested': 'Révision demandée'
  }
  return labels[status] || status
}

const isHomeworkOverdue = (homeworkItem: any) => {
  return new Date(homeworkItem.due_date) < new Date()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const getDaysUntilDue = (homeworkItem: any) => {
  const today = new Date()
  const dueDate = new Date(homeworkItem.due_date)
  const diffTime = dueDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}


const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('fr-FR')
}

// Cycle de vie
onMounted(async () => {
  await homeworkStore.fetchHomework()
})
</script>

<style scoped>
.homework-view {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>