<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <!-- En-tête du calendrier -->
    <div class="grid grid-cols-6 border-b border-gray-200">
      <div class="bg-gray-50 p-4 text-center border-r border-gray-200">
        <span class="text-sm font-medium text-gray-500">Horaires</span>
      </div>
      <div
        v-for="day in weekDays"
        :key="day.value"
        class="bg-gray-50 p-4 text-center border-r border-gray-200 last:border-r-0"
        :class="{ 'bg-blue-50': isToday(day.value) }"
      >
        <div class="text-sm font-medium" :class="{ 'text-blue-700': isToday(day.value) }">
          {{ day.label }}
        </div>
        <div class="text-xs text-gray-500 mt-1">
          {{ formatDateForDay(day.value) }}
        </div>
      </div>
    </div>

    <!-- Grille des créneaux -->
    <div class="divide-y divide-gray-200">
      <div
        v-for="timeSlot in timeSlots"
        :key="timeSlot.id"
        class="grid grid-cols-6 min-h-[80px]"
      >
        <!-- Colonne horaires -->
        <div class="bg-gray-50 p-3 border-r border-gray-200 flex flex-col justify-center text-center">
          <div class="text-sm font-medium text-gray-900">
            {{ formatTime(timeSlot.start_time) }}
          </div>
          <div class="text-xs text-gray-500">
            {{ formatTime(timeSlot.end_time) }}
          </div>
        </div>

        <!-- Colonnes des jours -->
        <div
          v-for="day in weekDays"
          :key="`${timeSlot.id}-${day.value}`"
          class="border-r border-gray-200 last:border-r-0 relative p-2 min-h-[80px]"
          :class="{ 'bg-blue-25': isToday(day.value) }"
        >
          <!-- Cours pour ce créneau -->
          <div
            v-for="(course, index) in getCoursesForSlot(timeSlot.id, day.value)"
            :key="course.id"
            class="absolute inset-2 rounded-lg p-2 text-white cursor-pointer hover:shadow-lg transition-all duration-200 transform hover:scale-105"
            :style="{ 
              backgroundColor: getCourseColor(course),
              zIndex: 10 + index,
              top: `${8 + index * 4}px`,
              left: `${8 + index * 4}px`,
              right: `${8 + index * 4}px`,
              bottom: `${8 + index * 4}px`
            }"
            @click="$emit('course-click', course)"
          >
            <div class="text-xs font-semibold truncate">
              {{ course.subject_name }}
            </div>
            <div class="text-xs opacity-90 truncate">
              {{ course.class_name }}
            </div>
            <div class="text-xs opacity-75 truncate">
              🏫 {{ course.room_name }}
            </div>
            <div v-if="course.teacher_name && viewMode !== 'teacher'" class="text-xs opacity-75 truncate">
              👨‍🏫 {{ course.teacher_name }}
            </div>
          </div>

          <!-- Slot vide -->
          <div
            v-if="getCoursesForSlot(timeSlot.id, day.value).length === 0"
            class="absolute inset-2 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center text-gray-400 hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
            @click="$emit('slot-click', { timeSlot, day: day.value })"
          >
            <PlusIcon class="w-6 h-6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Légende -->
    <div v-if="showLegend && subjects.length > 0" class="border-t border-gray-200 p-4 bg-gray-50">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Légende</h4>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="subject in subjects"
          :key="subject.id"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white"
          :style="{ backgroundColor: subject.color || '#6B7280' }"
        >
          {{ subject.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import type { TimeSlot, Schedule, Subject } from '@/types'
import { format, startOfWeek, addDays } from 'date-fns'
import { fr } from 'date-fns/locale'

interface Props {
  timeSlots: TimeSlot[]
  events: Schedule[]
  subjects?: Subject[]
  currentWeek?: Date
  viewMode?: 'teacher' | 'student' | 'class' | 'room'
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subjects: () => [],
  currentWeek: () => new Date(),
  viewMode: 'teacher',
  showLegend: true
})

const emit = defineEmits<{
  'course-click': [course: Schedule]
  'slot-click': [data: { timeSlot: TimeSlot, day: number }]
}>()

// Jours de la semaine
const weekDays = [
  { label: 'Lundi', value: 1 },
  { label: 'Mardi', value: 2 },
  { label: 'Mercredi', value: 3 },
  { label: 'Jeudi', value: 4 },
  { label: 'Vendredi', value: 5 }
]

// Computed
const weekStart = computed(() => startOfWeek(props.currentWeek, { weekStartsOn: 1 }))

// Méthodes
const getCoursesForSlot = (timeSlotId: number, dayOfWeek: number) => {
  return props.events.filter(event => {
    const timeSlot = props.timeSlots.find(ts => ts.id === event.time_slot)
    return timeSlot && timeSlot.id === timeSlotId && timeSlot.day_of_week === dayOfWeek
  })
}

const getCourseColor = (course: Schedule) => {
  // Essayer d'abord la couleur de la matière
  const subject = props.subjects.find(s => s.id === course.subject)
  if (subject?.color) {
    return subject.color
  }
  
  // Couleurs par défaut basées sur l'ID de la matière
  const colors = [
    '#3B82F6', // blue-500
    '#10B981', // emerald-500
    '#F59E0B', // amber-500
    '#EF4444', // red-500
    '#8B5CF6', // violet-500
    '#06B6D4', // cyan-500
    '#84CC16', // lime-500
    '#F97316', // orange-500
    '#EC4899', // pink-500
    '#6366F1'  // indigo-500
  ]
  
  const subjectId = course.subject || 0
  return colors[subjectId % colors.length]
}

const isToday = (dayOfWeek: number) => {
  const today = new Date()
  const dayDate = addDays(weekStart.value, dayOfWeek - 1)
  return format(today, 'yyyy-MM-dd') === format(dayDate, 'yyyy-MM-dd')
}

const formatDateForDay = (dayOfWeek: number) => {
  const dayDate = addDays(weekStart.value, dayOfWeek - 1)
  return format(dayDate, 'd MMM', { locale: fr })
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}
</script>

<style scoped>
.bg-blue-25 {
  background-color: rgb(239 246 255 / 0.5);
}
</style>