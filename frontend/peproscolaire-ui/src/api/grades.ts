/**
 * API apiClient pour le module grades (notes et évaluations)
 */
import { apiClient } from './apiClient'
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
  getEvaluationTypes: (params?: Record<string, any>): Promise<EvaluationType[]> =>
    apiClient.get('/evaluation-types/', { params }),
  
  getEvaluationType: (id: string): Promise<EvaluationType> =>
    apiClient.get(`/evaluation-types/${id}/`),
  
  createEvaluationType: (data: Partial<EvaluationType>): Promise<EvaluationType> =>
    apiClient.post('/evaluation-types/', data),
  
  updateEvaluationType: (id: string, data: Partial<EvaluationType>): Promise<EvaluationType> =>
    apiClient.put(`/evaluation-types/${id}/`, data),
  
  deleteEvaluationType: (id: string): Promise<void> =>
    apiClient.delete(`/evaluation-types/${id}/`),

  // Évaluations
  getEvaluations: (params?: Record<string, any>): Promise<PaginatedResponse<Evaluation>> =>
    apiClient.get('/evaluations/', { params }),
  
  getEvaluation: (id: string): Promise<Evaluation> =>
    apiClient.get(`/evaluations/${id}/`),
  
  createEvaluation: (data: Partial<Evaluation>): Promise<Evaluation> =>
    apiClient.post('/evaluations/', data),
  
  updateEvaluation: (id: string, data: Partial<Evaluation>): Promise<Evaluation> =>
    apiClient.put(`/evaluations/${id}/`, data),
  
  deleteEvaluation: (id: string): Promise<void> =>
    apiClient.delete(`/evaluations/${id}/`),
  
  getEvaluationGrades: (id: string): Promise<Grade[]> =>
    apiClient.get(`/evaluations/${id}/grades/`),
  
  bulkUpdateGrades: (evaluationId: string, grades: Partial<Grade>[]): Promise<Grade[]> =>
    apiClient.post(`/evaluations/${evaluationId}/bulk_update_grades/`, { grades }),

  // Notes individuelles
  getGrades: (params?: Record<string, any>): Promise<PaginatedResponse<Grade>> =>
    apiClient.get('/grades/', { params }),
  
  getGrade: (id: string): Promise<Grade> =>
    apiClient.get(`/grades/${id}/`),
  
  createGrade: (data: Partial<Grade>): Promise<Grade> =>
    apiClient.post('/grades/', data),
  
  updateGrade: (id: string, data: Partial<Grade>): Promise<Grade> =>
    apiClient.put(`/grades/${id}/`, data),
  
  deleteGrade: (id: string): Promise<void> =>
    apiClient.delete(`/grades/${id}/`),

  // Moyennes par matière
  getSubjectAverages: (params?: Record<string, any>): Promise<PaginatedResponse<SubjectAverage>> =>
    apiClient.get('/subject-averages/', { params }),
  
  getSubjectAverage: (id: string): Promise<SubjectAverage> =>
    apiClient.get(`/subject-averages/${id}/`),
  
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