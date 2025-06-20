<template>
  <div class="student-records-view">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold text-gray-900">Dossiers Élèves</h1>
          <div class="flex space-x-2">
            <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
              {{ activeStudentRecords.length }} actifs
            </span>
            <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
              {{ documentsByStatus.pending }} en attente
            </span>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Recherche -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un élève..."
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
            <span>Nouveau dossier</span>
          </button>
          
          <button
            @click="showUploadModal = true"
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            <CloudArrowUpIcon class="h-5 w-5" />
            <span>Importer</span>
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
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
            <option value="transferred">Transférés</option>
            <option value="graduated">Diplômés</option>
          </select>
          
          <select
            v-model="academicYearFilter"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Toutes les années</option>
            <option value="2024-2025">2024-2025</option>
            <option value="2023-2024">2023-2024</option>
            <option value="2022-2023">2022-2023</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="flex-1 overflow-hidden">
      <!-- Vue des dossiers élèves -->
      <div v-if="activeTab === 'records'" class="h-full overflow-y-auto">
        <div v-if="loading.studentRecords" class="p-8 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Chargement des dossiers...</p>
        </div>
        
        <div v-else-if="filteredStudentRecords.length === 0" class="p-8 text-center">
          <FolderIcon class="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">Aucun dossier trouvé</h3>
          <p class="text-gray-500">Aucun dossier ne correspond à vos critères de recherche</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          <div
            v-for="record in filteredStudentRecords"
            :key="record.id"
            @click="selectStudentRecord(record)"
            class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="h-10 w-10 bg-blue-500 rounded-full flex items-center justify-center">
                  <span class="text-white font-medium text-sm">
                    {{ getStudentInitials(record.student) }}
                  </span>
                </div>
                <div>
                  <h3 class="font-medium text-gray-900">
                    {{ record.student.first_name }} {{ record.student.last_name }}
                  </h3>
                  <p class="text-sm text-gray-500">{{ record.class_group }}</p>
                </div>
              </div>
              
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  getStatusColor(record.status)
                ]"
              >
                {{ getStatusLabel(record.status) }}
              </span>
            </div>
            
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Année académique:</span>
                <span class="font-medium">{{ record.academic_year }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Date d'inscription:</span>
                <span class="font-medium">{{ formatDate(record.enrollment_date) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Documents:</span>
                <span class="font-medium">
                  {{ record.documents?.length || 0 }} 
                  <span class="text-xs text-green-600">({{ getApprovedDocsCount(record) }} approuvés)</span>
                </span>
              </div>
            </div>
            
            <!-- Indicateurs -->
            <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <div class="flex space-x-2">
                <div v-if="getExpiringDocsCount(record) > 0" class="flex items-center space-x-1 text-orange-600">
                  <ExclamationTriangleIcon class="h-4 w-4" />
                  <span class="text-xs">{{ getExpiringDocsCount(record) }} expirent</span>
                </div>
                <div v-if="getMissingDocsCount(record) > 0" class="flex items-center space-x-1 text-red-600">
                  <XCircleIcon class="h-4 w-4" />
                  <span class="text-xs">{{ getMissingDocsCount(record) }} manquants</span>
                </div>
              </div>
              
              <ChevronRightIcon class="h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      <!-- Vue des documents -->
      <div v-else-if="activeTab === 'documents'" class="h-full overflow-y-auto">
        <div class="p-6">
          <!-- Filtres documents -->
          <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <select
                v-model="documentStatusFilter"
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tous les statuts</option>
                <option value="pending">En attente</option>
                <option value="approved">Approuvés</option>
                <option value="rejected">Rejetés</option>
                <option value="expired">Expirés</option>
              </select>
              
              <select
                v-model="documentCategoryFilter"
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Toutes les catégories</option>
                <option v-for="category in documentCategories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
              
              <input
                v-model="documentSearchQuery"
                type="text"
                placeholder="Rechercher un document..."
                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
              
              <button
                @click="showDocumentUploadModal = true"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm flex items-center justify-center space-x-2"
              >
                <PlusIcon class="h-4 w-4" />
                <span>Ajouter</span>
              </button>
            </div>
          </div>
          
          <!-- Liste des documents -->
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Élève
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Catégorie
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date d'ajout
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="document in filteredDocuments" :key="document.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <DocumentIcon class="h-8 w-8 text-gray-400 mr-3" />
                        <div>
                          <div class="text-sm font-medium text-gray-900">{{ document.title }}</div>
                          <div v-if="document.description" class="text-sm text-gray-500">{{ document.description }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">
                        {{ document.student_record?.student?.first_name }} {{ document.student_record?.student?.last_name }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ document.category }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          getDocumentStatusColor(document.status)
                        ]"
                      >
                        {{ getDocumentStatusLabel(document.status) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(document.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center space-x-2">
                        <button
                          @click="downloadDocument(document.id, document.title)"
                          class="text-blue-600 hover:text-blue-900"
                        >
                          <ArrowDownTrayIcon class="h-4 w-4" />
                        </button>
                        <button
                          v-if="document.status === 'pending'"
                          @click="approveDocument(document.id)"
                          class="text-green-600 hover:text-green-900"
                        >
                          <CheckIcon class="h-4 w-4" />
                        </button>
                        <button
                          v-if="document.status === 'pending'"
                          @click="rejectDocument(document.id)"
                          class="text-red-600 hover:text-red-900"
                        >
                          <XMarkIcon class="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Vue statistiques -->
      <div v-else-if="activeTab === 'stats'" class="h-full overflow-y-auto p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <!-- Carte statistique -->
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Total Élèves</p>
                <p class="text-3xl font-bold text-gray-900">{{ studentRecords.length }}</p>
              </div>
              <div class="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <UsersIcon class="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Documents en attente</p>
                <p class="text-3xl font-bold text-orange-600">{{ documentsByStatus.pending }}</p>
              </div>
              <div class="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <ClockIcon class="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Documents expirés</p>
                <p class="text-3xl font-bold text-red-600">{{ expiredDocuments.length }}</p>
              </div>
              <div class="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Graphiques et rapports -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Rapports rapides</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              @click="generateClassReport"
              class="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <h4 class="font-medium text-gray-900">Rapport de classe</h4>
              <p class="text-sm text-gray-500">Générer un rapport complet pour une classe</p>
            </button>
            
            <button
              @click="exportDocuments"
              class="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <h4 class="font-medium text-gray-900">Export documents</h4>
              <p class="text-sm text-gray-500">Exporter la liste des documents</p>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal détail dossier élève -->
    <div v-if="showDetailModal && currentStudentRecord" 
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium">
            Dossier de {{ currentStudentRecord.student.first_name }} {{ currentStudentRecord.student.last_name }}
          </h3>
          <button @click="showDetailModal = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <!-- Contenu du dossier détaillé -->
          <StudentRecordDetail :student-record="currentStudentRecord" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStudentRecordsStore } from '@/stores/student-records'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  CloudArrowUpIcon,
  FolderIcon,
  DocumentIcon,
  UsersIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ChevronRightIcon,
  XCircleIcon,
  CheckIcon,
  XMarkIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

// Stores
const studentRecordsStore = useStudentRecordsStore()

// État réactif
const {
  studentRecords,
  currentStudentRecord,
  documents,
  documentCategories,
  loading,
  error,
  activeStudentRecords,
  documentsByStatus,
  expiredDocuments
} = studentRecordsStore

// État local
const activeTab = ref('records')
const searchQuery = ref('')
const statusFilter = ref('')
const academicYearFilter = ref('')
const documentStatusFilter = ref('')
const documentCategoryFilter = ref('')
const documentSearchQuery = ref('')
const showDetailModal = ref(false)
const showCreateModal = ref(false)
const showUploadModal = ref(false)
const showDocumentUploadModal = ref(false)

// Onglets
const tabs = computed(() => [
  {
    key: 'records',
    label: 'Dossiers',
    count: studentRecords.length
  },
  {
    key: 'documents',
    label: 'Documents',
    count: documents.length
  },
  {
    key: 'stats',
    label: 'Statistiques',
    count: 0
  }
])

// Filtrage des dossiers
const filteredStudentRecords = computed(() => {
  let filtered = studentRecords

  if (statusFilter.value) {
    filtered = filtered.filter(record => record.status === statusFilter.value)
  }

  if (academicYearFilter.value) {
    filtered = filtered.filter(record => record.academic_year === academicYearFilter.value)
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(record =>
      `${record.student.first_name} ${record.student.last_name}`.toLowerCase().includes(query) ||
      record.class_group.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Filtrage des documents
const filteredDocuments = computed(() => {
  let filtered = documents

  if (documentStatusFilter.value) {
    filtered = filtered.filter(doc => doc.status === documentStatusFilter.value)
  }

  if (documentCategoryFilter.value) {
    filtered = filtered.filter(doc => doc.category === documentCategoryFilter.value)
  }

  if (documentSearchQuery.value.trim()) {
    const query = documentSearchQuery.value.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(query) ||
      doc.description?.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Méthodes
const selectStudentRecord = async (record: any) => {
  await studentRecordsStore.fetchStudentRecord(record.id)
  showDetailModal.value = true
}

const approveDocument = async (documentId: string) => {
  try {
    await studentRecordsStore.approveDocument(documentId)
  } catch (error) {
    console.error('Erreur lors de l\'approbation:', error)
  }
}

const rejectDocument = async (documentId: string) => {
  try {
    await studentRecordsStore.rejectDocument(documentId, 'Document rejeté')
  } catch (error) {
    console.error('Erreur lors du rejet:', error)
  }
}

const downloadDocument = async (documentId: string, filename: string) => {
  try {
    await studentRecordsStore.downloadDocument(documentId, filename)
  } catch (error) {
    console.error('Erreur lors du téléchargement:', error)
  }
}

const generateClassReport = () => {
  // TODO: Implémenter la génération de rapport
  console.log('Génération du rapport de classe')
}

const exportDocuments = () => {
  // TODO: Implémenter l'export
  console.log('Export des documents')
}

// Utilitaires
const getStudentInitials = (student: any) => {
  return `${student.first_name[0]}${student.last_name[0]}`.toUpperCase()
}

const getStatusColor = (status: string) => {
  const colors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    transferred: 'bg-yellow-100 text-yellow-800',
    graduated: 'bg-blue-100 text-blue-800'
  }
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: 'Actif',
    inactive: 'Inactif',
    transferred: 'Transféré',
    graduated: 'Diplômé'
  }
  return labels[status as keyof typeof labels] || status
}

const getDocumentStatusColor = (status: string) => {
  return studentRecordsStore.getDocumentStatusColor(status)
}

const getDocumentStatusLabel = (status: string) => {
  return studentRecordsStore.getDocumentStatusLabel(status)
}

const getApprovedDocsCount = (record: any) => {
  return record.documents?.filter((doc: any) => doc.status === 'approved').length || 0
}

const getExpiringDocsCount = (record: any) => {
  if (!record.documents) return 0
  const now = new Date()
  const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  
  return record.documents.filter((doc: any) => {
    if (!doc.expiry_date) return false
    const expiryDate = new Date(doc.expiry_date)
    return expiryDate > now && expiryDate <= thirtyDaysFromNow
  }).length
}

const getMissingDocsCount = (record: any) => {
  // TODO: Calculer les documents manquants requis
  return 0
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR')
}

// Cycle de vie
onMounted(async () => {
  await studentRecordsStore.fetchStudentRecords()
  await studentRecordsStore.fetchDocuments()
  await studentRecordsStore.fetchDocumentCategories()
})
</script>

<style scoped>
.student-records-view {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}
</style>