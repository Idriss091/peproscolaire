/**
 * API client pour le module schools
 */
import { client } from './client'
import type { 
  School, 
  AcademicYear, 
  Level, 
  Class, 
  StudentClassEnrollment,
  ApiResponse,
  PaginatedResponse
} from '@/types'

// Schools API
export const schoolsApi = {
  // Établissements
  getSchools: (params?: Record<string, any>): Promise<PaginatedResponse<School>> =>
    client.get('/schools/', { params }),
  
  getSchool: (id: string): Promise<School> =>
    client.get(`/schools/${id}/`),
  
  createSchool: (data: Partial<School>): Promise<School> =>
    client.post('/schools/', data),
  
  updateSchool: (id: string, data: Partial<School>): Promise<School> =>
    client.put(`/schools/${id}/`, data),
  
  deleteSchool: (id: string): Promise<void> =>
    client.delete(`/schools/${id}/`),
  
  getSchoolStatistics: (id: string): Promise<any> =>
    client.get(`/schools/${id}/statistics/`),

  // Années scolaires
  getAcademicYears: (params?: Record<string, any>): Promise<PaginatedResponse<AcademicYear>> =>
    client.get('/academic-years/', { params }),
  
  getAcademicYear: (id: string): Promise<AcademicYear> =>
    client.get(`/academic-years/${id}/`),
  
  createAcademicYear: (data: Partial<AcademicYear>): Promise<AcademicYear> =>
    client.post('/academic-years/', data),
  
  updateAcademicYear: (id: string, data: Partial<AcademicYear>): Promise<AcademicYear> =>
    client.put(`/academic-years/${id}/`, data),
  
  deleteAcademicYear: (id: string): Promise<void> =>
    client.delete(`/academic-years/${id}/`),
  
  getCurrentAcademicYear: (schoolId?: string): Promise<AcademicYear> =>
    client.get('/academic-years/current/', { 
      params: schoolId ? { school_id: schoolId } : undefined 
    }),

  // Niveaux
  getLevels: (params?: Record<string, any>): Promise<Level[]> =>
    client.get('/levels/', { params }),
  
  getLevel: (id: string): Promise<Level> =>
    client.get(`/levels/${id}/`),

  // Classes
  getClasses: (params?: Record<string, any>): Promise<PaginatedResponse<Class>> =>
    client.get('/classes/', { params }),
  
  getClass: (id: string): Promise<Class> =>
    client.get(`/classes/${id}/`),
  
  createClass: (data: Partial<Class>): Promise<Class> =>
    client.post('/classes/', data),
  
  updateClass: (id: string, data: Partial<Class>): Promise<Class> =>
    client.put(`/classes/${id}/`, data),
  
  deleteClass: (id: string): Promise<void> =>
    client.delete(`/classes/${id}/`),
  
  getClassStudents: (id: string): Promise<StudentClassEnrollment[]> =>
    client.get(`/classes/${id}/students/`),
  
  addStudentToClass: (classId: string, studentId: string): Promise<StudentClassEnrollment> =>
    client.post(`/classes/${classId}/add_student/`, { student_id: studentId }),
  
  removeStudentFromClass: (classId: string, studentId: string): Promise<ApiResponse> =>
    client.delete(`/classes/${classId}/remove_student/`, { data: { student_id: studentId } }),

  // Inscriptions
  getEnrollments: (params?: Record<string, any>): Promise<PaginatedResponse<StudentClassEnrollment>> =>
    client.get('/enrollments/', { params }),
  
  getEnrollment: (id: string): Promise<StudentClassEnrollment> =>
    client.get(`/enrollments/${id}/`),
  
  createEnrollment: (data: Partial<StudentClassEnrollment>): Promise<StudentClassEnrollment> =>
    client.post('/enrollments/', data),
  
  updateEnrollment: (id: string, data: Partial<StudentClassEnrollment>): Promise<StudentClassEnrollment> =>
    client.put(`/enrollments/${id}/`, data),
  
  deleteEnrollment: (id: string): Promise<void> =>
    client.delete(`/enrollments/${id}/`)
}