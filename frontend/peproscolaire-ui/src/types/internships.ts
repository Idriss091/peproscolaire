export interface Company {
  id: string
  name: string
  description?: string
  sector: string
  size: string
  contact_person?: string
  contact_email: string
  contact_phone?: string
  address: string
  city: string
  postal_code: string
  country: string
  website?: string
  linkedin_url?: string
  siret?: string
  is_partner: boolean
  is_active: boolean
  partnership_since?: string
  total_internships: number
  average_rating: number
  total_offers?: number
  created_at: string
  updated_at: string
  created_by_name?: string
}

export interface InternshipOffer {
  id: string
  company: string
  company_name: string
  company_details?: Partial<Company>
  title: string
  description: string
  offer_type: string
  status: string
  duration_value: number
  duration_type: string
  start_date: string
  end_date: string
  application_deadline: string
  department?: string
  supervisor_name?: string
  supervisor_email?: string
  supervisor_phone?: string
  required_level: string
  required_skills: string[]
  preferred_skills: string[]
  is_paid: boolean
  monthly_allowance?: number
  benefits: string[]
  remote_possible: boolean
  transport_provided: boolean
  meal_vouchers: boolean
  accommodation_help: boolean
  max_applications: number
  current_applications: number
  applications_count?: string
  can_apply: boolean
  created_at: string
  updated_at: string
  published_at?: string
  created_by_name?: string
}

export interface InternshipApplication {
  id: string
  student: string
  student_name?: string
  offer: string
  offer_title?: string
  company_name?: string
  status: string
  submitted_at?: string
  reviewed_at?: string
  response_at?: string
  cover_letter: string
  cv_file?: string
  portfolio_url?: string
  additional_documents: any[]
  motivation?: string
  availability_notes?: string
  special_requirements?: string
  company_notes?: string
  interview_date?: string
  interview_notes?: string
  created_at: string
  updated_at: string
}

export interface Internship {
  id: string
  application: string
  student: string
  student_name?: string
  company: string
  company_name?: string
  offer_title?: string
  academic_supervisor?: string
  academic_supervisor_name?: string
  company_supervisor: string
  company_supervisor_email: string
  start_date: string
  end_date: string
  actual_start_date?: string
  actual_end_date?: string
  status: string
  progress_percentage: number
  student_rating?: number
  company_rating?: number
  internship_agreement?: string
  final_report?: string
  company_evaluation?: string
  created_at: string
  updated_at: string
}

export interface InternshipVisit {
  id: string
  internship: string
  student_name?: string
  company_name?: string
  visitor: string
  visitor_name?: string
  visit_type: string
  status: string
  scheduled_date: string
  duration_minutes: number
  location: string
  participants: string[]
  visit_report?: string
  student_feedback?: string
  company_feedback?: string
  recommendations?: string
  overall_satisfaction?: number
  issues_identified: any[]
  follow_up_required: boolean
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface InternshipEvaluation {
  id: string
  internship: string
  student_name?: string
  company_name?: string
  evaluator: string
  evaluator_name?: string
  evaluator_type: string
  technical_skills: number
  soft_skills: number
  initiative: number
  reliability: number
  communication: number
  overall_rating: number
  strengths: string
  areas_for_improvement: string
  general_comments?: string
  would_recommend_student?: boolean
  would_recommend_company?: boolean
  created_at: string
  updated_at: string
}

export interface InternshipStats {
  total_applications: number
  pending_applications: number
  accepted_applications: number
  total_internships: number
  ongoing_internships: number
  completed_internships: number
  upcoming_internships: number
  current_internship?: {
    id: string
    company: string
    start_date: string
    end_date: string
    progress: number
  }
}

export interface InternshipSearch {
  query?: string
  sector?: string
  city?: string
  offer_type?: string
  is_paid?: boolean
  remote_possible?: boolean
  start_date_from?: string
  start_date_to?: string
  duration_min?: number
  duration_max?: number
}

export interface InternshipReport {
  period_start: string
  period_end: string
  total_offers: number
  total_applications: number
  total_internships: number
  success_rate: number
  average_duration: number
  top_companies: any[]
  sector_distribution: Record<string, number>
  monthly_trends: Record<string, any>
}