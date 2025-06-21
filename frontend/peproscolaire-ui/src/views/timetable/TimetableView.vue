<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Emploi du temps</h1>
        <p class="text-gray-600">Consultez votre emploi du temps hebdomadaire</p>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          variant="secondary"
          @click="exportSchedule"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter
        </BaseButton>
        
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showCreateModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Nouveau cours
        </BaseButton>
      </div>
    </div>

    <!-- Filtres et navigation -->
    <BaseCard>
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div class="flex items-center gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Semaine
            </label>
            <BaseInput
              v-model="currentWeek"
              type="week"
              @change="loadSchedule"
            />
          </div>
          
          <div v-if="authStore.hasPermission('teacher_access')">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Vue
            </label>
            <select
              v-model="viewMode"
              @change="loadSchedule"
              class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="teacher">Mon emploi du temps</option>
              <option value="class">Par classe</option>
              <option value="room">Par salle</option>
            </select>
          </div>
          
          <div v-if="viewMode !== 'teacher'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ viewMode === 'class' ? 'Classe' : 'Salle' }}
            </label>
            <select
              v-model="selectedEntity"
              @change="loadSchedule"
              class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Sélectionner...</option>
              <option 
                v-for="entity in entities" 
                :key="entity.id" 
                :value="entity.id"
              >
                {{ entity.name }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <BaseButton
            variant="outline"
            size="sm"
            @click="goToPreviousWeek"
            class="flex items-center gap-1"
          >
            <ChevronLeftIcon class="w-4 h-4" />
            Précédent
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="sm"
            @click="goToCurrentWeek"
          >
            Aujourd'hui
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="sm"
            @click="goToNextWeek"
            class="flex items-center gap-1"
          >
            Suivant
            <ChevronRightIcon class="w-4 h-4" />
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <!-- Emploi du temps -->
    <BaseCard>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement de l'emploi du temps...</p>
      </div>
      
      <div v-else-if="!schedule || schedule.length === 0" class="text-center py-8">
        <CalendarIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucun cours pour cette semaine</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <!-- Grille de l'emploi du temps -->
        <div class="min-w-full">
          <!-- En-tête des jours -->
          <div class="grid grid-cols-6 gap-px bg-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-50 p-3 text-center text-sm font-medium text-gray-500">
              Horaires
            </div>
            <div
              v-for="day in weekDays"
              :key="day.value"
              class="bg-gray-50 p-3 text-center text-sm font-medium text-gray-500"
              :class="{ 'bg-blue-50 text-blue-700': isToday(day.value) }"
            >
              <div>{{ day.label }}</div>
              <div class="text-xs">{{ formatDate(getDateForDay(day.value)) }}</div>
            </div>
          </div>
          
          <!-- Créneaux horaires -->
          <div class="mt-1 grid grid-cols-6 gap-px bg-gray-200">
            <div
              v-for="slot in timeSlots"
              :key="slot.id"
              class="col-span-6 grid grid-cols-6 gap-px"
            >
              <!-- Horaire -->
              <div class="bg-white p-3 text-center text-sm font-medium text-gray-700">
                <div>{{ formatTime(slot.start_time) }}</div>
                <div class="text-xs text-gray-500">{{ formatTime(slot.end_time) }}</div>
              </div>
              
              <!-- Cours pour chaque jour -->
              <div
                v-for="day in weekDays"
                :key="`${slot.id}-${day.value}`"
                class="bg-white p-2 min-h-[80px] relative"
              >
                <div
                  v-for="course in getCoursesForSlot(slot.id, day.value)"
                  :key="course.id"
                  class="absolute inset-1 rounded p-2 text-xs cursor-pointer hover:shadow-md transition-shadow"
                  :style="{ backgroundColor: course.subject_color || '#3B82F6', color: 'white' }"
                  @click="openCourseDetail(course)"
                >
                  <div class="font-medium truncate">{{ course.subject_name }}</div>
                  <div class="truncate opacity-90">{{ course.class_name }}</div>
                  <div class="truncate opacity-75">{{ course.room_name }}</div>
                  <div v-if="course.teacher_name" class="truncate opacity-75">
                    {{ course.teacher_name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Modal de détail du cours -->
    <BaseModal
      v-if="selectedCourse"
      :is-open="!!selectedCourse"
      :title="selectedCourse.subject_name"
      @close="selectedCourse = null"
    >
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Matière:</span>
            <p>{{ selectedCourse.subject_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Classe:</span>
            <p>{{ selectedCourse.class_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Salle:</span>
            <p>{{ selectedCourse.room_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Professeur:</span>
            <p>{{ selectedCourse.teacher_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Horaires:</span>
            <p>{{ formatTime(timetableStore.getTimeSlotById(selectedCourse.time_slot)?.start_time || '') }} - {{ formatTime(timetableStore.getTimeSlotById(selectedCourse.time_slot)?.end_time || '') }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Période:</span>
            <p>{{ formatDate(selectedCourse.start_date) }} - {{ formatDate(selectedCourse.end_date || '') }}</p>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 pt-4 border-t">
          <BaseButton
            variant="outline"
            @click="selectedCourse = null"
          >
            Fermer
          </BaseButton>
          
          <BaseButton
            v-if="authStore.hasPermission('teacher_access')"
            variant="primary"
            @click="editCourse(selectedCourse)"
          >
            Modifier
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  PlusIcon,
  DocumentArrowDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useTimetableStore } from '@/stores/timetable'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

import type { Schedule } from '@/types'

const authStore = useAuthStore()
const timetableStore = useTimetableStore()

// Utiliser storeToRefs pour la réactivité
const { schedules, timeSlots: storeTimeSlots } = storeToRefs(timetableStore)

// État local
const currentWeek = ref('')
const viewMode = ref('teacher')
const selectedEntity = ref('')
const entities = ref<any[]>([])
const selectedCourse = ref<Schedule | null>(null)
const showCreateModal = ref(false)
const isLoading = ref(false)

// Jours de la semaine
const weekDays = [
  { label: 'Lundi', value: 1 },
  { label: 'Mardi', value: 2 },
  { label: 'Mercredi', value: 3 },
  { label: 'Jeudi', value: 4 },
  { label: 'Vendredi', value: 5 }
]

// Computed
const loading = computed(() => isLoading.value)
const schedule = computed(() => schedules.value || [])
const timeSlots = computed(() => storeTimeSlots.value || [])

// Méthodes
const loadSchedule = async () => {
  isLoading.value = true
  
  try {
    const params: any = {}
    
    if (currentWeek.value) {
      params.week = currentWeek.value
    }
    
    if (viewMode.value === 'class' && selectedEntity.value) {
      params.class_group = selectedEntity.value
    } else if (viewMode.value === 'room' && selectedEntity.value) {
      params.room = selectedEntity.value
    } else if (viewMode.value === 'teacher' && authStore.user?.id) {
      params.teacher = authStore.user.id
    }
    
    await Promise.all([
      timetableStore.fetchSchedules(params),
      timetableStore.fetchTimeSlots()
    ])
  } finally {
    isLoading.value = false
  }
}

const getCoursesForSlot = (slotId: string, dayOfWeek: number) => {
  return timetableStore.getScheduleForSlot(dayOfWeek, slotId)
}

const openCourseDetail = (course: Schedule) => {
  selectedCourse.value = course
}

const editCourse = (course: Schedule) => {
  // TODO: Implémenter l'édition avec modal
  console.log('Éditer le cours:', course.id)
  selectedCourse.value = null
  showCreateModal.value = true
}

const exportSchedule = () => {
  // Créer et télécharger un fichier CSV
  const csvContent = generateScheduleCSV()
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `emploi-du-temps-${currentWeek.value || 'actuel'}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const generateScheduleCSV = () => {
  const headers = ['Jour', 'Heure', 'Matière', 'Professeur', 'Classe', 'Salle']
  const rows = [headers.join(',')]
  
  schedule.value.forEach(course => {
    const timeSlot = timetableStore.getTimeSlotById(course.time_slot)
    if (timeSlot) {
      const dayName = weekDays.find(d => d.value === timeSlot.day_of_week)?.label || ''
      const row = [
        dayName,
        `${formatTime(timeSlot.start_time)}-${formatTime(timeSlot.end_time)}`,
        course.subject_name || '',
        course.teacher_name || '',
        course.class_name || '',
        course.room_name || ''
      ]
      rows.push(row.join(','))
    }
  })
  
  return rows.join('\n')
}

const goToPreviousWeek = () => {
  const current = new Date(currentWeek.value)
  current.setDate(current.getDate() - 7)
  currentWeek.value = getWeekString(current)
  loadSchedule()
}

const goToCurrentWeek = () => {
  currentWeek.value = getWeekString(new Date())
  loadSchedule()
}

const goToNextWeek = () => {
  const current = new Date(currentWeek.value)
  current.setDate(current.getDate() + 7)
  currentWeek.value = getWeekString(current)
  loadSchedule()
}

// Utilitaires
const getWeekString = (date: Date) => {
  // Simplifié : utilisons juste l'année et la semaine de l'année
  const year = date.getFullYear()
  const startOfYear = new Date(year, 0, 1)
  const days = Math.floor((date.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000))
  const week = Math.ceil((days + startOfYear.getDay() + 1) / 7)
  return `${year}-W${week.toString().padStart(2, '0')}`
}

const getDateForDay = (dayOfWeek: number) => {
  // Simplifié : retournons la date d'aujourd'hui + offset
  const today = new Date()
  const currentDayOfWeek = today.getDay() || 7 // Lundi = 1, Dimanche = 7
  const daysToAdd = dayOfWeek - currentDayOfWeek
  const resultDate = new Date(today)
  resultDate.setDate(today.getDate() + daysToAdd)
  return resultDate
}

const isToday = (dayOfWeek: number) => {
  const today = new Date()
  const dayDate = getDateForDay(dayOfWeek)
  return today.toDateString() === dayDate.toDateString()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', { 
    day: 'numeric', 
    month: 'short' 
  })
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}

// Watchers
watch([viewMode, selectedEntity], () => {
  loadSchedule()
})

// Lifecycle
onMounted(async () => {
  currentWeek.value = getWeekString(new Date())
  
  // Charger les données initiales
  await Promise.all([
    timetableStore.fetchTimeSlots(),
    timetableStore.fetchSubjects(),
    timetableStore.fetchRooms()
  ])
  
  // Charger les entités selon le mode de vue
  if (viewMode.value === 'class') {
    // TODO: Charger les classes depuis le store schools
    entities.value = [
      { id: '1', name: '6ème A' },
      { id: '2', name: '6ème B' },
      { id: '3', name: '5ème A' }
    ]
  } else if (viewMode.value === 'room') {
    entities.value = timetableStore.rooms
  }
  
  loadSchedule()
})
</script>