import { apiClient } from './client'
import type { 
  Homework,
  HomeworkSubmission,
  HomeworkType,
  APIResponse,
  PaginatedResponse 
} from '@/types'

export const homeworkApi = {
  // Homework (Devoirs)
  async getHomework(params?: {
    subject?: string
    class_group?: string
    teacher?: string
    student?: string
    homework_type?: string
    status?: 'draft' | 'published' | 'archived'
    due_date_from?: string
    due_date_to?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Homework>> {
    const response = await apiClient.get('/homework/', { params })
    return response.data
  },

  async getHomeworkItem(id: string): Promise<Homework> {
    const response = await apiClient.get(`/homework/${id}/`)
    return response.data
  },

  async createHomework(data: {
    title: string
    description: string
    subject: string
    class_group: string
    homework_type: string
    due_date: string
    estimated_duration?: number
    instructions?: string
    resources?: string[]
    attachments?: File[]
    points_max?: number
    is_graded?: boolean
    allow_late_submission?: boolean
    late_penalty?: number
  }): Promise<Homework> {
    const formData = new FormData()
    
    // Ajouter les champs texte
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && key !== 'attachments' && key !== 'resources') {
        if (typeof value === 'boolean' || typeof value === 'number') {
          formData.append(key, value.toString())
        } else {
          formData.append(key, value as string)
        }
      }
    })

    // Ajouter les resources (array)
    if (data.resources) {
      data.resources.forEach((resource, index) => {
        formData.append(`resources[${index}]`, resource)
      })
    }

    // Ajouter les fichiers
    if (data.attachments) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file)
      })
    }

    const response = await apiClient.post('/homework/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateHomework(id: string, data: Partial<Homework>): Promise<Homework> {
    const response = await apiClient.patch(`/homework/${id}/`, data)
    return response.data
  },

  async deleteHomework(id: string): Promise<void> {
    await apiClient.delete(`/homework/${id}/`)
  },

  async duplicateHomework(id: string, data?: {
    class_group?: string
    due_date?: string
    title?: string
  }): Promise<Homework> {
    const response = await apiClient.post(`/homework/${id}/duplicate/`, data)
    return response.data
  },

  async publishHomework(id: string): Promise<Homework> {
    const response = await apiClient.post(`/homework/${id}/publish/`)
    return response.data
  },

  async archiveHomework(id: string): Promise<Homework> {
    const response = await apiClient.post(`/homework/${id}/archive/`)
    return response.data
  },

  // Homework Submissions (Rendus)
  async getSubmissions(homeworkId: string, params?: {
    student?: string
    status?: 'draft' | 'submitted' | 'graded' | 'late'
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<HomeworkSubmission>> {
    const response = await apiClient.get(`/homework/${homeworkId}/submissions/`, { params })
    return response.data
  },

  async getSubmission(id: string): Promise<HomeworkSubmission> {
    const response = await apiClient.get(`/homework/submissions/${id}/`)
    return response.data
  },

  async createSubmission(homeworkId: string, data: {
    content?: string
    attachments?: File[]
    is_draft?: boolean
  }): Promise<HomeworkSubmission> {
    const formData = new FormData()
    formData.append('homework', homeworkId)
    
    if (data.content) {
      formData.append('content', data.content)
    }
    
    if (data.is_draft !== undefined) {
      formData.append('is_draft', data.is_draft.toString())
    }
    
    if (data.attachments) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file)
      })
    }

    const response = await apiClient.post('/homework/submissions/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateSubmission(id: string, data: {
    content?: string
    attachments?: File[]
    is_draft?: boolean
  }): Promise<HomeworkSubmission> {
    const formData = new FormData()
    
    if (data.content) {
      formData.append('content', data.content)
    }
    
    if (data.is_draft !== undefined) {
      formData.append('is_draft', data.is_draft.toString())
    }
    
    if (data.attachments) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file)
      })
    }

    const response = await apiClient.patch(`/homework/submissions/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async submitHomework(id: string): Promise<HomeworkSubmission> {
    const response = await apiClient.post(`/homework/submissions/${id}/submit/`)
    return response.data
  },

  async gradeSubmission(id: string, data: {
    points_earned: number
    feedback?: string
    is_late?: boolean
  }): Promise<HomeworkSubmission> {
    const response = await apiClient.post(`/homework/submissions/${id}/grade/`, data)
    return response.data
  },

  async requestRevision(id: string, data: {
    feedback: string
    revision_instructions?: string
  }): Promise<HomeworkSubmission> {
    const response = await apiClient.post(`/homework/submissions/${id}/request-revision/`, data)
    return response.data
  },

  // Homework Types
  async getHomeworkTypes(): Promise<HomeworkType[]> {
    const response = await apiClient.get('/homework/types/')
    return response.data
  },

  async createHomeworkType(data: {
    name: string
    description?: string
    color?: string
    is_active?: boolean
  }): Promise<HomeworkType> {
    const response = await apiClient.post('/homework/types/', data)
    return response.data
  },

  async updateHomeworkType(id: string, data: Partial<HomeworkType>): Promise<HomeworkType> {
    const response = await apiClient.patch(`/homework/types/${id}/`, data)
    return response.data
  },

  async deleteHomeworkType(id: string): Promise<void> {
    await apiClient.delete(`/homework/types/${id}/`)
  },

  // Bulk Operations
  async bulkGradeSubmissions(submissions: {
    submission_id: string
    points_earned: number
    feedback?: string
  }[]): Promise<HomeworkSubmission[]> {
    const response = await apiClient.post('/homework/submissions/bulk-grade/', {
      submissions
    })
    return response.data
  },

  async bulkAssignHomework(homeworkId: string, data: {
    class_groups: string[]
    due_date?: string
    modifications?: {
      [key: string]: any
    }
  }): Promise<Homework[]> {
    const response = await apiClient.post(`/homework/${homeworkId}/bulk-assign/`, data)
    return response.data
  },

  // Statistics
  async getHomeworkStats(params?: {
    teacher?: string
    subject?: string
    class_group?: string
    date_from?: string
    date_to?: string
  }): Promise<{
    total_homework: number
    published_homework: number
    draft_homework: number
    average_submissions: number
    average_grade: number
    on_time_rate: number
    late_submissions: number
  }> {
    const response = await apiClient.get('/homework/stats/', { params })
    return response.data
  },

  async getSubmissionStats(homeworkId: string): Promise<{
    total_students: number
    submitted_count: number
    draft_count: number
    graded_count: number
    late_count: number
    submission_rate: number
    average_grade: number
    grade_distribution: {
      range: string
      count: number
    }[]
  }> {
    const response = await apiClient.get(`/homework/${homeworkId}/submission-stats/`)
    return response.data
  },

  async getStudentHomeworkStats(studentId: string, params?: {
    subject?: string
    date_from?: string
    date_to?: string
  }): Promise<{
    total_assigned: number
    submitted_count: number
    graded_count: number
    late_count: number
    average_grade: number
    completion_rate: number
    punctuality_rate: number
  }> {
    const response = await apiClient.get('/homework/student-stats/', {
      params: { student: studentId, ...params }
    })
    return response.data
  },

  // Calendar Integration
  async getHomeworkCalendar(params: {
    date_from: string
    date_to: string
    student?: string
    teacher?: string
    class_group?: string
  }): Promise<{
    date: string
    homework: {
      id: string
      title: string
      subject_name: string
      homework_type: string
      is_due: boolean
    }[]
  }[]> {
    const response = await apiClient.get('/homework/calendar/', { params })
    return response.data
  },

  // Export/Import
  async exportHomework(params?: {
    homework_ids?: string[]
    class_group?: string
    subject?: string
    format?: 'xlsx' | 'csv' | 'pdf'
  }): Promise<Blob> {
    const response = await apiClient.get('/homework/export/', {
      params,
      responseType: 'blob'
    })
    return response.data
  },

  async exportSubmissions(homeworkId: string, format: 'xlsx' | 'csv' | 'zip' = 'xlsx'): Promise<Blob> {
    const response = await apiClient.get(`/homework/${homeworkId}/export-submissions/`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  },

  // AI Suggestions (si le module IA est disponible)
  async getAISuggestions(data: {
    subject: string
    class_level: string
    topic?: string
    difficulty?: 'easy' | 'medium' | 'hard'
    duration?: number
  }): Promise<{
    title: string
    description: string
    instructions: string
    estimated_duration: number
    resources: string[]
  }[]> {
    const response = await apiClient.post('/homework/ai-suggestions/', data)
    return response.data
  },

  async generateHomeworkFromAI(data: {
    subject: string
    class_level: string
    topic: string
    difficulty: 'easy' | 'medium' | 'hard'
    homework_type: string
    estimated_duration: number
  }): Promise<{
    title: string
    description: string
    instructions: string
    resources: string[]
    evaluation_criteria: string[]
  }> {
    const response = await apiClient.post('/homework/ai-generate/', data)
    return response.data
  },

  // Notifications
  async getUpcomingDeadlines(days: number = 7): Promise<Homework[]> {
    const response = await apiClient.get('/homework/upcoming-deadlines/', {
      params: { days }
    })
    return response.data
  },

  async getOverdueHomework(): Promise<Homework[]> {
    const response = await apiClient.get('/homework/overdue/')
    return response.data
  },

  async getUnsubmittedHomework(studentId?: string): Promise<Homework[]> {
    const params = studentId ? { student: studentId } : {}
    const response = await apiClient.get('/homework/unsubmitted/', { params })
    return response.data
  }
}