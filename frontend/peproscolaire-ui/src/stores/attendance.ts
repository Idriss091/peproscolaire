import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { 
  Attendance, 
  AbsencePeriod, 
  PaginatedResponse,
  Schedule,
  User 
} from '@/types'
import { format } from 'date-fns'

interface AttendanceFilters {
  student?: number
  class?: number
  date?: string
  startDate?: string
  endDate?: string
  status?: 'present' | 'absent' | 'late' | 'excused'
  schedule?: number
}

interface AttendanceStats {
  totalStudents: number
  present: number
  absent: number
  late: number
  excused: number
  attendanceRate: number
}

export const useAttendanceStore = defineStore('attendance', () => {
  // State
  const attendances = ref<Attendance[]>([])
  const pendingAttendance = ref<any[]>([]) // Classes with pending attendance
  const absencePeriods = ref<AbsencePeriod[]>([])
  const currentClassStudents = ref<User[]>([])
  const stats = ref<AttendanceStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const attendanceByStudent = computed(() => {
    const grouped: Record<number, Attendance[]> = {}
    attendances.value.forEach(attendance => {
      if (!grouped[attendance.student]) {
        grouped[attendance.student] = []
      }
      grouped[attendance.student].push(attendance)
    })
    return grouped
  })

  const absentStudents = computed(() => {
    return attendances.value.filter(a => a.status === 'absent')
  })

  const chronicAbsentees = computed(() => {
    const studentAbsences: Record<number, number> = {}
    
    attendances.value
      .filter(a => a.status === 'absent' || a.status === 'late')
      .forEach(a => {
        studentAbsences[a.student] = (studentAbsences[a.student] || 0) + 1
      })
    
    return Object.entries(studentAbsences)
      .filter(([_, count]) => count >= 5) // 5+ absences
      .map(([studentId, count]) => ({
        studentId: parseInt(studentId),
        absenceCount: count
      }))
  })

  // Actions
  async function fetchAttendances(filters: AttendanceFilters = {}) {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      
      if (filters.student) params.append('student', filters.student.toString())
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.date) params.append('date', filters.date)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.status) params.append('status', filters.status)
      if (filters.schedule) params.append('schedule', filters.schedule.toString())

      const response = await apiClient.get<PaginatedResponse<Attendance>>(
        `/attendance/attendances/?${params.toString()}`
      )
      
      attendances.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des présences'
      console.error('Failed to fetch attendances:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPendingAttendance() {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/attendance/pending/')
      pendingAttendance.value = response.data.results || []
    } catch (err) {
      error.value = 'Erreur lors du chargement des appels en attente'
      console.error('Failed to fetch pending attendance:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchClassStudents(classId: number) {
    try {
      const response = await apiClient.get<PaginatedResponse<User>>(
        `/schools/classes/${classId}/students/`
      )
      currentClassStudents.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des élèves'
      throw err
    }
  }

  async function markAttendance(data: {
    schedule: number
    date: string
    attendances: Array<{
      student: number
      status: 'present' | 'absent' | 'late' | 'excused'
      arrival_time?: string
      notes?: string
    }>
  }) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/attendance/mark/', data)
      
      // Update local state
      if (response.data.attendances) {
        attendances.value.push(...response.data.attendances)
      }
      
      // Remove from pending
      pendingAttendance.value = pendingAttendance.value.filter(
        p => p.schedule_id !== data.schedule
      )
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de l\'enregistrement de l\'appel'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateAttendance(id: number, data: Partial<Attendance>) {
    try {
      const response = await apiClient.patch<Attendance>(
        `/attendance/attendances/${id}/`,
        data
      )
      
      const index = attendances.value.findIndex(a => a.id === id)
      if (index !== -1) {
        attendances.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour'
      throw err
    }
  }

  async function createAbsencePeriod(data: {
    student: number
    start_date: string
    end_date: string
    reason: string
    justification?: string
    justification_document?: File
  }) {
    try {
      const formData = new FormData()
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (value instanceof File) {
            formData.append(key, value)
          } else {
            formData.append(key, value.toString())
          }
        }
      })

      const response = await apiClient.post<AbsencePeriod>(
        '/attendance/absence-periods/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      absencePeriods.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la création de la période d\'absence'
      throw err
    }
  }

  async function justifyAbsence(absenceId: number, data: {
    justification: string
    justification_document?: File
  }) {
    try {
      const formData = new FormData()
      formData.append('justification', data.justification)
      formData.append('justified', 'true')
      
      if (data.justification_document) {
        formData.append('justification_document', data.justification_document)
      }

      const response = await apiClient.patch<AbsencePeriod>(
        `/attendance/absence-periods/${absenceId}/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      const index = absencePeriods.value.findIndex(a => a.id === absenceId)
      if (index !== -1) {
        absencePeriods.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la justification'
      throw err
    }
  }

  async function fetchAttendanceStats(filters: {
    class?: number
    date?: string
    startDate?: string
    endDate?: string
  } = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.date) params.append('date', filters.date)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)

      const response = await apiClient.get<AttendanceStats>(
        `/attendance/stats/?${params.toString()}`
      )
      
      stats.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch attendance stats:', err)
      throw err
    }
  }

  async function generateAttendanceReport(filters: {
    class?: number
    student?: number
    startDate: string
    endDate: string
    format: 'pdf' | 'excel'
  }) {
    try {
      const params = new URLSearchParams()
      
      params.append('start_date', filters.startDate)
      params.append('end_date', filters.endDate)
      params.append('format', filters.format)
      
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.student) params.append('student', filters.student.toString())

      const response = await apiClient.get(
        `/attendance/report/?${params.toString()}`,
        { responseType: 'blob' }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `rapport-assiduite.${filters.format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors de la génération du rapport'
      throw err
    }
  }

  return {
    // State
    attendances,
    pendingAttendance,
    absencePeriods,
    currentClassStudents,
    stats,
    loading,
    error,
    // Getters
    attendanceByStudent,
    absentStudents,
    chronicAbsentees,
    // Actions
    fetchAttendances,
    fetchPendingAttendance,
    fetchClassStudents,
    markAttendance,
    updateAttendance,
    createAbsencePeriod,
    justifyAbsence,
    fetchAttendanceStats,
    generateAttendanceReport
  }
})