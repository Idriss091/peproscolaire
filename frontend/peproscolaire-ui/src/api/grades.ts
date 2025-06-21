/**
 * API apiClient pour le module grades (notes et évaluations)
 */
import { apiClient } from './client'
import type { 
  EvaluationType,
  Evaluation,
  Grade,
  SubjectAverage,
  Competence,
  CompetenceGrade,
  Bulletin,
  ApiResponse,
  PaginatedResponse
} from '@/types'

export const gradesApi = {
  // Types d'évaluation
  getEvaluationTypes: async (params?: Record<string, any>): Promise<EvaluationType[]> => {
    try {
      const response = await apiClient.get('/grades/evaluation-types/', { params })
      return response.data.results || response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Fallback to mock data
        return []
      }
      throw error
    }
  },
  
  getEvaluationType: async (id: string): Promise<EvaluationType> => {
    try {
      const response = await apiClient.get(`/grades/evaluation-types/${id}/`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Type d\'évaluation non trouvé')
      }
      throw error
    }
  },
  
  createEvaluationType: async (data: Partial<EvaluationType>): Promise<EvaluationType> => {
    try {
      const response = await apiClient.post('/grades/evaluation-types/', data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateEvaluationType: async (id: string, data: Partial<EvaluationType>): Promise<EvaluationType> => {
    try {
      const response = await apiClient.put(`/grades/evaluation-types/${id}/`, data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  deleteEvaluationType: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`/grades/evaluation-types/${id}/`)
    } catch (error) {
      throw error
    }
  },

  // Évaluations
  getEvaluations: async (params?: Record<string, any>): Promise<PaginatedResponse<Evaluation>> => {
    try {
      const response = await apiClient.get('/grades/evaluations/', { params })
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Fallback to mock data
        return { results: [], count: 0, next: null, previous: null }
      }
      throw error
    }
  },
  
  getEvaluation: async (id: string): Promise<Evaluation> => {
    try {
      const response = await apiClient.get(`/grades/evaluations/${id}/`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Évaluation non trouvée')
      }
      throw error
    }
  },
  
  createEvaluation: async (data: Partial<Evaluation>): Promise<Evaluation> => {
    try {
      const response = await apiClient.post('/grades/evaluations/', data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateEvaluation: async (id: string, data: Partial<Evaluation>): Promise<Evaluation> => {
    try {
      const response = await apiClient.put(`/grades/evaluations/${id}/`, data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  deleteEvaluation: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`/grades/evaluations/${id}/`)
    } catch (error) {
      throw error
    }
  },
  
  getEvaluationGrades: async (id: string): Promise<Grade[]> => {
    try {
      const response = await apiClient.get(`/grades/evaluations/${id}/grades/`)
      return response.data.results || response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return []
      }
      throw error
    }
  },
  
  bulkUpdateEvaluationGrades: async (evaluationId: string, grades: Partial<Grade>[]): Promise<Grade[]> => {
    try {
      const response = await apiClient.post(`/grades/evaluations/${evaluationId}/bulk_update_grades/`, { grades })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Notes individuelles
  getGrades: async (params?: Record<string, any>): Promise<PaginatedResponse<Grade>> => {
    try {
      const response = await apiClient.get('/grades/grades/', { params })
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return { results: [], count: 0, next: null, previous: null }
      }
      throw error
    }
  },
  
  getGrade: async (id: string): Promise<Grade> => {
    try {
      const response = await apiClient.get(`/grades/grades/${id}/`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Note non trouvée')
      }
      throw error
    }
  },
  
  createGrade: async (data: Partial<Grade>): Promise<Grade> => {
    try {
      const response = await apiClient.post('/grades/grades/', data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateGrade: async (id: string, data: Partial<Grade>): Promise<Grade> => {
    try {
      const response = await apiClient.put(`/grades/grades/${id}/`, data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  deleteGrade: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`/grades/grades/${id}/`)
    } catch (error) {
      throw error
    }
  },

  // Moyennes par matière
  getSubjectAverages: async (params?: Record<string, any>): Promise<PaginatedResponse<SubjectAverage>> => {
    try {
      const response = await apiClient.get('/grades/subject-averages/', { params })
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return { results: [], count: 0, next: null, previous: null }
      }
      throw error
    }
  },
  
  getSubjectAverage: async (id: string): Promise<SubjectAverage> => {
    try {
      const response = await apiClient.get(`/grades/subject-averages/${id}/`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Moyenne non trouvée')
      }
      throw error
    }
  },
  
  getStudentAverages: (studentId: string, period?: string): Promise<SubjectAverage[]> =>
    apiClient.get('/subject-averages/by_student/', { 
      params: { student_id: studentId, period } 
    }),
  
  getClassAverages: (classId: string, period?: string): Promise<any> =>
    apiClient.get('/subject-averages/by_class/', { 
      params: { class_id: classId, period } 
    }),

  // Compétences
  getCompetences: (params?: Record<string, any>): Promise<PaginatedResponse<Competence>> =>
    apiClient.get('/competences/', { params }),
  
  getCompetence: (id: string): Promise<Competence> =>
    apiClient.get(`/competences/${id}/`),
  
  createCompetence: (data: Partial<Competence>): Promise<Competence> =>
    apiClient.post('/competences/', data),
  
  updateCompetence: (id: string, data: Partial<Competence>): Promise<Competence> =>
    apiClient.put(`/competences/${id}/`, data),
  
  deleteCompetence: (id: string): Promise<void> =>
    apiClient.delete(`/competences/${id}/`),

  // Notes de compétences
  getCompetenceGrades: (params?: Record<string, any>): Promise<PaginatedResponse<CompetenceGrade>> =>
    apiClient.get('/competence-grades/', { params }),
  
  getCompetenceGrade: (id: string): Promise<CompetenceGrade> =>
    apiClient.get(`/competence-grades/${id}/`),
  
  createCompetenceGrade: (data: Partial<CompetenceGrade>): Promise<CompetenceGrade> =>
    apiClient.post('/competence-grades/', data),
  
  updateCompetenceGrade: (id: string, data: Partial<CompetenceGrade>): Promise<CompetenceGrade> =>
    apiClient.put(`/competence-grades/${id}/`, data),
  
  deleteCompetenceGrade: (id: string): Promise<void> =>
    apiClient.delete(`/competence-grades/${id}/`),

  // Bulletins
  getBulletins: (params?: Record<string, any>): Promise<PaginatedResponse<Bulletin>> =>
    apiClient.get('/bulletins/', { params }),
  
  getBulletin: (id: string): Promise<Bulletin> =>
    apiClient.get(`/bulletins/${id}/`),
  
  createBulletin: (data: Partial<Bulletin>): Promise<Bulletin> =>
    apiClient.post('/bulletins/', data),
  
  updateBulletin: (id: string, data: Partial<Bulletin>): Promise<Bulletin> =>
    apiClient.put(`/bulletins/${id}/`, data),
  
  deleteBulletin: (id: string): Promise<void> =>
    apiClient.delete(`/bulletins/${id}/`),
  
  generateBulletin: (studentId: string, period: string): Promise<Bulletin> =>
    apiClient.post('/bulletins/generate/', { 
      student_id: studentId, 
      period 
    }),
  
  getBulletinPdf: (id: string): Promise<Blob> =>
    apiClient.get(`/bulletins/${id}/pdf/`, { responseType: 'blob' }),

  // Statistiques et analyses
  getGradeStatistics: (params?: Record<string, any>): Promise<any> =>
    apiClient.get('/statistics/', { params }),
  
  getClassPerformance: (classId: string, subject?: string): Promise<any> =>
    apiClient.get('/statistics/class_performance/', { 
      params: { class_id: classId, subject } 
    }),
  
  getStudentProgress: (studentId: string): Promise<any> =>
    apiClient.get('/statistics/student_progress/', { 
      params: { student_id: studentId } 
    }),

  // Actions en lot
  bulkCreateGrades: (grades: Partial<Grade>[]): Promise<Grade[]> =>
    apiClient.post('/grades/bulk_create/', { grades }),
  
  bulkUpdateGrades: (grades: Partial<Grade>[]): Promise<Grade[]> =>
    apiClient.post('/grades/bulk_update/', { grades }),
  
  bulkDeleteGrades: (ids: string[]): Promise<ApiResponse> =>
    apiClient.post('/grades/bulk_delete/', { ids }),

  // Import/Export
  exportGrades: (params?: Record<string, any>): Promise<Blob> =>
    apiClient.get('/grades/export/', { 
      params, 
      responseType: 'blob' 
    }),
  
  importGrades: (file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/grades/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}