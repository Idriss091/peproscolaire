import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { 
  Homework, 
  HomeworkAttachment,
  PaginatedResponse,
  Subject,
  Class
} from '@/types'
import { format, isAfter, isBefore, startOfDay, endOfDay } from 'date-fns'

interface HomeworkFilters {
  class?: number
  subject?: number
  teacher?: number
  student?: number
  givenDate?: string
  dueDate?: string
  dueDateFrom?: string
  dueDateTo?: string
  homeworkType?: string
  isGraded?: boolean
  search?: string
}

interface HomeworkSubmission {
  id: number
  homework: number
  student: number
  submitted_at: string
  content?: string
  attachments: Array<{
    id: number
    file: string
    file_name: string
    file_size: number
  }>
  grade?: number
  feedback?: string
  is_late: boolean
}

interface WorkloadAnalysis {
  date: string
  homeworkCount: number
  estimatedDuration: number
  subjects: Array<{
    subject: string
    count: number
    duration: number
  }>
}

export const useHomeworkStore = defineStore('homework', () => {
  // State
  const homeworks = ref<Homework[]>([])
  const recentHomework = ref<Homework[]>([])
  const submissions = ref<HomeworkSubmission[]>([])
  const workloadAnalysis = ref<WorkloadAnalysis[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentFilters = ref<HomeworkFilters>({})

  // Getters
  const upcomingHomework = computed(() => {
    const now = new Date()
    return homeworks.value
      .filter(hw => isAfter(new Date(hw.due_date), now))
      .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
  })

  const overdueHomework = computed(() => {
    const now = new Date()
    return homeworks.value
      .filter(hw => isBefore(new Date(hw.due_date), now))
      .filter(hw => {
        const submission = submissions.value.find(s => s.homework === hw.id)
        return !submission
      })
  })

  const homeworkBySubject = computed(() => {
    const grouped: Record<number, Homework[]> = {}
    homeworks.value.forEach(hw => {
      if (!grouped[hw.subject]) {
        grouped[hw.subject] = []
      }
      grouped[hw.subject].push(hw)
    })
    return grouped
  })

  const totalEstimatedDuration = computed(() => {
    return upcomingHomework.value.reduce((total, hw) => total + hw.estimated_duration, 0)
  })

  // Actions
  async function fetchHomework(filters: HomeworkFilters = {}) {
    loading.value = true
    error.value = null
    currentFilters.value = filters

    try {
      const params = new URLSearchParams()
      
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.subject) params.append('subject', filters.subject.toString())
      if (filters.teacher) params.append('teacher', filters.teacher.toString())
      if (filters.student) params.append('student', filters.student.toString())
      if (filters.givenDate) params.append('given_date', filters.givenDate)
      if (filters.dueDate) params.append('due_date', filters.dueDate)
      if (filters.dueDateFrom) params.append('due_date_from', filters.dueDateFrom)
      if (filters.dueDateTo) params.append('due_date_to', filters.dueDateTo)
      if (filters.homeworkType) params.append('homework_type', filters.homeworkType)
      if (filters.isGraded !== undefined) params.append('is_graded', filters.isGraded.toString())
      if (filters.search) params.append('search', filters.search)

      const response = await apiClient.get<PaginatedResponse<Homework>>(
        `/homework/homeworks/?${params.toString()}`
      )
      
      homeworks.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des devoirs'
      console.error('Failed to fetch homework:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchRecentHomework() {
    const today = new Date()
    const weekFromNow = new Date()
    weekFromNow.setDate(today.getDate() + 7)

    await fetchHomework({
      dueDateFrom: format(today, 'yyyy-MM-dd'),
      dueDateTo: format(weekFromNow, 'yyyy-MM-dd')
    })
    
    recentHomework.value = homeworks.value.slice(0, 10)
  }

  async function fetchHomeworkById(id: number) {
    try {
      const response = await apiClient.get<Homework>(`/homework/homeworks/${id}/`)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors du chargement du devoir'
      throw err
    }
  }

  async function createHomework(data: {
    title: string
    description: string
    subject: number
    class_group: number
    due_date: string
    estimated_duration: number
    homework_type: string
    is_graded: boolean
    visible_to_parents: boolean
    attachments?: File[]
  }) {
    loading.value = true
    error.value = null

    try {
      const formData = new FormData()
      
      // Add basic fields
      Object.entries(data).forEach(([key, value]) => {
        if (key !== 'attachments' && value !== undefined && value !== null) {
          formData.append(key, value.toString())
        }
      })

      // Add attachments
      if (data.attachments) {
        data.attachments.forEach((file, index) => {
          formData.append(`attachment_${index}`, file)
        })
      }

      const response = await apiClient.post<Homework>(
        '/homework/homeworks/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      homeworks.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la création du devoir'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateHomework(id: number, data: Partial<Homework>) {
    try {
      const response = await apiClient.patch<Homework>(
        `/homework/homeworks/${id}/`,
        data
      )
      
      const index = homeworks.value.findIndex(hw => hw.id === id)
      if (index !== -1) {
        homeworks.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour du devoir'
      throw err
    }
  }

  async function deleteHomework(id: number) {
    try {
      await apiClient.delete(`/homework/homeworks/${id}/`)
      homeworks.value = homeworks.value.filter(hw => hw.id !== id)
    } catch (err) {
      error.value = 'Erreur lors de la suppression du devoir'
      throw err
    }
  }

  async function fetchSubmissions(homeworkId: number) {
    try {
      const response = await apiClient.get<PaginatedResponse<HomeworkSubmission>>(
        `/homework/homeworks/${homeworkId}/submissions/`
      )
      submissions.value = response.data.results
      return response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des rendus'
      throw err
    }
  }

  async function submitHomework(homeworkId: number, data: {
    content?: string
    attachments?: File[]
  }) {
    try {
      const formData = new FormData()
      
      if (data.content) {
        formData.append('content', data.content)
      }

      if (data.attachments) {
        data.attachments.forEach((file, index) => {
          formData.append(`attachment_${index}`, file)
        })
      }

      const response = await apiClient.post<HomeworkSubmission>(
        `/homework/homeworks/${homeworkId}/submit/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      submissions.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la soumission du devoir'
      throw err
    }
  }

  async function gradeSubmission(submissionId: number, data: {
    grade: number
    feedback?: string
  }) {
    try {
      const response = await apiClient.patch<HomeworkSubmission>(
        `/homework/submissions/${submissionId}/`,
        data
      )
      
      const index = submissions.value.findIndex(s => s.id === submissionId)
      if (index !== -1) {
        submissions.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la notation'
      throw err
    }
  }

  async function fetchWorkloadAnalysis(filters: {
    class: number
    startDate: string
    endDate: string
  }) {
    try {
      const params = new URLSearchParams()
      params.append('class', filters.class.toString())
      params.append('start_date', filters.startDate)
      params.append('end_date', filters.endDate)

      const response = await apiClient.get<WorkloadAnalysis[]>(
        `/homework/workload-analysis/?${params.toString()}`
      )
      
      workloadAnalysis.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de l\'analyse de charge'
      throw err
    }
  }

  async function suggestHomework(data: {
    subject: number
    class_group: number
    topic: string
    difficulty?: 'easy' | 'medium' | 'hard'
  }) {
    try {
      const response = await apiClient.post('/homework/suggest/', data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la suggestion de devoirs'
      throw err
    }
  }

  async function duplicateHomework(id: number, targetClass: number) {
    try {
      const response = await apiClient.post<Homework>(
        `/homework/homeworks/${id}/duplicate/`,
        { target_class: targetClass }
      )
      
      homeworks.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la duplication du devoir'
      throw err
    }
  }

  return {
    // State
    homeworks,
    recentHomework,
    submissions,
    workloadAnalysis,
    loading,
    error,
    currentFilters,
    // Getters
    upcomingHomework,
    overdueHomework,
    homeworkBySubject,
    totalEstimatedDuration,
    // Actions
    fetchHomework,
    fetchRecentHomework,
    fetchHomeworkById,
    createHomework,
    updateHomework,
    deleteHomework,
    fetchSubmissions,
    submitHomework,
    gradeSubmission,
    fetchWorkloadAnalysis,
    suggestHomework,
    duplicateHomework
  }
})