<template>
  <BaseCard>
    <template #header>
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-medium text-gray-900">
            Appel - {{ classInfo?.name }}
          </h3>
          <p class="text-sm text-gray-500">
            {{ formatDate(date) }} | {{ students.length }} élèves
          </p>
        </div>
        <div class="flex gap-2">
          <BaseButton
            variant="secondary"
            size="sm"
            @click="markAllPresent"
          >
            Tous présents
          </BaseButton>
          <BaseButton
            variant="primary"
            size="sm"
            @click="saveAttendance"
            :loading="saving"
            :disabled="!hasChanges"
          >
            Enregistrer
          </BaseButton>
        </div>
      </div>
    </template>

    <div class="space-y-4">
      <!-- Filtres rapides -->
      <div class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">Filtrer :</span>
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="filterStatus = filterStatus === status.value ? '' : status.value"
            class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
            :class="filterStatus === status.value 
              ? 'bg-blue-100 text-blue-800 border border-blue-300'
              : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'"
          >
            {{ status.label }} ({{ getCountByStatus(status.value) }})
          </button>
        </div>
        
        <div class="ml-auto">
          <BaseInput
            v-model="searchTerm"
            placeholder="Rechercher un élève..."
            size="sm"
            class="w-64"
          />
        </div>
      </div>

      <!-- Liste des élèves -->
      <div class="space-y-2">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
          :class="{
            'border-green-200 bg-green-50': attendance[student.id]?.status === 'present',
            'border-red-200 bg-red-50': attendance[student.id]?.status === 'absent',
            'border-yellow-200 bg-yellow-50': attendance[student.id]?.status === 'late',
            'border-blue-200 bg-blue-50': attendance[student.id]?.status === 'excused'
          }"
        >
          <!-- Informations élève -->
          <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                <span class="text-sm font-medium text-gray-700">
                  {{ getStudentInitials(student) }}
                </span>
              </div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900">
                {{ student.first_name }} {{ student.last_name }}
              </div>
              <div class="text-sm text-gray-500">
                N° {{ student.student_number || student.id }}
              </div>
            </div>
          </div>

          <!-- Statut et actions -->
          <div class="flex items-center space-x-4">
            <!-- Heure d'arrivée pour les retards -->
            <div
              v-if="attendance[student.id]?.status === 'late'"
              class="text-sm text-gray-600"
            >
              <input
                v-model="attendance[student.id].arrival_time"
                type="time"
                class="text-sm border-gray-300 rounded focus:border-blue-500 focus:ring-blue-500"
                placeholder="Heure d'arrivée"
              >
            </div>

            <!-- Boutons de statut -->
            <div class="flex space-x-1">
              <button
                v-for="status in statusOptions"
                :key="status.value"
                @click="setAttendanceStatus(student.id, status.value)"
                class="px-3 py-1 rounded-md text-xs font-medium transition-colors"
                :class="attendance[student.id]?.status === status.value
                  ? `${status.activeClass} ring-2 ring-offset-1 ${status.ringClass}`
                  : `${status.inactiveClass} hover:${status.hoverClass}`"
              >
                {{ status.label }}
              </button>
            </div>

            <!-- Commentaire -->
            <div>
              <button
                @click="showCommentModal(student.id)"
                class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                :class="{ 'text-blue-600': attendance[student.id]?.notes }"
              >
                <ChatBubbleLeftEllipsisIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Résumé -->
      <div class="mt-6 p-4 bg-gray-50 rounded-lg">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">
              {{ getCountByStatus('present') }}
            </div>
            <div class="text-sm text-gray-600">Présents</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-red-600">
              {{ getCountByStatus('absent') }}
            </div>
            <div class="text-sm text-gray-600">Absents</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-yellow-600">
              {{ getCountByStatus('late') }}
            </div>
            <div class="text-sm text-gray-600">Retards</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">
              {{ getCountByStatus('excused') }}
            </div>
            <div class="text-sm text-gray-600">Excusés</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de commentaire -->
    <BaseModal
      :is-open="!!selectedStudentForComment"
      title="Ajouter un commentaire"
      @close="selectedStudentForComment = null"
    >
      <div v-if="selectedStudentForComment" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Élève
          </label>
          <p class="text-sm text-gray-900">
            {{ getStudentById(selectedStudentForComment)?.first_name }} 
            {{ getStudentById(selectedStudentForComment)?.last_name }}
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Commentaire
          </label>
          <textarea
            v-model="commentText"
            rows="3"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Ajouter une note concernant cet élève..."
          />
        </div>
        
        <div class="flex justify-end space-x-3">
          <BaseButton
            variant="secondary"
            @click="selectedStudentForComment = null"
          >
            Annuler
          </BaseButton>
          <BaseButton
            variant="primary"
            @click="saveComment"
          >
            Enregistrer
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ChatBubbleLeftEllipsisIcon } from '@heroicons/vue/24/outline'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import type { User, Class } from '@/types'

