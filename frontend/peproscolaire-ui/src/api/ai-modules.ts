import { api } from './client'

// Types pour les modules IA
export interface AppreciationOptions {
  type: 'bulletin' | 'conseil_classe' | 'parents' | 'orientation'
  tone: 'bienveillant' | 'neutre' | 'motivant' | 'ferme'
  length: 'courte' | 'standard' | 'détaillée'
  focus_areas?: string[]
  temperature?: number
  max_tokens?: number
  max_retries?: number
}

export interface AppreciationResult {
  content: string
  confidence: number
  metadata: {
    type: string
    tone: string
    length: string
    generated_at: string
    model_version: string
    is_default?: boolean
  }
}

export interface GenerateAppreciationRequest {
  student_id: string
  subject_id: string
  period_id: string
  options?: AppreciationOptions
}

export interface GenerateMultipleAppreciationsRequest {
  class_id?: string
  student_ids?: string[]
  subject_id: string
  period_id: string
  options?: AppreciationOptions
}

export interface RiskPrediction {
  dropout_probability: number
  risk_level: string
  risk_score: number
  main_risk_factors: Array<{
    factor: string
    value: number
    importance: number
    impact: string
  }>
  recommendations: Array<{
    priority: string
    action: string
    details: string
  }>
}

export interface ModelStatus {
  name: string
  status: 'active' | 'error' | 'training'
  performance?: {
    accuracy?: number
    precision?: number
    recall?: number
    f1_score?: number
    auc?: number
  }
  last_training?: string
  features_count?: number
  training_samples?: number | string
}

export interface AIModelStatusResponse {
  models: {
    dropout_risk: ModelStatus
    appreciation_generator: ModelStatus
  }
  global_metrics: {
    total_profiles: number
    high_risk_count: number
    average_risk_score: number
    last_update: string
  }
  system_status: {
    total_profiles: number
    high_risk_students: number
    average_risk_score: number
    last_analysis_update: string
  }
}

export interface DashboardMetrics {
  model_performance: {
    accuracy: number
    precision: number
    recall: number
    f1_score: number
    test_samples: number
  }
  risk_distribution: {
    very_low: number
    low: number
    moderate: number
    high: number
    critical: number
  }
  average_risk_score: number
  total_profiles: number
  high_risk_count: number
  recent_alerts: number
  profiles_analyzed_today: number
  interventions_active: number
  last_update: string
}

