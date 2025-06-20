/**
 * API client pour le module attendance (vie scolaire)
 */
import { apiClient } from './apiClient'
import type { 
  Attendance,
  AbsencePeriod,
  Sanction,
  StudentBehavior,
  AttendanceAlert,
  AttendanceSummary,
  AttendanceStatistics,
  AttendanceReport,
  ApiResponse,
  PaginatedResponse,
  MonthlyReport,
  AttendanceDashboard,
  TodayAbsences
} from '@/types'

export const attendanceApi = {
  // Présences/Absences
  getAttendances: async (params?: Record<string, string | number>): Promise<PaginatedResponse<Attendance>> =>
    (await apiClient.get('/attendances/', { params })).data,
  
  getAttendance: async (id: number): Promise<Attendance> =>
    (await apiClient.get(`/attendances/${id}/`)).data,
  
  createAttendance: async (data: Partial<Attendance>): Promise<Attendance> =>
    (await apiClient.post('/attendances/', data)).data,
  
  updateAttendance: async (id: number, data: Partial<Attendance>): Promise<Attendance> =>
    (await apiClient.put(`/attendances/${id}/`, data)).data,
  
  deleteAttendance: async (id: number): Promise<void> =>
    (await apiClient.delete(`/attendances/${id}/`)).data,

  // Appel en classe
  getClassAttendance: async (classId: number, date: string): Promise<Attendance[]> =>
    (await apiClient.get('/attendances/by_class/', { 
      params: { class_id: classId, date } 
    })).data,
  
  markClassAttendance: async (classId: number, date: string, attendances: Partial<Attendance>[]): Promise<Attendance[]> =>
    (await apiClient.post('/attendances/mark_class/', { 
      class_id: classId, 
      date, 
      attendances 
    })).data,
  
  bulkMarkAttendance: async (attendances: Partial<Attendance>[]): Promise<Attendance[]> =>
    (await apiClient.post('/attendances/bulk_mark/', { attendances })).data,

  // Présences par élève
  getStudentAttendance: async (studentId: number, params?: Record<string, string | number>): Promise<Attendance[]> =>
    (await apiClient.get('/attendances/by_student/', { 
      params: { student_id: studentId, ...params } 
    })).data,
  
  getStudentAttendanceSummary: async (studentId: number, period?: string): Promise<AttendanceSummary> =>
    (await apiClient.get('/attendances/student_summary/', { 
      params: { student_id: studentId, period } 
    })).data,

  // Périodes d'absence
  getAbsencePeriods: async (params?: Record<string, string | number>): Promise<PaginatedResponse<AbsencePeriod>> =>
    (await apiClient.get('/absence-periods/', { params })).data,
  
  getAbsencePeriod: async (id: number): Promise<AbsencePeriod> =>
    (await apiClient.get(`/absence-periods/${id}/`)).data,
  
  createAbsencePeriod: async (data: Partial<AbsencePeriod>): Promise<AbsencePeriod> =>
    (await apiClient.post('/absence-periods/', data)).data,
  
  updateAbsencePeriod: async (id: number, data: Partial<AbsencePeriod>): Promise<AbsencePeriod> =>
    (await apiClient.put(`/absence-periods/${id}/`, data)).data,
  
  deleteAbsencePeriod: async (id: number): Promise<void> =>
    (await apiClient.delete(`/absence-periods/${id}/`)).data,
  
  approveAbsencePeriod: async (id: number): Promise<AbsencePeriod> =>
    (await apiClient.post(`/absence-periods/${id}/approve/`)).data,
  
  rejectAbsencePeriod: async (id: number, reason?: string): Promise<AbsencePeriod> =>
    (await apiClient.post(`/absence-periods/${id}/reject/`, { reason })).data,

  // Sanctions
  getSanctions: async (params?: Record<string, string | number>): Promise<PaginatedResponse<Sanction>> =>
    (await apiClient.get('/sanctions/', { params })).data,
  
  getSanction: async (id: number): Promise<Sanction> =>
    (await apiClient.get(`/sanctions/${id}/`)).data,
  
  createSanction: async (data: Partial<Sanction>): Promise<Sanction> =>
    (await apiClient.post('/sanctions/', data)).data,
  
  updateSanction: async (id: number, data: Partial<Sanction>): Promise<Sanction> =>
    (await apiClient.put(`/sanctions/${id}/`, data)).data,
  
  deleteSanction: async (id: number): Promise<void> =>
    (await apiClient.delete(`/sanctions/${id}/`)).data,
  
  completeSanction: async (id: number): Promise<Sanction> =>
    (await apiClient.post(`/sanctions/${id}/complete/`)).data,

  // Comportement des élèves
  getStudentBehaviors: async (params?: Record<string, string | number>): Promise<PaginatedResponse<StudentBehavior>> =>
    (await apiClient.get('/behaviors/', { params })).data,
  
  getStudentBehavior: async (id: number): Promise<StudentBehavior> =>
    (await apiClient.get(`/behaviors/${id}/`)).data,
  
  createStudentBehavior: async (data: Partial<StudentBehavior>): Promise<StudentBehavior> =>
    (await apiClient.post('/behaviors/', data)).data,
  
  updateStudentBehavior: async (id: number, data: Partial<StudentBehavior>): Promise<StudentBehavior> =>
    (await apiClient.put(`/behaviors/${id}/`, data)).data,
  
  deleteStudentBehavior: async (id: number): Promise<void> =>
    (await apiClient.delete(`/behaviors/${id}/`)).data,
  
  getStudentBehaviorHistory: async (studentId: number, params?: Record<string, string | number>): Promise<StudentBehavior[]> =>
    (await apiClient.get('/behaviors/by_student/', { 
      params: { student_id: studentId, ...params } 
    })).data,

  // Alertes d'assiduité
  getAttendanceAlerts: async (params?: Record<string, string | number>): Promise<PaginatedResponse<AttendanceAlert>> =>
    (await apiClient.get('/alerts/', { params })).data,
  
  getAttendanceAlert: async (id: number): Promise<AttendanceAlert> =>
    (await apiClient.get(`/alerts/${id}/`)).data,
  
  createAttendanceAlert: async (data: Partial<AttendanceAlert>): Promise<AttendanceAlert> =>
    (await apiClient.post('/alerts/', data)).data,
  
  updateAttendanceAlert: async (id: number, data: Partial<AttendanceAlert>): Promise<AttendanceAlert> =>
    (await apiClient.put(`/alerts/${id}/`, data)).data,
  
  deleteAttendanceAlert: async (id: number): Promise<void> =>
    (await apiClient.delete(`/alerts/${id}/`)).data,
  
  acknowledgeAlert: async (id: number): Promise<AttendanceAlert> =>
    (await apiClient.post(`/alerts/${id}/acknowledge/`)).data,
  
  resolveAlert: async (id: number, resolution?: string): Promise<AttendanceAlert> =>
    (await apiClient.post(`/alerts/${id}/resolve/`, { resolution })).data,

  // Statistiques et rapports
  getAttendanceStatistics: async (params?: Record<string, string | number>): Promise<AttendanceStatistics> =>
    (await apiClient.get('/statistics/', { params })).data,
  
  getClassAttendanceReport: async (classId: number, period?: string): Promise<AttendanceReport> =>
    (await apiClient.get('/statistics/class_report/', { 
      params: { class_id: classId, period } 
    })).data,
  
  getStudentAttendanceReport: async (studentId: number, period?: string): Promise<AttendanceReport> =>
    (await apiClient.get('/statistics/student_report/', { 
      params: { student_id: studentId, period } 
    })).data,
  
  getAbsenteeismTrends: async (params?: Record<string, string | number>): Promise<AttendanceStatistics[]> =>
    (await apiClient.get('/statistics/absenteeism_trends/', { params })).data,
  
  getAttendanceComparison: async (params?: Record<string, string | number>): Promise<AttendanceStatistics> =>
    (await apiClient.get('/statistics/comparison/', { params })).data,

  // Actions automatiques
  triggerAttendanceCheck: async (): Promise<ApiResponse> =>
    (await apiClient.post('/check_alerts/')).data,
  
  generateMonthlyReport: async (month: string, year: number): Promise<MonthlyReport> =>
    (await apiClient.post('/generate_monthly_report/', { month, year })).data,
  
  autoJustifyMedicalAbsences: async (): Promise<ApiResponse> =>
    (await apiClient.post('/auto_justify_medical/')).data,

  // Import/Export
  exportAttendanceReport: async (params?: Record<string, string | number>): Promise<Blob> =>
    (await apiClient.get('/export/', { 
      params, 
      responseType: 'blob' 
    })).data,
  
  importAttendanceData: async (file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return (await apiClient.post('/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })).data
  },

  // Justificatifs
  uploadJustification: async (absenceId: number, file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return (await apiClient.post(`/absence-periods/${absenceId}/upload_justification/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })).data
  },
  
  downloadJustification: async (absenceId: number): Promise<Blob> =>
    (await apiClient.get(`/absence-periods/${absenceId}/justification/`, { responseType: 'blob' })).data,

  // Notifications
  sendAbsenceNotification: async (studentId: number, message?: string): Promise<ApiResponse> =>
    (await apiClient.post('/send_absence_notification/', { 
      student_id: studentId, 
      message 
    })).data,
  
  sendBehaviorAlert: async (behaviorId: number): Promise<ApiResponse> =>
    (await apiClient.post(`/behaviors/${behaviorId}/send_alert/`)).data,

  // Dashboard data
  getAttendanceDashboard: async (params?: Record<string, string | number>): Promise<AttendanceDashboard> =>
    (await apiClient.get('/dashboard/', { params })).data,
  
  getTodayAbsences: async (): Promise<TodayAbsences> =>
    (await apiClient.get('/today_absences/')).data,
  
  getPendingApprovals: async (): Promise<AbsencePeriod[]> =>
    (await apiClient.get('/pending_approvals/')).data,
  
  getRecentAlerts: async (limit?: number): Promise<AttendanceAlert[]> =>
    (await apiClient.get('/recent_alerts/', { 
      params: limit ? { limit } : undefined 
    })).data
}