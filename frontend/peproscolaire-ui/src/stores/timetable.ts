import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { Schedule, TimeSlot, Subject, Room, PaginatedResponse } from '@/types'
import { format, startOfWeek, endOfWeek, isToday } from 'date-fns'

// Données mockées pour le développement
const MOCK_TIME_SLOTS: TimeSlot[] = [
  { id: '1', name: '8h00 - 9h00', start_time: '08:00', end_time: '09:00', order: 1 },
  { id: '2', name: '9h00 - 10h00', start_time: '09:00', end_time: '10:00', order: 2 },
  { id: '3', name: '10h15 - 11h15', start_time: '10:15', end_time: '11:15', order: 3 },
  { id: '4', name: '11h15 - 12h15', start_time: '11:15', end_time: '12:15', order: 4 },
  { id: '5', name: '14h00 - 15h00', start_time: '14:00', end_time: '15:00', order: 5 },
  { id: '6', name: '15h00 - 16h00', start_time: '15:00', end_time: '16:00', order: 6 },
]

const MOCK_SUBJECTS: Subject[] = [
  { id: '1', name: 'Mathématiques', code: 'MATH', color: '#3B82F6' },
  { id: '2', name: 'Français', code: 'FR', color: '#EF4444' },
  { id: '3', name: 'Histoire-Géographie', code: 'HG', color: '#10B981' },
  { id: '4', name: 'Sciences Physiques', code: 'PC', color: '#F59E0B' },
  { id: '5', name: 'Anglais', code: 'ANG', color: '#8B5CF6' },
]

const MOCK_ROOMS: Room[] = [
  { id: '1', name: 'Salle 101', capacity: 30, building: 'Bâtiment A' },
  { id: '2', name: 'Salle 102', capacity: 25, building: 'Bâtiment A' },
  { id: '3', name: 'Labo Sciences', capacity: 20, building: 'Bâtiment B' },
  { id: '4', name: 'CDI', capacity: 40, building: 'Bâtiment C' },
]

const MOCK_SCHEDULES: Schedule[] = [
  {
    id: '1',
    subject: MOCK_SUBJECTS[0],
    teacher: { id: '1', first_name: 'Jean', last_name: 'Martin' },
    room: MOCK_ROOMS[0],
    time_slot: MOCK_TIME_SLOTS[0],
    date: format(new Date(), 'yyyy-MM-dd'),
    day_of_week: new Date().getDay(),
    class_name: '3ème A',
    is_cancelled: false,
  },
  {
    id: '2',
    subject: MOCK_SUBJECTS[1],
    teacher: { id: '2', first_name: 'Marie', last_name: 'Dupont' },
    room: MOCK_ROOMS[1],
    time_slot: MOCK_TIME_SLOTS[1],
    date: format(new Date(), 'yyyy-MM-dd'),
    day_of_week: new Date().getDay(),
    class_name: '3ème A',
    is_cancelled: false,
  },
]

const useMockApi = () => import.meta.env.VITE_USE_MOCK_API === 'true'

interface TimetableFilters {
  view?: 'teacher' | 'student' | 'class' | 'room'
  entityId?: number
  startDate?: string
  endDate?: string
  subject?: number
  isActive?: boolean
}

