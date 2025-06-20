/**
 * API client pour le module timetable (emploi du temps)
 */
import { client } from './client'
import type { 
  Subject,
  Room,
  TimeSlot,
  Schedule,
  ScheduleModification,
  ApiResponse,
  PaginatedResponse
} from '@/types'

export const timetableApi = {
  // Matières
  getSubjects: (params?: Record<string, any>): Promise<PaginatedResponse<Subject>> =>
    client.get('/subjects/', { params }),
  
  getSubject: (id: string): Promise<Subject> =>
    client.get(`/subjects/${id}/`),
  
  createSubject: (data: Partial<Subject>): Promise<Subject> =>
    client.post('/subjects/', data),
  
  updateSubject: (id: string, data: Partial<Subject>): Promise<Subject> =>
    client.put(`/subjects/${id}/`, data),
  
  deleteSubject: (id: string): Promise<void> =>
    client.delete(`/subjects/${id}/`),

  // Salles
  getRooms: (params?: Record<string, any>): Promise<PaginatedResponse<Room>> =>
    client.get('/rooms/', { params }),
  
  getRoom: (id: string): Promise<Room> =>
    client.get(`/rooms/${id}/`),
  
  createRoom: (data: Partial<Room>): Promise<Room> =>
    client.post('/rooms/', data),
  
  updateRoom: (id: string, data: Partial<Room>): Promise<Room> =>
    client.put(`/rooms/${id}/`, data),
  
  deleteRoom: (id: string): Promise<void> =>
    client.delete(`/rooms/${id}/`),
  
  getRoomSchedule: (roomId: string, date?: string): Promise<Schedule[]> =>
    client.get(`/rooms/${roomId}/schedule/`, { 
      params: date ? { date } : undefined 
    }),

  // Créneaux horaires
  getTimeSlots: (params?: Record<string, any>): Promise<PaginatedResponse<TimeSlot>> =>
    client.get('/time-slots/', { params }),
  
  getTimeSlot: (id: string): Promise<TimeSlot> =>
    client.get(`/time-slots/${id}/`),
  
  createTimeSlot: (data: Partial<TimeSlot>): Promise<TimeSlot> =>
    client.post('/time-slots/', data),
  
  updateTimeSlot: (id: string, data: Partial<TimeSlot>): Promise<TimeSlot> =>
    client.put(`/time-slots/${id}/`, data),
  
  deleteTimeSlot: (id: string): Promise<void> =>
    client.delete(`/time-slots/${id}/`),

  // Emplois du temps (Schedules)
  getSchedules: (params?: Record<string, any>): Promise<PaginatedResponse<Schedule>> =>
    client.get('/schedules/', { params }),
  
  getSchedule: (id: string): Promise<Schedule> =>
    client.get(`/schedules/${id}/`),
  
  createSchedule: (data: Partial<Schedule>): Promise<Schedule> =>
    client.post('/schedules/', data),
  
  updateSchedule: (id: string, data: Partial<Schedule>): Promise<Schedule> =>
    client.put(`/schedules/${id}/`, data),
  
  deleteSchedule: (id: string): Promise<void> =>
    client.delete(`/schedules/${id}/`),
  
  checkConflicts: (data: Partial<Schedule>): Promise<any> =>
    client.post('/schedules/check_conflicts/', data),

  // Emplois du temps par entité
  getTeacherSchedule: (teacherId: string, params?: Record<string, any>): Promise<Schedule[]> =>
    client.get('/schedules/by_teacher/', { 
      params: { teacher_id: teacherId, ...params } 
    }),
  
  getClassSchedule: (classId: string, params?: Record<string, any>): Promise<Schedule[]> =>
    client.get('/schedules/by_class/', { 
      params: { class_id: classId, ...params } 
    }),
  
  getStudentSchedule: (studentId: string, params?: Record<string, any>): Promise<Schedule[]> =>
    client.get('/schedules/by_student/', { 
      params: { student_id: studentId, ...params } 
    }),
  
  getRoomScheduleDetailed: (roomId: string, params?: Record<string, any>): Promise<Schedule[]> =>
    client.get('/schedules/by_room/', { 
      params: { room_id: roomId, ...params } 
    }),

  // Emplois du temps hebdomadaires
  getWeeklySchedule: (params: Record<string, any>): Promise<any> =>
    client.get('/schedules/weekly/', { params }),
  
  getTeacherWeeklySchedule: (teacherId: string, week?: string): Promise<any> =>
    client.get('/schedules/weekly/teacher/', { 
      params: { teacher_id: teacherId, week } 
    }),
  
  getClassWeeklySchedule: (classId: string, week?: string): Promise<any> =>
    client.get('/schedules/weekly/class/', { 
      params: { class_id: classId, week } 
    }),
  
  getStudentWeeklySchedule: (studentId: string, week?: string): Promise<any> =>
    client.get('/schedules/weekly/student/', { 
      params: { student_id: studentId, week } 
    }),

  // Modifications d'emploi du temps
  getScheduleModifications: (params?: Record<string, any>): Promise<PaginatedResponse<ScheduleModification>> =>
    client.get('/schedule-modifications/', { params }),
  
  getScheduleModification: (id: string): Promise<ScheduleModification> =>
    client.get(`/schedule-modifications/${id}/`),
  
  createScheduleModification: (data: Partial<ScheduleModification>): Promise<ScheduleModification> =>
    client.post('/schedule-modifications/', data),
  
  updateScheduleModification: (id: string, data: Partial<ScheduleModification>): Promise<ScheduleModification> =>
    client.put(`/schedule-modifications/${id}/`, data),
  
  deleteScheduleModification: (id: string): Promise<void> =>
    client.delete(`/schedule-modifications/${id}/`),

  // Actions spéciales
  duplicateSchedule: (scheduleId: string, targetWeek: string): Promise<Schedule[]> =>
    client.post(`/schedules/${scheduleId}/duplicate/`, { target_week: targetWeek }),
  
  bulkCreateSchedules: (schedules: Partial<Schedule>[]): Promise<Schedule[]> =>
    client.post('/schedules/bulk_create/', { schedules }),
  
  bulkUpdateSchedules: (schedules: Partial<Schedule>[]): Promise<Schedule[]> =>
    client.post('/schedules/bulk_update/', { schedules }),
  
  bulkDeleteSchedules: (ids: string[]): Promise<ApiResponse> =>
    client.post('/schedules/bulk_delete/', { ids }),

  // Statistiques et rapports
  getScheduleStatistics: (params?: Record<string, any>): Promise<any> =>
    client.get('/schedules/statistics/', { params }),
  
  getTeacherWorkload: (teacherId?: string): Promise<any> =>
    client.get('/schedules/teacher_workload/', { 
      params: teacherId ? { teacher_id: teacherId } : undefined 
    }),
  
  getRoomOccupancy: (roomId?: string): Promise<any> =>
    client.get('/schedules/room_occupancy/', { 
      params: roomId ? { room_id: roomId } : undefined 
    }),
  
  getConflictReport: (): Promise<any> =>
    client.get('/schedules/conflicts/'),

  // Import/Export
  exportSchedule: (params?: Record<string, any>): Promise<Blob> =>
    client.get('/schedules/export/', { 
      params, 
      responseType: 'blob' 
    }),
  
  importSchedule: (file: File): Promise<ApiResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/schedules/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Export formats spéciaux
  exportScheduleIcal: (params?: Record<string, any>): Promise<Blob> =>
    client.get('/schedules/export/ical/', { 
      params, 
      responseType: 'blob' 
    }),
  
  exportSchedulePdf: (params?: Record<string, any>): Promise<Blob> =>
    client.get('/schedules/export/pdf/', { 
      params, 
      responseType: 'blob' 
    })
}