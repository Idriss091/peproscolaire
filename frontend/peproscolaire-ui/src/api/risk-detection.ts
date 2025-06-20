import { apiClient, apiRequest } from './client'
import type {
  RiskProfile,
  Alert,
  AlertConfiguration,
  InterventionPlan,
  InterventionAction,
  DashboardStats,
  PaginatedResponse,
  FilterOptions
} from '@/types'

export interface RiskAnalysisRequest {
  student_id?: string
  class_id?: string
  force_update?: boolean
}

export interface InterventionPlanCreate {
  risk_profile: string
  title: string
  description: string
  coordinator?: string
  participants?: string[]
  start_date: string
  end_date: string
  objectives: any[]
  planned_actions: any[]
  resources_needed?: string
  success_criteria?: string
  evaluation_frequency?: 'weekly' | 'biweekly' | 'monthly'
  actions?: Partial<InterventionAction>[]
}

export interface InterventionEffectiveness {
  intervention_plan_id: string
  effectiveness_score: number
  outcomes: string
  recommendations?: string[]
}

class RiskDetectionAPI {
  private readonly basePath = '/ai-analytics'

  // Profils de risque
  async getRiskProfiles(filters?: FilterOptions) {
    return apiRequest(async () => {
      return await apiClient.get<PaginatedResponse<RiskProfile>>(
        `${this.basePath}/risk-profiles/`,
        filters
      )
    })
  }

  async getRiskProfile(id: string) {
    return apiRequest(async () => {
      return await apiClient.get<RiskProfile>(`${this.basePath}/risk-profiles/${id}/`)
    })
  }

  async createRiskProfile(data: { student: string; academic_year: string }) {
    return apiRequest(async () => {
      return await apiClient.post<RiskProfile>(`${this.basePath}/risk-profiles/`, data)
    })
  }

  async analyzeRiskProfile(id: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; profile_id: string }>(
        `${this.basePath}/risk-profiles/${id}/analyze/`
      )
    })
  }

  async startMonitoring(id: string, assigned_to?: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; profile: RiskProfile }>(
        `${this.basePath}/risk-profiles/${id}/start_monitoring/`,
        { assigned_to }
      )
    })
  }

  async getRiskHistory(id: string) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/risk-profiles/${id}/history/`)
    })
  }

  async getRecommendations(id: string) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/risk-profiles/${id}/recommendations/`)
    })
  }

  // Alertes
  async getAlerts(filters?: FilterOptions) {
    return apiRequest(async () => {
      return await apiClient.get<PaginatedResponse<Alert>>(
        `${this.basePath}/alerts/`,
        filters
      )
    })
  }

  async getAlert(id: string) {
    return apiRequest(async () => {
      return await apiClient.get<Alert>(`${this.basePath}/alerts/${id}/`)
    })
  }

  async acknowledgeAlert(id: string, actions_taken?: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; alert: Alert }>(
        `${this.basePath}/alerts/${id}/acknowledge/`,
        { actions_taken }
      )
    })
  }

  async markAlertRead(id: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string }>(
        `${this.basePath}/alerts/${id}/mark_read/`
      )
    })
  }

  async getAlertsDashboard() {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/alerts/dashboard/`)
    })
  }

  // Configurations d'alerte
  async getAlertConfigurations() {
    return apiRequest(async () => {
      return await apiClient.get<PaginatedResponse<AlertConfiguration>>(
        `${this.basePath}/alert-configurations/`
      )
    })
  }

  async createAlertConfiguration(data: Partial<AlertConfiguration>) {
    return apiRequest(async () => {
      return await apiClient.post<AlertConfiguration>(
        `${this.basePath}/alert-configurations/`,
        data
      )
    })
  }

  async updateAlertConfiguration(id: string, data: Partial<AlertConfiguration>) {
    return apiRequest(async () => {
      return await apiClient.patch<AlertConfiguration>(
        `${this.basePath}/alert-configurations/${id}/`,
        data
      )
    })
  }

  async testAlertConfiguration(id: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; alert?: Alert }>(
        `${this.basePath}/alert-configurations/${id}/test_alert/`
      )
    })
  }

  // Plans d'intervention
  async getInterventionPlans(filters?: FilterOptions) {
    return apiRequest(async () => {
      return await apiClient.get<PaginatedResponse<InterventionPlan>>(
        `${this.basePath}/intervention-plans/`,
        filters
      )
    })
  }

  async getInterventionPlan(id: string) {
    return apiRequest(async () => {
      return await apiClient.get<InterventionPlan>(`${this.basePath}/intervention-plans/${id}/`)
    })
  }

  async createInterventionPlan(data: InterventionPlanCreate) {
    return apiRequest(async () => {
      return await apiClient.post<InterventionPlan>(
        `${this.basePath}/intervention-plans/`,
        data
      )
    })
  }

  async updateInterventionPlan(id: string, data: Partial<InterventionPlan>) {
    return apiRequest(async () => {
      return await apiClient.patch<InterventionPlan>(
        `${this.basePath}/intervention-plans/${id}/`,
        data
      )
    })
  }

  async addActionToPlan(id: string, actionData: Partial<InterventionAction>) {
    return apiRequest(async () => {
      return await apiClient.post<InterventionAction>(
        `${this.basePath}/intervention-plans/${id}/add_action/`,
        actionData
      )
    })
  }

  async evaluateEffectiveness(id: string, data: InterventionEffectiveness) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; plan: InterventionPlan }>(
        `${this.basePath}/intervention-plans/${id}/evaluate_effectiveness/`,
        data
      )
    })
  }

  async getMyInterventions() {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/intervention-plans/my_interventions/`)
    })
  }

  // Actions d'intervention
  async getInterventionActions(filters?: FilterOptions) {
    return apiRequest(async () => {
      return await apiClient.get<PaginatedResponse<InterventionAction>>(
        `${this.basePath}/intervention-actions/`,
        filters
      )
    })
  }

  async completeAction(id: string, notes?: string, impact_assessment?: string) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; action: InterventionAction }>(
        `${this.basePath}/intervention-actions/${id}/complete/`,
        { notes, impact_assessment }
      )
    })
  }

  async getActionsCalendar(start_date?: string, end_date?: string) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/intervention-actions/calendar/`, {
        start_date,
        end_date
      })
    })
  }

  // Dashboard et analyses
  async getDashboard() {
    return apiRequest(async () => {
      return await apiClient.get<DashboardStats>(`${this.basePath}/dashboard/`)
    })
  }

  async triggerRiskAnalysis(data: RiskAnalysisRequest) {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; tasks: string[] }>(
        `${this.basePath}/analysis/trigger/`,
        data
      )
    })
  }

  async getStudentRiskHistory(studentId: string) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/students/${studentId}/history/`)
    })
  }

  async getClassRiskReport(classId: string) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/classes/${classId}/report/`)
    })
  }

  async bulkRiskAnalysis(type: 'daily' | 'patterns') {
    return apiRequest(async () => {
      return await apiClient.post<{ message: string; task_id: string }>(
        `${this.basePath}/analysis/bulk/`,
        { type }
      )
    })
  }

  async getRiskStatistics(period_days?: number) {
    return apiRequest(async () => {
      return await apiClient.get<any>(`${this.basePath}/statistics/`, {
        period_days
      })
    })
  }
}

export const riskDetectionAPI = new RiskDetectionAPI()