export const useTimetableStore = defineStore('timetable', () => {
  // State
  const schedules = ref<Schedule[]>([])
  const todaySchedule = ref<Schedule[]>([])
  const weekSchedule = ref<Schedule[]>([])
  const timeSlots = ref<TimeSlot[]>([])
  const subjects = ref<Subject[]>([])
  const rooms = ref<Room[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentFilters = ref<TimetableFilters>({})

  // Getters
  const schedulesByDay = computed(() => {
    const grouped: Record<number, Schedule[]> = {}
    weekSchedule.value.forEach(schedule => {
      const slot = timeSlots.value.find(ts => ts.id === schedule.time_slot)
      if (slot) {
        if (!grouped[slot.day_of_week]) {
          grouped[slot.day_of_week] = []
        }
        grouped[slot.day_of_week].push(schedule)
      }
    })
    return grouped
  })

  const upcomingSchedules = computed(() => {
    return todaySchedule.value
      .filter(schedule => {
        const slot = timeSlots.value.find(ts => ts.id === schedule.time_slot)
        if (!slot) return false
        const now = new Date()
        const [hours, minutes] = slot.start_time.split(':').map(Number)
        const scheduleTime = new Date()
        scheduleTime.setHours(hours, minutes, 0, 0)
        return scheduleTime > now
      })
      .sort((a, b) => {
        const slotA = timeSlots.value.find(ts => ts.id === a.time_slot)!
        const slotB = timeSlots.value.find(ts => ts.id === b.time_slot)!
        return slotA.start_time.localeCompare(slotB.start_time)
      })
  })

  const filteredSchedules = computed(() => {
    return schedules.value
  })

  // Helper methods
  function getScheduleForSlot(dayOfWeek: number, timeSlotId: string | number) {
    return (schedules.value || []).filter(schedule => {
      return schedule.day_of_week === dayOfWeek && schedule.time_slot === timeSlotId.toString()
    })
  }

  function getTimeSlotById(id: string | number) {
    return timeSlots.value.find(slot => slot.id === id)
  }

  // Actions
  async function fetchSchedules(filters: TimetableFilters = {}) {
    loading.value = true
    error.value = null
    currentFilters.value = filters

    try {
      if (useMockApi()) {
        // Mode mock - retourner des données simulées
        await new Promise(resolve => setTimeout(resolve, 300)) // Simuler latence
        schedules.value = MOCK_SCHEDULES
      } else {
        const params = new URLSearchParams()
        
        if (filters.view) params.append('view', filters.view)
        if (filters.entityId) params.append('entity_id', filters.entityId.toString())
        if (filters.startDate) params.append('start_date', filters.startDate)
        if (filters.endDate) params.append('end_date', filters.endDate)
        if (filters.subject) params.append('subject', filters.subject.toString())
        if (filters.isActive !== undefined) params.append('is_active', filters.isActive.toString())

        const response = await apiClient.get<any>(
          `/timetable/?${params.toString()}`
        )
        
        // Transformer les données de l'API en format attendu par le store
        const apiData = response.data
        const transformedSchedules = []
        
        // Convertir {monday: [...], tuesday: [...]} en tableau de Schedule
        const dayMap = {
          monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5
        }
        
        // Mapping des horaires API vers les time_slot ids du store
        const timeSlotMapping = {
          '08:00-09:00': '1',
          '09:00-10:00': '2', 
          '10:15-11:15': '3',
          '11:15-12:15': '4',
          '14:00-15:00': '5',
          '15:00-16:00': '6'
        }
        
        Object.keys(apiData).forEach(dayKey => {
          const dayOfWeek = dayMap[dayKey]
          if (dayOfWeek && apiData[dayKey]) {
            apiData[dayKey].forEach((item, index) => {
              const timeSlotId = timeSlotMapping[item.time] || (index + 1).toString()
              const [startTime, endTime] = item.time.split('-')
              
              transformedSchedules.push({
                id: `${dayKey}-${index}`,
                subject: { id: index.toString(), name: item.subject, code: item.subject.substring(0, 3), color: '#3B82F6' },
                teacher: { 
                  id: index.toString(), 
                  first_name: item.teacher.split(' ')[1] || item.teacher, 
                  last_name: item.teacher.split(' ')[0] 
                },
                room: { id: index.toString(), name: item.room },
                time_slot: timeSlotId,
                subject_name: item.subject,
                subject_color: '#3B82F6',
                teacher_name: item.teacher,
                room_name: item.room,
                class_name: '3ème A',
                date: new Date().toISOString().split('T')[0],
                day_of_week: dayOfWeek,
                is_cancelled: false
              })
            })
          }
        })
        
        schedules.value = transformedSchedules
      }
    } catch (err) {
      // Fallback vers les données mock en cas d'erreur
      console.warn('API call failed, using mock data:', err)
      schedules.value = MOCK_SCHEDULES
    } finally {
      loading.value = false
    }
  }

  async function fetchTodaySchedule() {
    const today = format(new Date(), 'yyyy-MM-dd')
    await fetchSchedules({
      startDate: today,
      endDate: today,
      isActive: true
    })
    todaySchedule.value = schedules.value
  }

  async function fetchWeekSchedule(date: Date = new Date()) {
    const start = format(startOfWeek(date, { weekStartsOn: 1 }), 'yyyy-MM-dd')
    const end = format(endOfWeek(date, { weekStartsOn: 1 }), 'yyyy-MM-dd')
    
    await fetchSchedules({
      startDate: start,
      endDate: end,
      isActive: true
    })
    weekSchedule.value = schedules.value
  }

  async function fetchTimeSlots() {
    try {
      if (useMockApi()) {
        await new Promise(resolve => setTimeout(resolve, 200))
        timeSlots.value = MOCK_TIME_SLOTS
      } else {
        const response = await apiClient.get<PaginatedResponse<TimeSlot>>('/timetable/timeslots/')
        timeSlots.value = response.data.results
      }
    } catch (err) {
      console.warn('Failed to fetch time slots, using mock data:', err)
      timeSlots.value = MOCK_TIME_SLOTS
    }
  }

  async function fetchSubjects() {
    try {
      if (useMockApi()) {
        await new Promise(resolve => setTimeout(resolve, 200))
        subjects.value = MOCK_SUBJECTS
      } else {
        const response = await apiClient.get<PaginatedResponse<Subject>>('/timetable/subjects/')
        subjects.value = response.data.results
      }
    } catch (err) {
      console.warn('Failed to fetch subjects, using mock data:', err)
      subjects.value = MOCK_SUBJECTS
    }
  }

  async function fetchRooms() {
    try {
      if (useMockApi()) {
        await new Promise(resolve => setTimeout(resolve, 200))
        rooms.value = MOCK_ROOMS
      } else {
        const response = await apiClient.get<PaginatedResponse<Room>>('/timetable/rooms/')
        rooms.value = response.data.results
      }
    } catch (err) {
      console.warn('Failed to fetch rooms, using mock data:', err)
      rooms.value = MOCK_ROOMS
    }
  }

  async function createSchedule(data: Partial<Schedule>) {
    try {
      const response = await apiClient.post<Schedule>('/timetable/schedules/', data)
      schedules.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la création du cours'
      throw err
    }
  }

  async function updateSchedule(id: number, data: Partial<Schedule>) {
    try {
      const response = await apiClient.patch<Schedule>(`/timetable/schedules/${id}/`, data)
      const index = schedules.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schedules.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour du cours'
      throw err
    }
  }

  async function deleteSchedule(id: number) {
    try {
      await apiClient.delete(`/timetable/schedules/${id}/`)
      schedules.value = schedules.value.filter(s => s.id !== id)
    } catch (err) {
      error.value = 'Erreur lors de la suppression du cours'
      throw err
    }
  }

  async function createTemporaryModification(scheduleId: number, data: {
    date: string
    new_time_slot?: number
    new_room?: number
    new_teacher?: number
    is_cancelled?: boolean
    reason: string
  }) {
    try {
      const response = await apiClient.post(
        `/timetable/schedules/${scheduleId}/modifications/`,
        data
      )
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la création de la modification'
      throw err
    }
  }

  async function exportTimetable(format: 'pdf' | 'ical', filters: TimetableFilters = {}) {
    try {
      const params = new URLSearchParams()
      params.append('format', format)
      
      if (filters.view) params.append('view', filters.view)
      if (filters.entityId) params.append('entity_id', filters.entityId.toString())
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)

      const response = await apiClient.get(
        `/timetable/export/?${params.toString()}`,
        { responseType: 'blob' }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `emploi-du-temps.${format === 'pdf' ? 'pdf' : 'ics'}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors de l\'export'
      throw err
    }
  }

  // Initialize
  async function initialize() {
    await Promise.all([
      fetchTimeSlots(),
      fetchSubjects(),
      fetchRooms()
    ])
  }

  return {
    // State
    schedules,
    todaySchedule,
    weekSchedule,
    timeSlots,
    subjects,
    rooms,
    loading: { schedules: loading, timeSlots: loading },
    error,
    currentFilters,
    // Getters
    schedulesByDay,
    upcomingSchedules,
    filteredSchedules,
    // Helper methods
    getScheduleForSlot,
    getTimeSlotById,
    // Actions
    fetchSchedules,
    fetchTodaySchedule,
    fetchWeekSchedule,
    fetchTimeSlots,
    fetchSubjects,
    fetchRooms,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    createTemporaryModification,
    exportTimetable,
    initialize
  }
})