interface AttendanceRecord {
  status: 'present' | 'absent' | 'late' | 'excused'
  arrival_time?: string
  notes?: string
}

interface Props {
  students: User[]
  classInfo?: Class
  date: string
  existingAttendance?: Record<string, AttendanceRecord>
}

const props = withDefaults(defineProps<Props>(), {
  existingAttendance: () => ({})
})

const emit = defineEmits<{
  save: [attendance: Record<string, AttendanceRecord>]
}>()

// État local
const attendance = reactive<Record<string, AttendanceRecord>>({})
const filterStatus = ref('')
const searchTerm = ref('')
const selectedStudentForComment = ref<string | null>(null)
const commentText = ref('')
const saving = ref(false)

// Configuration des statuts
const statusOptions = [
  {
    value: 'present',
    label: 'Présent',
    activeClass: 'bg-green-100 text-green-800',
    inactiveClass: 'bg-gray-100 text-gray-700',
    hoverClass: 'bg-green-50',
    ringClass: 'ring-green-500'
  },
  {
    value: 'absent',
    label: 'Absent',
    activeClass: 'bg-red-100 text-red-800',
    inactiveClass: 'bg-gray-100 text-gray-700',
    hoverClass: 'bg-red-50',
    ringClass: 'ring-red-500'
  },
  {
    value: 'late',
    label: 'Retard',
    activeClass: 'bg-yellow-100 text-yellow-800',
    inactiveClass: 'bg-gray-100 text-gray-700',
    hoverClass: 'bg-yellow-50',
    ringClass: 'ring-yellow-500'
  },
  {
    value: 'excused',
    label: 'Excusé',
    activeClass: 'bg-blue-100 text-blue-800',
    inactiveClass: 'bg-gray-100 text-gray-700',
    hoverClass: 'bg-blue-50',
    ringClass: 'ring-blue-500'
  }
]

const statusFilters = [
  { value: 'present', label: 'Présents' },
  { value: 'absent', label: 'Absents' },
  { value: 'late', label: 'Retards' },
  { value: 'excused', label: 'Excusés' }
]

// Computed
const filteredStudents = computed(() => {
  let filtered = props.students

  // Filtrer par statut
  if (filterStatus.value) {
    filtered = filtered.filter(student => 
      attendance[student.id]?.status === filterStatus.value
    )
  }

  // Filtrer par recherche
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(student => 
      `${student.first_name} ${student.last_name}`.toLowerCase().includes(term) ||
      student.student_number?.toString().includes(term)
    )
  }

  return filtered.sort((a, b) => 
    `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`)
  )
})

const hasChanges = computed(() => {
  return Object.keys(attendance).length > 0
})

// Méthodes
const setAttendanceStatus = (studentId: string, status: AttendanceRecord['status']) => {
  if (!attendance[studentId]) {
    attendance[studentId] = { status }
  } else {
    attendance[studentId].status = status
  }

  // Réinitialiser l'heure d'arrivée si ce n'est pas un retard
  if (status !== 'late') {
    delete attendance[studentId].arrival_time
  } else if (!attendance[studentId].arrival_time) {
    // Définir l'heure actuelle par défaut pour les retards
    const now = new Date()
    attendance[studentId].arrival_time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  }
}

const markAllPresent = () => {
  props.students.forEach(student => {
    setAttendanceStatus(student.id.toString(), 'present')
  })
}

const getCountByStatus = (status: string) => {
  return Object.values(attendance).filter(record => record.status === status).length
}

const getStudentInitials = (student: User) => {
  const firstName = student.first_name?.[0] || ''
  const lastName = student.last_name?.[0] || ''
  return (firstName + lastName).toUpperCase()
}

const getStudentById = (id: string) => {
  return props.students.find(s => s.id.toString() === id)
}

const showCommentModal = (studentId: string) => {
  selectedStudentForComment.value = studentId
  commentText.value = attendance[studentId]?.notes || ''
}

const saveComment = () => {
  if (selectedStudentForComment.value) {
    if (!attendance[selectedStudentForComment.value]) {
      attendance[selectedStudentForComment.value] = { status: 'present' }
    }
    attendance[selectedStudentForComment.value].notes = commentText.value
    selectedStudentForComment.value = null
    commentText.value = ''
  }
}

const saveAttendance = async () => {
  saving.value = true
  try {
    emit('save', { ...attendance })
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Initialiser avec les données existantes
watch(() => props.existingAttendance, (newData) => {
  Object.assign(attendance, newData)
}, { immediate: true })

// Initialiser tous les élèves comme présents par défaut
watch(() => props.students, (students) => {
  students.forEach(student => {
    if (!attendance[student.id]) {
      attendance[student.id] = { status: 'present' }
    }
  })
}, { immediate: true })
</script>