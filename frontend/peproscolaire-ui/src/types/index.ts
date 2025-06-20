// User types
export type UserType = 'student' | 'parent' | 'teacher' | 'admin' | 'superadmin'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  user_type: UserType
  is_active: boolean
  date_joined: string
  last_login: string | null
  profile?: UserProfile
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