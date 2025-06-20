import { apiClient } from './apiClient'

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
  student_id: number
  subject_id: number
  period_id: number
  options?: AppreciationOptions
}

export interface GenerateMultipleAppreciationsRequest {
  class_id?: number
  student_ids?: number[]
  subject_id: number
  period_id: number
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
  async generateAppreciation(request: GenerateAppreciationRequest): Promise<{
    success: boolean
    appreciation: AppreciationResult
    student: { id: number; name: string }
    subject: { id: number; name: string }
    period: { id: number; name: string }
    average: number | null
  }> {
    const response = await apiClient.post<{
      success: boolean
      appreciation: AppreciationResult
      student: { id: number; name: string }
      subject: { id: number; name: string }
      period: { id: number; name: string }
      average: number | null
    }>('/ai-analytics/ai/appreciation/generate/', request)
    return response.data
  },

  async generateMultipleAppreciations(request: GenerateMultipleAppreciationsRequest): Promise<{
    success: boolean
    total_students: number
    successful_generations: number
    failed_generations: number
    results: Array<{
      student_id: number
      appreciation: AppreciationResult | null
      status: 'success' | 'error'
      error?: string
    }>
    options_used: AppreciationOptions
  }> {
    const response = await apiClient.post<{
      success: boolean
      total_students: number
      successful_generations: number
      failed_generations: number
      results: Array<{
        student_id: number
        appreciation: AppreciationResult | null
        status: 'success' | 'error'
        error?: string
      }>
      options_used: AppreciationOptions
    }>('/ai-analytics/ai/appreciation/generate-multiple/', request)
    return response.data
  },

  // Analyse de risque et prédictions
  async predictStudentRisk(student_id: number): Promise<{
    student: { id: number; name: string }
    prediction: RiskPrediction
    data_collected: {
      analysis_date: string
      features_count: number
    }
  }> {
    const response = await apiClient.post<{
      student: { id: number; name: string }
      prediction: RiskPrediction
      data_collected: {
        analysis_date: string
        features_count: number
      }
    }>('/ai-analytics/ai/prediction/risk/', { student_id })
    return response.data
  },