// Service API pour les modules IA
export const aiModulesAPI = {
  // Génération d'appréciations
  async generateAppreciation(request: GenerateAppreciationRequest) {
    const response = await api.post<{
      success: boolean
      appreciation: AppreciationResult
      student: { id: string; name: string }
      subject: { id: string; name: string }
      period: { id: string; name: string }
      average: number | null
    }>('/ai-analytics/ai/appreciation/generate/', request)
    return response.data
  },

  async generateMultipleAppreciations(request: GenerateMultipleAppreciationsRequest) {
    const response = await api.post<{
      success: boolean
      total_students: number
      successful_generations: number
      failed_generations: number
      results: Array<{
        student_id: string
        appreciation: AppreciationResult | null
        status: 'success' | 'error'
        error?: string
      }>
      options_used: AppreciationOptions
    }>('/ai-analytics/ai/appreciation/generate-multiple/', request)
    return response.data
  },

  // Analyse de risque et prédictions
  async predictStudentRisk(student_id: string) {
    const response = await api.post<{
      student: { id: string; name: string }
      prediction: RiskPrediction
      data_collected: {
        analysis_date: string
        features_count: number
      }
    }>('/ai-analytics/ai/prediction/risk/', { student_id })
    return response.data
  },

  // Status et métriques des modèles IA
  async getModelStatus() {
    const response = await api.get<AIModelStatusResponse>('/ai-analytics/ai/model/status/')
    return response.data
  },

  async getDashboardMetrics() {
    const response = await api.get<DashboardMetrics>('/ai-analytics/ai/dashboard/metrics/')
    return response.data
  },

  // Entraînement des modèles (admin only)
  async trainModel(model_type: 'dropout_risk' | 'performance_prediction', force_retrain = false) {
    const response = await api.post<{
      message: string
      task_id: string
      force_retrain: boolean
    }>('/ai-analytics/ai/model/train/', { 
      model_type, 
      force_retrain 
    })
    return response.data
  },

  // Gestion des profils de risque
  async getRiskProfiles(params?: {
    risk_level?: string[]
    is_monitored?: boolean
    min_risk_score?: number
    max_risk_score?: number
    student?: string
    academic_year?: string
    assigned_to?: string
    search?: string
    page?: number
    page_size?: number
  }) {
    const response = await api.get('/ai-analytics/risk-profiles/', { params })
    return response.data
  },

  async getRiskProfile(id: string) {
    const response = await api.get(`/ai-analytics/risk-profiles/${id}/`)
    return response.data
  },

  async analyzeRiskProfile(id: string) {
    const response = await api.post(`/ai-analytics/risk-profiles/${id}/analyze/`)
    return response.data
  },

  async startMonitoring(id: string, assigned_to?: string) {
    const response = await api.post(`/ai-analytics/risk-profiles/${id}/start_monitoring/`, {
      assigned_to
    })
    return response.data
  },

  async getRiskProfileHistory(id: string) {
    const response = await api.get(`/ai-analytics/risk-profiles/${id}/history/`)
    return response.data
  },

  async getRiskProfileRecommendations(id: string) {
    const response = await api.get(`/ai-analytics/risk-profiles/${id}/recommendations/`)
    return response.data
  },

  // Alertes
  async getAlerts(params?: {
    is_acknowledged?: boolean
    priority?: string
    risk_profile__student?: string
    page?: number
    page_size?: number
  }) {
    const response = await api.get('/ai-analytics/alerts/', { params })
    return response.data
  },

  async acknowledgeAlert(id: string, actions_taken?: string) {
    const response = await api.post(`/ai-analytics/alerts/${id}/acknowledge/`, {
      actions_taken
    })
    return response.data
  },

  async markAlertAsRead(id: string) {
    const response = await api.post(`/ai-analytics/alerts/${id}/mark_read/`)
    return response.data
  },

  async getAlertsDashboard() {
    const response = await api.get('/ai-analytics/alerts/dashboard/')
    return response.data
  },

  // Plans d'intervention
  async getInterventionPlans(params?: {
    status?: string
    coordinator?: string
    risk_profile__student?: string
    page?: number
    page_size?: number
  }) {
    const response = await api.get('/ai-analytics/intervention-plans/', { params })
    return response.data
  },

  async getInterventionPlan(id: string) {
    const response = await api.get(`/ai-analytics/intervention-plans/${id}/`)
    return response.data
  },

  async createInterventionPlan(data: {
    risk_profile: string
    title: string
    description: string
    start_date: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    resources_needed?: string
    success_criteria?: string
    evaluation_frequency?: 'weekly' | 'biweekly' | 'monthly'
  }) {
    const response = await api.post('/ai-analytics/intervention-plans/', data)
    return response.data
  },

  async updateInterventionPlan(id: string, data: Partial<{
    title: string
    description: string
    status: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    resources_needed: string
    success_criteria: string
    outcomes: string
    effectiveness_score: number
  }>) {
    const response = await api.patch(`/ai-analytics/intervention-plans/${id}/`, data)
    return response.data
  },

  async addActionToInterventionPlan(planId: string, data: {
    action_type: string
    title: string
    description: string
    responsible?: string
    scheduled_date: string
    scheduled_time?: string
    duration_minutes?: number
  }) {
    const response = await api.post(`/ai-analytics/intervention-plans/${planId}/add_action/`, data)
    return response.data
  },

  async evaluateInterventionEffectiveness(id: string, data: {
    outcomes: string
    effectiveness_score: number
  }) {
    const response = await api.post(`/ai-analytics/intervention-plans/${id}/evaluate_effectiveness/`, data)
    return response.data
  },

  async getMyInterventions() {
    const response = await api.get('/ai-analytics/intervention-plans/my_interventions/')
    return response.data
  },

  // Actions d'intervention
  async getInterventionActions(params?: {
    intervention_plan?: string
    responsible?: string
    completed?: boolean
    action_type?: string
    page?: number
    page_size?: number
  }) {
    const response = await api.get('/ai-analytics/intervention-actions/', { params })
    return response.data
  },

  async completeInterventionAction(id: string, data: {
    notes?: string
    impact_assessment?: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative'
  }) {
    const response = await api.post(`/ai-analytics/intervention-actions/${id}/complete/`, data)
    return response.data
  },

  async getInterventionActionsCalendar(start_date?: string, end_date?: string) {
    const params: any = {}
    if (start_date) params.start_date = start_date
    if (end_date) params.end_date = end_date
    
    const response = await api.get('/ai-analytics/intervention-actions/calendar/', { params })
    return response.data
  },

  // Dashboard et statistiques
  async getRiskDashboard() {
    const response = await api.get('/ai-analytics/dashboard/')
    return response.data
  },

  async getStudentRiskHistory(student_id: string) {
    const response = await api.get(`/ai-analytics/students/${student_id}/history/`)
    return response.data
  },

  async getClassRiskReport(class_id: string) {
    const response = await api.get(`/ai-analytics/classes/${class_id}/report/`)
    return response.data
  },

  async getRiskStatistics(period_days = 30) {
    const response = await api.get('/ai-analytics/statistics/', {
      params: { period_days }
    })
    return response.data
  },

  // Analyse déclenchement
  async triggerRiskAnalysis(data: {
    student_id?: string
    class_id?: string
    force_update?: boolean
  }) {
    const response = await api.post('/ai-analytics/analysis/trigger/', data)
    return response.data
  },

  async triggerBulkAnalysis(type: 'daily' | 'patterns') {
    const response = await api.post('/ai-analytics/analysis/bulk/', { type })
    return response.data
  }
}

export default aiModulesAPI