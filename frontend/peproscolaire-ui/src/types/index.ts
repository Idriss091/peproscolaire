// User types
export type UserType = 'student' | 'parent' | 'teacher' | 'admin' | 'superadmin'

export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  user_type: UserType
  is_active: boolean
  date_joined: string
  last_login: string | null
  profile?: UserProfile
  profile_picture?: string | null
  school?: School
}

export interface UserProfile {
  id: number
  user: number
  phone_number?: string
  address?: string
  date_of_birth?: string
  gender?: 'M' | 'F' | 'O'
  emergency_contact?: string
  emergency_phone?: string
  profile_picture?: string
  bio?: string
  preferences?: Record<string, any>
}

// Authentication
export interface LoginCredentials {
  username: string
  password: string
  user_type?: UserType
}

export interface AuthResponse {
  access: string
  refresh: string
  user: User
}

// School types
export interface School {
  id: number
  name: string
  school_type: 'college' | 'lycee'
  address: string
  postal_code: string
  city: string
  phone: string
  email: string
  website?: string
  logo?: string
  subdomain: string
  is_active: boolean
}

export interface AcademicYear {
  id: number
  school: number
  name: string
  start_date: string
  end_date: string
  is_current: boolean
}

export interface Class {
  id: number
  school: number
  academic_year: number
  name: string
  level: string
  capacity: number
  main_teacher?: number
}

// Timetable types
export interface TimeSlot {
  id: number
  school: number
  name: string
  start_time: string
  end_time: string
  day_of_week: number
  slot_type: 'course' | 'break' | 'lunch'
}

export interface Subject {
  id: number
  name: string
  code: string
  description?: string
  color?: string
  school: number
}

export interface Room {
  id: number
  school: number
  name: string
  building?: string
  floor?: number
  capacity: number
  room_type: 'classroom' | 'lab' | 'gym' | 'library' | 'other'
  equipment?: string[]
}

export interface Schedule {
  id: number
  time_slot: number
  subject: number
  teacher: number
  class_group: number
  room: number
  academic_year: number
  is_active: boolean
  recurrence_type: 'weekly' | 'biweekly' | 'custom'
  effective_date: string
  end_date?: string
}

// Attendance types
export interface Attendance {
  id: number
  student: number
  schedule: number
  date: string
  status: 'present' | 'absent' | 'late' | 'excused'
  arrival_time?: string
  notes?: string
  marked_by: number
  marked_at: string
}

export interface AbsencePeriod {
  id: number
  student: number
  start_date: string
  end_date: string
  reason: string
  justification?: string
  justified: boolean
  justification_document?: string
  created_by: number
}

// Grades types
export interface EvaluationType {
  id: number
  school: number
  name: string
  code: string
  coefficient: number
  category: 'exam' | 'quiz' | 'homework' | 'project' | 'participation' | 'other'
}

export interface Grade {
  id: number
  student: number
  evaluation: number
  value: number
  max_value: number
  coefficient: number
  comment?: string
  graded_by: number
  graded_at: string
}

export interface Evaluation {
  id: number
  name: string
  evaluation_type: number
  subject: number
  class_group: number
  grading_period: number
  date: string
  max_score: number
  coefficient: number
  description?: string
  visible_to_students: boolean
  visible_to_parents: boolean
}

export interface Competence {
  id: number
  name: string
  code: string
  subject: number
  level: string
  description?: string
  skills: string[]
}

export interface CompetenceGrade {
  id: number
  student: number
  competence: number
  evaluation: number
  mastery_level: 'not_acquired' | 'in_progress' | 'acquired' | 'expert'
  comment?: string
  graded_by: number
  graded_at: string
}

export interface SubjectAverage {
  id: number
  student: number
  subject: number
  grading_period: number
  average: number
  coefficient_total: number
  grade_count: number
  class_average?: number
  class_rank?: number
}

export interface Bulletin {
  id: number
  student: number
  grading_period: number
  general_average: number
  class_average: number
  rank: number
  appreciations: BulletinAppreciation[]
  teacher_comments?: string
  head_teacher_comment?: string
  generated_at: string
  is_published: boolean
}

export interface BulletinAppreciation {
  id: number
  subject: number
  average: number
  appreciation: string
  teacher: number
}

// Homework types
export interface Homework {
  id: number
  title: string
  description: string
  subject: number
  class_group: number
  teacher: number
  given_date: string
  due_date: string
  estimated_duration: number
  homework_type: 'exercise' | 'reading' | 'project' | 'revision' | 'other'
  attachments?: HomeworkAttachment[]
  is_graded: boolean
  visible_to_parents: boolean
}

export interface HomeworkAttachment {
  id: number
  homework: number
  file: string
  file_name: string
  file_size: number
  uploaded_at: string
}

export interface HomeworkType {
  id: number
  name: string
  code: string
  description?: string
  color?: string
  is_graded: boolean
  estimated_duration?: number
}

