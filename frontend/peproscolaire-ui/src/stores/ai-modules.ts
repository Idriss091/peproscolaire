import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { aiModulesAPI, type AppreciationOptions, type AppreciationResult, type RiskPrediction, type ModelStatus, type DashboardMetrics } from '@/api/ai-modules'

export const useAIModulesStore = defineStore('ai-modules', () => {
  // State
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Model status
  const modelStatus = ref<{
    dropout_risk: ModelStatus | null
    appreciation_generator: ModelStatus | null
  }>({
    dropout_risk: null,
    appreciation_generator: null
  })
  
  // Dashboard metrics
  const dashboardMetrics = ref<DashboardMetrics | null>(null)
  const lastMetricsUpdate = ref<string | null>(null)
  
  // Appreciations cache
  const recentAppreciations = ref<Map<string, AppreciationResult>>(new Map())
  const appreciationHistory = ref<Array<{
    id: string
    student_name: string
    subject_name: string
    appreciation: AppreciationResult
    generated_at: string
  }>>([])
  
  // Risk predictions cache
  const riskPredictions = ref<Map<string, RiskPrediction>>(new Map())
  
  // Training status
  const trainingStatus = ref<{
    isTraining: boolean
    model_type: string | null
    task_id: string | null
    started_at: string | null
  }>({
    isTraining: false,
    model_type: null,
    task_id: null,
    started_at: null
  })

  // Getters
  const isDropoutModelActive = computed(() => 
    modelStatus.value.dropout_risk?.status === 'active'
  )
  
  const isAppreciationGeneratorActive = computed(() => 
    modelStatus.value.appreciation_generator?.status === 'active'
  )
  
  const dropoutModelPerformance = computed(() => 
    modelStatus.value.dropout_risk?.performance
  )
  
  const totalRiskProfiles = computed(() => 
    dashboardMetrics.value?.total_profiles || 0
  )
  
  const highRiskStudents = computed(() => 
    dashboardMetrics.value?.high_risk_count || 0
  )
  
  const averageRiskScore = computed(() => 
    dashboardMetrics.value?.average_risk_score || 0
  )
  
  const recentAlertsCount = computed(() => 
    dashboardMetrics.value?.recent_alerts || 0
  )

  // Actions
  async function fetchModelStatus() {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.getModelStatus()
      modelStatus.value = response.models
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de la récupération du status des modèles'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDashboardMetrics() {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.getDashboardMetrics()
      dashboardMetrics.value = response
      lastMetricsUpdate.value = new Date().toISOString()
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de la récupération des métriques'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function generateAppreciation(
    student_id: string,
    subject_id: string,
    period_id: string,
    options?: AppreciationOptions
  ) {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.generateAppreciation({
        student_id,
        subject_id,
        period_id,
        options
      })
      
      // Cache the result
      const cacheKey = `${student_id}-${subject_id}-${period_id}`
      recentAppreciations.value.set(cacheKey, response.appreciation)
      
      // Add to history
      appreciationHistory.value.unshift({
        id: cacheKey,
        student_name: response.student.name,
        subject_name: response.subject.name,
        appreciation: response.appreciation,
        generated_at: response.appreciation.metadata.generated_at
      })
      
      // Limit history to 50 items
      if (appreciationHistory.value.length > 50) {
        appreciationHistory.value = appreciationHistory.value.slice(0, 50)
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de la génération de l\'appréciation'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function generateMultipleAppreciations(
    class_id: string | undefined,
    student_ids: string[] | undefined,
    subject_id: string,
    period_id: string,
    options?: AppreciationOptions
  ) {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.generateMultipleAppreciations({
        class_id,
        student_ids,
        subject_id,
        period_id,
        options
      })
      
      // Cache successful results
      response.results.forEach(result => {
        if (result.status === 'success' && result.appreciation) {
          const cacheKey = `${result.student_id}-${subject_id}-${period_id}`
          recentAppreciations.value.set(cacheKey, result.appreciation)
        }
      })
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de la génération multiple'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function predictStudentRisk(student_id: string) {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.predictStudentRisk(student_id)
      
      // Cache the prediction
      riskPredictions.value.set(student_id, response.prediction)
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de la prédiction de risque'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function trainModel(model_type: 'dropout_risk' | 'performance_prediction', force_retrain = false) {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await aiModulesAPI.trainModel(model_type, force_retrain)
      
      // Update training status
      trainingStatus.value = {
        isTraining: true,
        model_type,
        task_id: response.task_id,
        started_at: new Date().toISOString()
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors du lancement de l\'entraînement'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearTrainingStatus() {
    trainingStatus.value = {
      isTraining: false,
      model_type: null,
      task_id: null,
      started_at: null
    }
  }

  function getCachedAppreciation(student_id: string, subject_id: string, period_id: string) {
    const cacheKey = `${student_id}-${subject_id}-${period_id}`
    return recentAppreciations.value.get(cacheKey)
  }

  function getCachedRiskPrediction(student_id: string) {
    return riskPredictions.value.get(student_id)
  }

  function clearCache() {
    recentAppreciations.value.clear()
    riskPredictions.value.clear()
    appreciationHistory.value = []
  }

  function clearError() {
    error.value = null
  }

  // Auto-refresh metrics every 5 minutes
  let metricsInterval: number | null = null
  
  function startMetricsAutoRefresh() {
    if (metricsInterval) return
    
    metricsInterval = window.setInterval(() => {
      fetchDashboardMetrics().catch(() => {
        // Silent fail for auto-refresh
      })
    }, 5 * 60 * 1000) // 5 minutes
  }
  
  function stopMetricsAutoRefresh() {
    if (metricsInterval) {
      clearInterval(metricsInterval)
      metricsInterval = null
    }
  }

  return {
    // State
    isLoading,
    error,
    modelStatus,
    dashboardMetrics,
    lastMetricsUpdate,
    recentAppreciations,
    appreciationHistory,
    riskPredictions,
    trainingStatus,
    
    // Getters
    isDropoutModelActive,
    isAppreciationGeneratorActive,
    dropoutModelPerformance,
    totalRiskProfiles,
    highRiskStudents,
    averageRiskScore,
    recentAlertsCount,
    
    // Actions
    fetchModelStatus,
    fetchDashboardMetrics,
    generateAppreciation,
    generateMultipleAppreciations,
    predictStudentRisk,
    trainModel,
    clearTrainingStatus,
    getCachedAppreciation,
    getCachedRiskPrediction,
    clearCache,
    clearError,
    startMetricsAutoRefresh,
    stopMetricsAutoRefresh
  }
})