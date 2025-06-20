import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { Schedule, TimeSlot, Subject, Room, PaginatedResponse } from '@/types'
import { format, startOfWeek, endOfWeek, isToday } from 'date-fns'

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
    return schedules.value.filter(schedule => {
      const slot = timeSlots.value.find(ts => ts.id === schedule.time_slot)
      return slot && slot.day_of_week === dayOfWeek && slot.id === timeSlotId
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
      const params = new URLSearchParams()
      
      if (filters.view) params.append('view', filters.view)
      if (filters.entityId) params.append('entity_id', filters.entityId.toString())
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.subject) params.append('subject', filters.subject.toString())
      if (filters.isActive !== undefined) params.append('is_active', filters.isActive.toString())

      const response = await apiClient.get<PaginatedResponse<Schedule>>(
        `/timetable/schedules/?${params.toString()}`
      )
      
      schedules.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement de l\'emploi du temps'
      console.error('Failed to fetch schedules:', err)
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
      const response = await apiClient.get<PaginatedResponse<TimeSlot>>('/timetable/timeslots/')
      timeSlots.value = response.data.results
    } catch (err) {
      console.error('Failed to fetch time slots:', err)
    }
  }

  async function fetchSubjects() {
    try {
      const response = await apiClient.get<PaginatedResponse<Subject>>('/timetable/subjects/')
      subjects.value = response.data.results
    } catch (err) {
      console.error('Failed to fetch subjects:', err)
    }
  }

  async function fetchRooms() {
    try {
      const response = await apiClient.get<PaginatedResponse<Room>>('/timetable/rooms/')
      rooms.value = response.data.results
    } catch (err) {
      console.error('Failed to fetch rooms:', err)
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