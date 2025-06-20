import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { 
  RiskProfile, 
  Alert,
  PaginatedResponse,
  User
} from '@/types'

interface RiskFilters {
  riskLevel?: 'low' | 'medium' | 'high' | 'critical'
  isActive?: boolean
  isAcknowledged?: boolean
  class?: number
  grade?: number
  search?: string
}

interface AlertFilters {
  severity?: 'info' | 'warning' | 'critical'
  alertType?: string
  isResolved?: boolean
  student?: number
  startDate?: string
  endDate?: string
  limit?: number
}

interface InterventionPlan {
  id: number
  risk_profile: number
  title: string
  description: string
  actions: Array<{
    id: number
    action: string
    responsible: number
    due_date: string
    status: 'pending' | 'in_progress' | 'completed'
    completed_at?: string
    notes?: string
  }>
  created_by: number
  created_at: string
  updated_at: string
  is_active: boolean
}

interface RiskStatistics {
  totalStudents: number
  atRiskCount: number
  byLevel: {
    low: number
    medium: number
    high: number
    critical: number
  }
  byCategory: Array<{
    category: string
    count: number
    percentage: number
  }>
  trends: Array<{
    date: string
    count: number
  }>
}

export const useRiskDetectionStore = defineStore('risk-detection', () => {
  // State
  const riskProfiles = ref<RiskProfile[]>([])
  const alerts = ref<Alert[]>([])
  const interventionPlans = ref<InterventionPlan[]>([])
  const currentRiskProfile = ref<RiskProfile | null>(null)
  const statistics = ref<RiskStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const criticalRisks = computed(() => 
    riskProfiles.value.filter(p => p.risk_level === 'critical' && p.is_active)
  )

  const unacknowledgedProfiles = computed(() =>
    riskProfiles.value.filter(p => !p.acknowledged_by && p.is_active)
  )

  const unresolvedAlerts = computed(() =>
    alerts.value.filter(a => !a.is_resolved)
  )

  const risksByLevel = computed(() => {
    const grouped = {
      low: [] as RiskProfile[],
      medium: [] as RiskProfile[],
      high: [] as RiskProfile[],
      critical: [] as RiskProfile[]
    }
    
    riskProfiles.value.forEach(profile => {
      if (profile.is_active) {
        grouped[profile.risk_level].push(profile)
      }
    })
    
    return grouped
  })

  // Actions
  async function fetchRiskProfiles(filters: RiskFilters = {}) {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      
      if (filters.riskLevel) params.append('risk_level', filters.riskLevel)
      if (filters.isActive !== undefined) params.append('is_active', filters.isActive.toString())
      if (filters.isAcknowledged !== undefined) {
        params.append('is_acknowledged', filters.isAcknowledged.toString())
      }
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.grade) params.append('grade', filters.grade.toString())
      if (filters.search) params.append('search', filters.search)

      const response = await apiClient.get<PaginatedResponse<RiskProfile>>(
        `/ai-analytics/risk-profiles/?${params.toString()}`
      )
      
      riskProfiles.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des profils de risque'
      console.error('Failed to fetch risk profiles:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchRiskProfile(studentId: number) {
    try {
      const response = await apiClient.get<RiskProfile>(
        `/ai-analytics/risk-profiles/student/${studentId}/`
      )
      currentRiskProfile.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Erreur lors du chargement du profil de risque'
      throw err
    }
  }

  async function fetchAlerts(filters: AlertFilters = {}) {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      
      if (filters.severity) params.append('severity', filters.severity)
      if (filters.alertType) params.append('alert_type', filters.alertType)
      if (filters.isResolved !== undefined) params.append('is_resolved', filters.isResolved.toString())
      if (filters.student) params.append('student', filters.student.toString())
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.limit) params.append('limit', filters.limit.toString())

      const response = await apiClient.get<PaginatedResponse<Alert>>(
        `/ai-analytics/alerts/?${params.toString()}`
      )
      
      alerts.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des alertes'
      console.error('Failed to fetch alerts:', err)
    } finally {
      loading.value = false
    }
  }

  async function acknowledgeRiskProfile(profileId: number, notes?: string) {
    try {
      const response = await apiClient.post(
        `/ai-analytics/risk-profiles/${profileId}/acknowledge/`,
        { notes }
      )
      
      const profile = riskProfiles.value.find(p => p.id === profileId)
      if (profile) {
        profile.acknowledged_by = response.data.acknowledged_by
        profile.acknowledged_at = response.data.acknowledged_at
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la prise en compte'
      throw err
    }
  }

  async function resolveAlert(alertId: number, resolutionNotes: string) {
    try {
      const response = await apiClient.post(
        `/ai-analytics/alerts/${alertId}/resolve/`,
        { resolution_notes: resolutionNotes }
      )
      
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.is_resolved = true
        alert.resolved_by = response.data.resolved_by
        alert.resolved_at = response.data.resolved_at
        alert.resolution_notes = resolutionNotes
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la résolution'
      throw err
    }
  }

  async function createInterventionPlan(data: {
    risk_profile: number
    title: string
    description: string
    actions: Array<{
      action: string
      responsible: number
      due_date: string
    }>
  }) {
    try {
      const response = await apiClient.post<InterventionPlan>(
        '/ai-analytics/intervention-plans/',
        data
      )
      
      interventionPlans.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la création du plan'
      throw err
    }
  }

  async function updateInterventionPlan(id: number, data: Partial<InterventionPlan>) {
    try {
      const response = await apiClient.patch<InterventionPlan>(
        `/ai-analytics/intervention-plans/${id}/`,
        data
      )
      
      const index = interventionPlans.value.findIndex(p => p.id === id)
      if (index !== -1) {
        interventionPlans.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour du plan'
      throw err
    }
  }

  async function updateActionStatus(planId: number, actionId: number, data: {
    status: 'pending' | 'in_progress' | 'completed'
    notes?: string
  }) {
    try {
      const response = await apiClient.patch(
        `/ai-analytics/intervention-plans/${planId}/actions/${actionId}/`,
        data
      )
      
      const plan = interventionPlans.value.find(p => p.id === planId)
      if (plan) {
        const action = plan.actions.find(a => a.id === actionId)
        if (action) {
          action.status = data.status
          if (data.notes) action.notes = data.notes
          if (data.status === 'completed') {
            action.completed_at = new Date().toISOString()
          }
        }
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour de l\'action'
      throw err
    }
  }

  async function fetchInterventionPlans(riskProfileId?: number) {
    try {
      const params = riskProfileId 
        ? `?risk_profile=${riskProfileId}`
        : ''
      
      const response = await apiClient.get<PaginatedResponse<InterventionPlan>>(
        `/ai-analytics/intervention-plans/${params}`
      )
      
      interventionPlans.value = response.data.results
    } catch (err) {
      error.value = 'Erreur lors du chargement des plans'
      console.error('Failed to fetch intervention plans:', err)
    }
  }

  async function fetchRiskStatistics(filters: {
    class?: number
    grade?: number
    startDate?: string
    endDate?: string
  } = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.grade) params.append('grade', filters.grade.toString())
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)

      const response = await apiClient.get<RiskStatistics>(
        `/ai-analytics/statistics/?${params.toString()}`
      )
      
      statistics.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Erreur lors du chargement des statistiques'
      throw err
    }
  }

  async function triggerAnalysis(studentId?: number) {
    try {
      const data = studentId ? { student_id: studentId } : {}
      const response = await apiClient.post(
        '/ai-analytics/trigger-analysis/',
        data
      )
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors du déclenchement de l\'analyse'
      throw err
    }
  }

  async function exportRiskReport(filters: {
    format: 'pdf' | 'excel'
    riskLevel?: string
    class?: number
    includeInterventions?: boolean
  }) {
    try {
      const params = new URLSearchParams()
      params.append('format', filters.format)
      
      if (filters.riskLevel) params.append('risk_level', filters.riskLevel)
      if (filters.class) params.append('class', filters.class.toString())
      if (filters.includeInterventions !== undefined) {
        params.append('include_interventions', filters.includeInterventions.toString())
      }

      const response = await apiClient.get(
        `/ai-analytics/export-report/?${params.toString()}`,
        { responseType: 'blob' }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `rapport-risques.${filters.format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors de l\'export du rapport'
      throw err
    }
  }

  return {
    // State
    riskProfiles,
    alerts,
    interventionPlans,
    currentRiskProfile,
    statistics,
    loading,
    error,
    // Getters
    criticalRisks,
    unacknowledgedProfiles,
    unresolvedAlerts,
    risksByLevel,
    // Actions
    fetchRiskProfiles,
    fetchRiskProfile,
    fetchAlerts,
    acknowledgeRiskProfile,
    resolveAlert,
    createInterventionPlan,
    updateInterventionPlan,
    updateActionStatus,
    fetchInterventionPlans,
    fetchRiskStatistics,
    triggerAnalysis,
    exportRiskReport
  }
})