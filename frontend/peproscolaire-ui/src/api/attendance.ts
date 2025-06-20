/**
 * API client pour le module attendance (vie scolaire)
 */
import { client } from './client'
import type { 
  Attendance,
  AbsencePeriod,
  Sanction,
  StudentBehavior,
  AttendanceAlert,
  ApiResponse,
  PaginatedResponse
} from '@/types'

export const attendanceApi = {
  // Présences/Absences
  getAttendances: (params?: Record<string, any>): Promise<PaginatedResponse<Attendance>> =>
    client.get('/attendances/', { params }),
  
  getAttendance: (id: string): Promise<Attendance> =>
    client.get(`/attendances/${id}/`),
  
  createAttendance: (data: Partial<Attendance>): Promise<Attendance> =>
    client.post('/attendances/', data),
  
  updateAttendance: (id: string, data: Partial<Attendance>): Promise<Attendance> =>
    client.put(`/attendances/${id}/`, data),
  
  deleteAttendance: (id: string): Promise<void> =>
    client.delete(`/attendances/${id}/`),

  // Appel en classe
  getClassAttendance: (classId: string, date: string): Promise<Attendance[]> =>
    client.get('/attendances/by_class/', { 
      params: { class_id: classId, date } 
    }),
  
  markClassAttendance: (classId: string, date: string, attendances: Partial<Attendance>[]): Promise<Attendance[]> =>
    client.post('/attendances/mark_class/', { 
      class_id: classId, 
      date, 
      attendances 
    }),
  
  bulkMarkAttendance: (attendances: Partial<Attendance>[]): Promise<Attendance[]> =>
    client.post('/attendances/bulk_mark/', { attendances }),

  // Présences par élève
  getStudentAttendance: (studentId: string, params?: Record<string, any>): Promise<Attendance[]> =>
    client.get('/attendances/by_student/', { 
      params: { student_id: studentId, ...params } 
    }),
  
  getStudentAttendanceSummary: (studentId: string, period?: string): Promise<any> =>
    client.get('/attendances/student_summary/', { 
      params: { student_id: studentId, period } 
    }),

  // Périodes d'absence
  getAbsencePeriods: (params?: Record<string, any>): Promise<PaginatedResponse<AbsencePeriod>> =>
    client.get('/absence-periods/', { params }),
  
  getAbsencePeriod: (id: string): Promise<AbsencePeriod> =>
    client.get(`/absence-periods/${id}/`),
  
  createAbsencePeriod: (data: Partial<AbsencePeriod>): Promise<AbsencePeriod> =>
    client.post('/absence-periods/', data),
  
  updateAbsencePeriod: (id: string, data: Partial<AbsencePeriod>): Promise<AbsencePeriod> =>
    client.put(`/absence-periods/${id}/`, data),
  
  deleteAbsencePeriod: (id: string): Promise<void> =>
    client.delete(`/absence-periods/${id}/`),
  
  approveAbsencePeriod: (id: string): Promise<AbsencePeriod> =>
    client.post(`/absence-periods/${id}/approve/`),
  
  rejectAbsencePeriod: (id: string, reason?: string): Promise<AbsencePeriod> =>
    client.post(`/absence-periods/${id}/reject/`, { reason }),

  // Sanctions
  getSanctions: (params?: Record<string, any>): Promise<PaginatedResponse<Sanction>> =>
    client.get('/sanctions/', { params }),
  
  getSanction: (id: string): Promise<Sanction> =>
    client.get(`/sanctions/${id}/`),
  
  createSanction: (data: Partial<Sanction>): Promise<Sanction> =>
    client.post('/sanctions/', data),
  
  updateSanction: (id: string, data: Partial<Sanction>): Promise<Sanction> =>
    client.put(`/sanctions/${id}/`, data),
  
  deleteSanction: (id: string): Promise<void> =>
    client.delete(`/sanctions/${id}/`),
  
  completeSanction: (id: string): Promise<Sanction> =>
    client.post(`/sanctions/${id}/complete/`),

  // Comportement des élèves
  getStudentBehaviors: (params?: Record<string, any>): Promise<PaginatedResponse<StudentBehavior>> =>
    client.get('/behaviors/', { params }),
  
  getStudentBehavior: (id: string): Promise<StudentBehavior> =>
    client.get(`/behaviors/${id}/`),
  
  createStudentBehavior: (data: Partial<StudentBehavior>): Promise<StudentBehavior> =>
    client.post('/behaviors/', data),
  
  updateStudentBehavior: (id: string, data: Partial<StudentBehavior>): Promise<StudentBehavior> =>
    client.put(`/behaviors/${id}/`, data),
  
  deleteStudentBehavior: (id: string): Promise<void> =>
    client.delete(`/behaviors/${id}/`),
  
  getStudentBehaviorHistory: (studentId: string, params?: Record<string, any>): Promise<StudentBehavior[]> =>
    client.get('/behaviors/by_student/', { 
      params: { student_id: studentId, ...params } 
    }),

  // Alertes d'assiduité
  getAttendanceAlerts: (params?: Record<string, any>): Promise<PaginatedResponse<AttendanceAlert>> =>
    client.get('/alerts/', { params }),
  
  getAttendanceAlert: (id: string): Promise<AttendanceAlert> =>
    client.get(`/alerts/${id}/`),
  
  createAttendanceAlert: (data: Partial<AttendanceAlert>): Promise<AttendanceAlert> =>
    client.post('/alerts/', data),
  
  updateAttendanceAlert: (id: string, data: Partial<AttendanceAlert>): Promise<AttendanceAlert> =>
    client.put(`/alerts/${id}/`, data),
  
  deleteAttendanceAlert: (id: string): Promise<void> =>
    client.delete(`/alerts/${id}/`),
  
  acknowledgeAlert: (id: string): Promise<AttendanceAlert> =>
    client.post(`/alerts/${id}/acknowledge/`),
  
  resolveAlert: (id: string, resolution?: string): Promise<AttendanceAlert> =>
    client.post(`/alerts/${id}/resolve/`, { resolution }),

  // Statistiques et rapports
  getAttendanceStatistics: (params?: Record<string, any>): Promise<any> =>
    client.get('/statistics/', { params }),
  
  getClassAttendanceReport: (classId: string, period?: string): Promise<any> =>
    client.get('/statistics/class_report/', { 
      params: { class_id: classId, period } 
    }),
  
  getStudentAttendanceReport: (studentId: string, period?: string): Promise<any> =>
    client.get('/statistics/student_report/', { 
      params: { student_id: studentId, period } 
    }),
  
  getAbsenteeismTrends: (params?: Record<string, any>): Promise<any> =>
    client.get('/statistics/absenteeism_trends/', { params }),
  
  getAttendanceComparison: (params?: Record<string, any>): Promise<any> =>
    client.get('/statistics/comparison/', { params }),

  // Actions automatiques
  triggerAttendanceCheck: (): Promise<ApiResponse> =>
    client.post('/check_alerts/'),
  
  generateMonthlyReport: (month: string, year: number): Promise<any> =>
    client.post('/generate_monthly_report/', { month, year }),
  
  autoJustifyMedicalAbsences: (): Promise<ApiResponse> =>
    client.post('/auto_justify_medical/'),

  // Import/Export
  exportAttendanceReport: (params?: Record<string, any>): Promise<Blob> =>
    client.get('/export/', { 
      params, 
      responseType: 'blob' 
    }),
  
  importAttendanceData: (file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Justificatifs
  uploadJustification: (absenceId: string, file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post(`/absence-periods/${absenceId}/upload_justification/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  downloadJustification: (absenceId: string): Promise<Blob> =>
    client.get(`/absence-periods/${absenceId}/justification/`, { responseType: 'blob' }),

  // Notifications
  sendAbsenceNotification: (studentId: string, message?: string): Promise<ApiResponse> =>
    client.post('/send_absence_notification/', { 
      student_id: studentId, 
      message 
    }),
  
  sendBehaviorAlert: (behaviorId: string): Promise<ApiResponse> =>
    client.post(`/behaviors/${behaviorId}/send_alert/`),

  // Dashboard data
  getAttendanceDashboard: (params?: Record<string, any>): Promise<any> =>
    client.get('/dashboard/', { params }),
  
  getTodayAbsences: (): Promise<any> =>
    client.get('/today_absences/'),
  
  getPendingApprovals: (): Promise<AbsencePeriod[]> =>
    client.get('/pending_approvals/'),
  
  getRecentAlerts: (limit?: number): Promise<AttendanceAlert[]> =>
    client.get('/recent_alerts/', { 
      params: limit ? { limit } : undefined 
    })
}