  // Status et métriques des modèles IA
  async getModelStatus(): Promise<AIModelStatusResponse> {
    const response = await apiClient.get<AIModelStatusResponse>('/ai-analytics/ai/model/status/')
    return response.data
  },

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.get<DashboardMetrics>('/ai-analytics/ai/dashboard/metrics/')
    return response.data
  },

  // Entraînement des modèles (admin only)
  async trainModel(model_type: 'dropout_risk' | 'performance_prediction', force_retrain = false): Promise<{
    message: string
    task_id: string
    force_retrain: boolean
  }> {
    const response = await apiClient.post<{
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
    student?: number
    academic_year?: number
    assigned_to?: number
    search?: string
    page?: number
    page_size?: number
  }): Promise<{
    count: number
    next: string | null
    previous: string | null
    results: Array<{
      id: number
      student: { id: number; name: string }
      risk_level: string
      risk_score: number
      is_monitored: boolean
      assigned_to: { id: number; name: string } | null
      created_at: string
      updated_at: string
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/risk-profiles/', { params })
    return response.data
  },

  async getRiskProfile(id: number): Promise<{
    id: number
    student: { id: number; name: string }
    risk_level: string
    risk_score: number
    is_monitored: boolean
    assigned_to: { id: number; name: string } | null
    prediction: RiskPrediction
    created_at: string
    updated_at: string
  }> {
    const response = await apiClient.get(`/ai-analytics/risk-profiles/${id}/`)
    return response.data
  },

  async analyzeRiskProfile(id: number): Promise<{
    success: boolean
    message: string
    updated_prediction: RiskPrediction
  }> {
    const response = await apiClient.post(`/ai-analytics/risk-profiles/${id}/analyze/`)
    return response.data
  },

  async startMonitoring(id: number, assigned_to?: number): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/ai-analytics/risk-profiles/${id}/start_monitoring/`, {
      assigned_to
    })
    return response.data
  },

  async getRiskProfileHistory(id: number): Promise<{
    history: Array<{
      id: number
      risk_score: number
      risk_level: string
      analysis_date: string
      changes: string[]
    }>
  }> {
    const response = await apiClient.get(`/ai-analytics/risk-profiles/${id}/history/`)
    return response.data
  },

  async getRiskProfileRecommendations(id: number): Promise<{
    recommendations: Array<{
      priority: string
      action: string
      details: string
      category: string
      urgency_level: number
    }>
  }> {
    const response = await apiClient.get(`/ai-analytics/risk-profiles/${id}/recommendations/`)
    return response.data
  },

  // Alertes
  async getAlerts(params?: {
    is_acknowledged?: boolean
    priority?: string
    risk_profile__student?: number
    page?: number
    page_size?: number
  }): Promise<{
    count: number
    next: string | null
    previous: string | null
    results: Array<{
      id: number
      risk_profile: { id: number; student: { id: number; name: string } }
      priority: string
      message: string
      is_acknowledged: boolean
      is_read: boolean
      created_at: string
      acknowledged_at: string | null
      actions_taken: string | null
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/alerts/', { params })
    return response.data
  },

  async acknowledgeAlert(id: number, actions_taken?: string): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/ai-analytics/alerts/${id}/acknowledge/`, {
      actions_taken
    })
    return response.data
  },

  async markAlertAsRead(id: number): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/ai-analytics/alerts/${id}/mark_read/`)
    return response.data
  },

  async getAlertsDashboard(): Promise<{
    total_alerts: number
    unread_alerts: number
    high_priority_alerts: number
    recent_alerts: Array<{
      id: number
      priority: string
      message: string
      created_at: string
      student_name: string
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/alerts/dashboard/')
    return response.data
  },

  // Plans d'intervention
  async getInterventionPlans(params?: {
    status?: string
    coordinator?: number
    risk_profile__student?: number
    page?: number
    page_size?: number
  }): Promise<{
    count: number
    next: string | null
    previous: string | null
    results: Array<{
      id: number
      risk_profile: { id: number; student: { id: number; name: string } }
      title: string
      description: string
      status: string
      coordinator: { id: number; name: string }
      start_date: string
      end_date: string
      created_at: string
      updated_at: string
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/intervention-plans/', { params })
    return response.data
  },

  async getInterventionPlan(id: number): Promise<{
    id: number
    risk_profile: { id: number; student: { id: number; name: string } }
    title: string
    description: string
    status: string
    coordinator: { id: number; name: string }
    start_date: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    resources_needed: string | null
    success_criteria: string | null
    outcomes: string | null
    effectiveness_score: number | null
    evaluation_frequency: 'weekly' | 'biweekly' | 'monthly' | null
    created_at: string
    updated_at: string
  }> {
    const response = await apiClient.get(`/ai-analytics/intervention-plans/${id}/`)
    return response.data
  },

  async createInterventionPlan(data: {
    risk_profile: number
    title: string
    description: string
    start_date: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    resources_needed?: string
    success_criteria?: string
    evaluation_frequency?: 'weekly' | 'biweekly' | 'monthly'
  }): Promise<{
    id: number
    risk_profile: { id: number; student: { id: number; name: string } }
    title: string
    description: string
    status: string
    coordinator: { id: number; name: string }
    start_date: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    created_at: string
  }> {
    const response = await apiClient.post('/ai-analytics/intervention-plans/', data)
    return response.data
  },

  async updateInterventionPlan(id: number, data: Partial<{
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
  }>): Promise<{
    id: number
    title: string
    description: string
    status: string
    end_date: string
    objectives: string[]
    planned_actions: string[]
    resources_needed: string | null
    success_criteria: string | null
    outcomes: string | null
    effectiveness_score: number | null
    updated_at: string
  }> {
    const response = await apiClient.patch(`/ai-analytics/intervention-plans/${id}/`, data)
    return response.data
  },

  async addActionToInterventionPlan(planId: number, data: {
    action_type: string
    title: string
    description: string
    responsible?: number
    scheduled_date: string
    scheduled_time?: string
    duration_minutes?: number
  }): Promise<{
    id: number
    intervention_plan: number
    action_type: string
    title: string
    description: string
    responsible: { id: number; name: string } | null
    scheduled_date: string
    scheduled_time: string | null
    duration_minutes: number | null
    is_completed: boolean
    created_at: string
  }> {
    const response = await apiClient.post(`/ai-analytics/intervention-plans/${planId}/add_action/`, data)
    return response.data
  },

  async evaluateInterventionEffectiveness(id: number, data: {
    outcomes: string
    effectiveness_score: number
  }): Promise<{
    success: boolean
    message: string
    updated_plan: {
      id: number
      outcomes: string
      effectiveness_score: number
      status: string
    }
  }> {
    const response = await apiClient.post(`/ai-analytics/intervention-plans/${id}/evaluate_effectiveness/`, data)
    return response.data
  },

  async getMyInterventions(): Promise<{
    active_interventions: Array<{
      id: number
      title: string
      student_name: string
      status: string
      start_date: string
      end_date: string
      next_action: {
        id: number
        title: string
        scheduled_date: string
      } | null
    }>
    pending_actions: Array<{
      id: number
      title: string
      intervention_plan: { id: number; title: string; student_name: string }
      scheduled_date: string
      action_type: string
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/intervention-plans/my_interventions/')
    return response.data
  },

  // Actions d'intervention
  async getInterventionActions(params?: {
    intervention_plan?: number
    responsible?: number
    completed?: boolean
    action_type?: string
    page?: number
    page_size?: number
  }): Promise<{
    count: number
    next: string | null
    previous: string | null
    results: Array<{
      id: number
      intervention_plan: { id: number; title: string; student_name: string }
      action_type: string
      title: string
      description: string
      responsible: { id: number; name: string } | null
      scheduled_date: string
      scheduled_time: string | null
      is_completed: boolean
      completed_at: string | null
      notes: string | null
      impact_assessment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative' | null
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/intervention-actions/', { params })
    return response.data
  },

  async completeInterventionAction(id: number, data: {
    notes?: string
    impact_assessment?: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative'
  }): Promise<{
    success: boolean
    message: string
    action: {
      id: number
      is_completed: boolean
      completed_at: string
      notes: string | null
      impact_assessment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative' | null
    }
  }> {
    const response = await apiClient.post(`/ai-analytics/intervention-actions/${id}/complete/`, data)
    return response.data
  },

  async getInterventionActionsCalendar(start_date?: string, end_date?: string): Promise<{
    actions: Array<{
      id: number
      title: string
      description: string
      scheduled_date: string
      scheduled_time: string | null
      duration_minutes: number | null
      action_type: string
      intervention_plan: { id: number; title: string; student_name: string }
      responsible: { id: number; name: string } | null
      is_completed: boolean
    }>
  }> {
    const params: { start_date?: string; end_date?: string } = {}
    if (start_date) params.start_date = start_date
    if (end_date) params.end_date = end_date
    
    const response = await apiClient.get('/ai-analytics/intervention-actions/calendar/', { params })
    return response.data
  },

  // Dashboard et statistiques
  async getRiskDashboard(): Promise<{
    total_students: number
    high_risk_students: number
    monitored_students: number
    active_interventions: number
    recent_alerts: number
    risk_distribution: {
      very_low: number
      low: number
      moderate: number
      high: number
      critical: number
    }
    recent_activity: Array<{
      type: string
      message: string
      timestamp: string
      student_name: string
    }>
  }> {
    const response = await apiClient.get('/ai-analytics/dashboard/')
    return response.data
  },

  async getStudentRiskHistory(student_id: number): Promise<{
    student: { id: number; name: string }
    history: Array<{
      date: string
      risk_score: number
      risk_level: string
      main_factors: string[]
      notes: string | null
    }>
    trends: {
      risk_trend: 'improving' | 'stable' | 'worsening'
      score_change: number
      period_analysis: string
    }
  }> {
    const response = await apiClient.get(`/ai-analytics/students/${student_id}/history/`)
    return response.data
  },

  async getClassRiskReport(class_id: number): Promise<{
    class_info: { id: number; name: string; level: string }
    total_students: number
    risk_distribution: {
      very_low: number
      low: number
      moderate: number
      high: number
      critical: number
    }
    average_risk_score: number
    high_risk_students: Array<{
      id: number
      name: string
      risk_score: number
      risk_level: string
      main_factors: string[]
    }>
    class_trends: {
      risk_evolution: 'improving' | 'stable' | 'worsening'
      period_comparison: string
    }
  }> {
    const response = await apiClient.get(`/ai-analytics/classes/${class_id}/report/`)
    return response.data
  },

  async getRiskStatistics(period_days = 30): Promise<{
    period_days: number
    total_analyses: number
    new_high_risk: number
    risk_level_changes: {
      improvements: number
      deteriorations: number
    }
    model_performance: {
      accuracy: number
      precision: number
      recall: number
      f1_score: number
    }
    intervention_effectiveness: {
      total_interventions: number
      successful_interventions: number
      average_effectiveness_score: number
    }
  }> {
    const response = await apiClient.get('/ai-analytics/statistics/', {
      params: { period_days }
    })
    return response.data
  },

  // Analyse déclenchement
  async triggerRiskAnalysis(data: {
    student_id?: number
    class_id?: number
    force_update?: boolean
  }): Promise<{
    success: boolean
    message: string
    task_id?: string
    analysis_count: number
  }> {
    const response = await apiClient.post('/ai-analytics/analysis/trigger/', data)
    return response.data
  },

  async triggerBulkAnalysis(type: 'daily' | 'patterns'): Promise<{
    success: boolean
    message: string
    task_id: string
    analysis_type: 'daily' | 'patterns'
    estimated_duration: string
  }> {
    const response = await apiClient.post('/ai-analytics/analysis/bulk/', { type })
    return response.data
  }
}

export default aiModulesAPI