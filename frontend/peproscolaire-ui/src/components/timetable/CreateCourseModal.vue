<template>
  <BaseModal
    :is-open="isOpen"
    :title="isEditing ? 'Modifier le cours' : 'Nouveau cours'"
    @close="handleClose"
    size="lg"
  >
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Informations de base -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Matière *
          </label>
          <select
            v-model="form.subject"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner une matière</option>
            <option
              v-for="subject in subjects"
              :key="subject.id"
              :value="subject.id"
            >
              {{ subject.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Classe *
          </label>
          <select
            v-model="form.class_group"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner une classe</option>
            <option
              v-for="classItem in classes"
              :key="classItem.id"
              :value="classItem.id"
            >
              {{ classItem.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Salle *
          </label>
          <select
            v-model="form.room"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner une salle</option>
            <option
              v-for="room in rooms"
              :key="room.id"
              :value="room.id"
            >
              {{ room.name }} ({{ room.capacity }} places)
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Professeur
          </label>
          <select
            v-model="form.teacher"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner un professeur</option>
            <option
              v-for="teacher in teachers"
              :key="teacher.id"
              :value="teacher.id"
            >
              {{ teacher.first_name }} {{ teacher.last_name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Horaires -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Créneau horaire *
          </label>
          <select
            v-model="form.time_slot"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner un créneau</option>
            <option
              v-for="slot in timeSlots"
              :key="slot.id"
              :value="slot.id"
            >
              {{ getDayName(slot.day_of_week) }} - {{ formatTime(slot.start_time) }} à {{ formatTime(slot.end_time) }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Année académique *
          </label>
          <select
            v-model="form.academic_year"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Sélectionner l'année</option>
            <option
              v-for="year in academicYears"
              :key="year.id"
              :value="year.id"
            >
              {{ year.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Période -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Date de début *
          </label>
          <input
            v-model="form.effective_date"
            type="date"
            required
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Date de fin
          </label>
          <input
            v-model="form.end_date"
            type="date"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>
      </div>

      <!-- Récurrence -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Type de récurrence
        </label>
        <select
          v-model="form.recurrence_type"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="weekly">Hebdomadaire</option>
          <option value="biweekly">Bihebdomadaire</option>
          <option value="custom">Personnalisée</option>
        </select>
      </div>

      <!-- Vérification des conflits -->
      <div v-if="conflicts.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">
              Conflits détectés
            </h3>
            <div class="mt-2 text-sm text-yellow-700">
              <ul class="list-disc list-inside space-y-1">
                <li v-for="conflict in conflicts" :key="conflict.id">
                  {{ conflict.message }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        <BaseButton
          type="button"
          variant="secondary"
          @click="handleClose"
        >
          Annuler
        </BaseButton>
        
        <BaseButton
          type="button"
          variant="ghost"
          @click="checkConflicts"
          :loading="checkingConflicts"
        >
          Vérifier les conflits
        </BaseButton>
        
        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
          :disabled="conflicts.length > 0"
        >
          {{ isEditing ? 'Modifier' : 'Créer' }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import type { Schedule, TimeSlot, Subject, Room, User, AcademicYear, Class } from '@/types'

interface Props {
  isOpen: boolean
  schedule?: Schedule | null
  timeSlots: TimeSlot[]
  subjects: Subject[]
  rooms: Room[]
  teachers: User[]
  classes: Class[]
  academicYears: AcademicYear[]
}

const props = withDefaults(defineProps<Props>(), {
  schedule: null
})

const emit = defineEmits<{
  close: []
  submit: [data: Partial<Schedule>]
}>()

// État local
const loading = ref(false)
const checkingConflicts = ref(false)
const conflicts = ref<any[]>([])

// Formulaire
const form = reactive({
  subject: '',
  class_group: '',
  room: '',
  teacher: '',
  time_slot: '',
  academic_year: '',
  effective_date: '',
  end_date: '',
  recurrence_type: 'weekly',
  is_active: true
})

// Computed
const isEditing = computed(() => !!props.schedule)

// Méthodes
const handleClose = () => {
  resetForm()
  emit('close')
}

const handleSubmit = async () => {
  if (conflicts.value.length > 0) return
  
  loading.value = true
  
  try {
    const data = {
      ...form,
      subject: parseInt(form.subject),
      class_group: parseInt(form.class_group),
      room: parseInt(form.room),
      teacher: form.teacher ? parseInt(form.teacher) : null,
      time_slot: parseInt(form.time_slot),
      academic_year: parseInt(form.academic_year)
    }
    
    emit('submit', data)
    handleClose()
  } catch (error) {
    console.error('Erreur lors de la soumission:', error)
  } finally {
    loading.value = false
  }
}

const checkConflicts = async () => {
  checkingConflicts.value = true
  
  try {
    // TODO: Implémenter la vérification des conflits avec l'API
    // const response = await timetableApi.checkConflicts(form)
    // conflicts.value = response.conflicts || []
    
    // Simulation pour la démo
    conflicts.value = []
    
    console.log('Vérification des conflits pour:', form)
  } catch (error) {
    console.error('Erreur lors de la vérification des conflits:', error)
  } finally {
    checkingConflicts.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    subject: '',
    class_group: '',
    room: '',
    teacher: '',
    time_slot: '',
    academic_year: '',
    effective_date: '',
    end_date: '',
    recurrence_type: 'weekly',
    is_active: true
  })
  conflicts.value = []
}

const populateForm = (schedule: Schedule) => {
  Object.assign(form, {
    subject: schedule.subject?.toString() || '',
    class_group: schedule.class_group?.toString() || '',
    room: schedule.room?.toString() || '',
    teacher: schedule.teacher?.toString() || '',
    time_slot: schedule.time_slot?.toString() || '',
    academic_year: schedule.academic_year?.toString() || '',
    effective_date: schedule.effective_date || '',
    end_date: schedule.end_date || '',
    recurrence_type: schedule.recurrence_type || 'weekly',
    is_active: schedule.is_active ?? true
  })
}

const getDayName = (dayOfWeek: number) => {
  const days = ['', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
  return days[dayOfWeek] || ''
}

const formatTime = (timeString: string) => {
  return timeString.substring(0, 5)
}

// Watchers
watch(() => props.schedule, (newSchedule) => {
  if (newSchedule) {
    populateForm(newSchedule)
  } else {
    resetForm()
  }
}, { immediate: true })

watch(() => props.isOpen, (isOpen) => {
  if (!isOpen) {
    resetForm()
  }
})

// Vérification automatique des conflits quand les champs critiques changent
watch([() => form.time_slot, () => form.room, () => form.teacher], () => {
  if (form.time_slot && form.room) {
    conflicts.value = []
  }
})
</script>