export interface HomeworkSubmission {
  id: number
  homework: number
  student: number
  submitted_at: string
  content?: string
  files: HomeworkSubmissionFile[]
  status: 'draft' | 'submitted' | 'late' | 'graded'
  grade?: number
  teacher_feedback?: string
  graded_at?: string
  graded_by?: number
}

export interface HomeworkSubmissionFile {
  id: number
  submission: number
  file: string
  file_name: string
  file_size: number
  uploaded_at: string
}

// Messaging types
export interface Message {
  id: number
  sender: number
  subject: string
  body: string
  sent_at: string
  is_draft: boolean
  is_system_message: boolean
  priority: 'low' | 'normal' | 'high'
  thread?: number
  attachments?: MessageAttachment[]
  recipients: MessageRecipient[]
}

export interface MessageRecipient {
  id: number
  message: number
  recipient: number
  is_read: boolean
  read_at?: string
  folder: 'inbox' | 'sent' | 'draft' | 'trash' | 'archive'
  is_starred: boolean
  labels: string[]
}

export interface MessageAttachment {
  id: number
  message: number
  file: string
  file_name: string
  file_size: number
  file_type: string
}

// Risk Detection types
export interface RiskProfile {
  id: number
  student: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  overall_score: number
  last_updated: string
  factors: RiskFactor[]
  is_active: boolean
  acknowledged_by?: number
  acknowledged_at?: string
}

export interface RiskFactor {
  category: string
  score: number
  weight: number
  details: Record<string, any>
}

export interface Alert {
  id: number
  risk_profile: number
  alert_type: string
  severity: 'info' | 'warning' | 'critical'
  message: string
  created_at: string
  is_resolved: boolean
  resolved_by?: number
  resolved_at?: string
  resolution_notes?: string
}

export interface AlertConfiguration {
  id: number
  alert_type: string
  name: string
  description?: string
  severity_threshold: number
  is_enabled: boolean
  notification_channels: string[]
  escalation_rules?: {
    time_minutes: number
    escalate_to: string[]
  }[]
  created_at: string
  updated_at: string
}

// Common types
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  detail?: string
  [field: string]: any
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

// Alias pour compatibilité
export type APIResponse<T = any> = ApiResponse<T>

// Import et export des types chatbot
export type { ChatbotConversation as Conversation } from './chatbot'
export type { ChatbotMessage, ChatbotResponse, QuickReply } from './chatbot'

// Attendance types
export interface AttendanceAlert {
  id: number
  student: number
  alert_type: string
  message: string
  created_at: string
  is_resolved: boolean
}

export interface AttendanceSummary {
  total_days: number
  present_days: number
  absent_days: number
  late_days: number
  excused_days: number
  attendance_rate: number
  punctuality_rate: number
  recent_absences: Attendance[]
  absence_trends: {
    weekly: number[]
    monthly: number[]
  }
}

export interface AttendanceStatistics {
  period: string
  class_average: number
  student_rank?: number
  comparison_data: {
    better_than_percent: number
    attendance_percentile: number
  }
}

export interface AttendanceReport {
  period: string
  summary: AttendanceSummary
  statistics: AttendanceStatistics
  charts_data: {
    daily_attendance: Array<{ date: string; status: string }>
    weekly_trends: Array<{ week: string; rate: number }>
  }
}

export interface StudentBehavior {
  id: number
  student: number
  behavior_type: string
  description: string
  severity: 'low' | 'medium' | 'high'
  date: string
  teacher: number
}

export interface Sanction {
  id: number
  student: number
  sanction_type: string
  description: string
  start_date: string
  end_date?: string
  is_active: boolean
}

// Tenant types
export interface Tenant {
  id: number
  schema_name: string
  domain_url: string
  school: School
  primary_color: string
  secondary_color: string
  logo_url?: string
  favicon_url?: string
  is_active: boolean
  created_on: string
  max_students: number
  max_storage_gb: number
  modules_enabled: Record<string, boolean>
}

export interface TenantTheme {
  primaryColor: string
  secondaryColor: string
  logoUrl?: string
  schoolName: string
}

// Additional attendance types
export interface MonthlyReport {
  month: string
  year: number
  total_students: number
  attendance_summary: AttendanceSummary
  class_reports: Array<{
    class_id: number
    class_name: string
    attendance_rate: number
    absent_students: number
  }>
  generated_at: string
}

export interface AttendanceDashboard {
  today_summary: {
    total_students: number
    present_count: number
    absent_count: number
    late_count: number
    attendance_rate: number
  }
  recent_alerts: AttendanceAlert[]
  weekly_trends: Array<{
    date: string
    attendance_rate: number
  }>
  top_absent_classes: Array<{
    class_name: string
    absent_count: number
  }>
}

export interface TodayAbsences {
  date: string
  total_absences: number
  excused_absences: number
  unexcused_absences: number
  students: Array<{
    id: number
    first_name: string
    last_name: string
    class_name: string
    absence_type: string
    reason?: string
  }>
}