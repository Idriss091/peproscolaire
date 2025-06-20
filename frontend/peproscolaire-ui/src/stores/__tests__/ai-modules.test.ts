/**
 * Tests pour le store AI Modules
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAIModulesStore } from '../ai-modules'
import { aiModulesAPI } from '@/api/ai-modules'
import type { AppreciationOptions, ModelStatus, DashboardMetrics } from '@/api/ai-modules'

// Mock de l'API
vi.mock('@/api/ai-modules', () => ({
  aiModulesAPI: {
    getModelStatus: vi.fn(),
    getDashboardMetrics: vi.fn(),
    generateAppreciation: vi.fn(),
    generateMultipleAppreciations: vi.fn(),
    predictStudentRisk: vi.fn(),
    trainModel: vi.fn()
  }
}))

describe('AI Modules Store', () => {
  let store: ReturnType<typeof useAIModulesStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAIModulesStore()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('State Management', () => {
    it('should initialize with correct default state', () => {
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.modelStatus.dropout_risk).toBe(null)
      expect(store.modelStatus.appreciation_generator).toBe(null)
      expect(store.dashboardMetrics).toBe(null)
      expect(store.recentAppreciations.size).toBe(0)
      expect(store.appreciationHistory).toEqual([])
    })

    it('should update loading state correctly', async () => {
      vi.mocked(aiModulesAPI.getModelStatus).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          models: {
            dropout_risk: { name: 'Dropout Risk', status: 'active' } as ModelStatus,
            appreciation_generator: { name: 'Appreciation Generator', status: 'active' } as ModelStatus
          },
          global_metrics: {
            total_profiles: 100,
            high_risk_count: 15,
            average_risk_score: 0.3,
            last_update: '2024-01-15T10:00:00Z'
          },
          system_status: {
            total_profiles: 100,
            high_risk_students: 15,
            average_risk_score: 0.3,
            last_analysis_update: '2024-01-15T10:00:00Z'
          }
        }), 100))
      )

      const promise = store.fetchModelStatus()
      expect(store.isLoading).toBe(true)

      await promise
      expect(store.isLoading).toBe(false)
    })

    it('should handle errors correctly', async () => {
      const errorMessage = 'API Error'
      vi.mocked(aiModulesAPI.getModelStatus).mockRejectedValue(new Error(errorMessage))

      try {
        await store.fetchModelStatus()
      } catch (error) {
        // Expected to throw
      }

      expect(store.error).toBe('Erreur lors de la récupération du status des modèles')
      expect(store.isLoading).toBe(false)
    })
  })

  describe('Model Status', () => {
    it('should fetch and update model status', async () => {
      const mockResponse = {
        models: {
          dropout_risk: {
            name: 'Dropout Risk Model',
            status: 'active' as const,
            performance: {
              accuracy: 0.87,
              precision: 0.82,
              recall: 0.85,
              f1_score: 0.83
            },
            last_training: '2024-01-15T08:00:00Z',
            features_count: 18,
            training_samples: 1000
          },
          appreciation_generator: {
            name: 'Appreciation Generator',
            status: 'active' as const,
            last_training: '2024-01-15T08:00:00Z'
          }
        },
        global_metrics: {
          total_profiles: 150,
          high_risk_count: 25,
          average_risk_score: 0.35,
          last_update: '2024-01-15T10:00:00Z'
        },
        system_status: {
          total_profiles: 150,
          high_risk_students: 25,
          average_risk_score: 0.35,
          last_analysis_update: '2024-01-15T10:00:00Z'
        }
      }

      vi.mocked(aiModulesAPI.getModelStatus).mockResolvedValue(mockResponse)

      await store.fetchModelStatus()

      expect(store.modelStatus.dropout_risk).toEqual(mockResponse.models.dropout_risk)
      expect(store.modelStatus.appreciation_generator).toEqual(mockResponse.models.appreciation_generator)
    })

    it('should compute isDropoutModelActive correctly', async () => {
      // Initially false
      expect(store.isDropoutModelActive).toBe(false)

      // Set active model
      store.modelStatus.dropout_risk = {
        name: 'Dropout Risk',
        status: 'active'
      }

      expect(store.isDropoutModelActive).toBe(true)

      // Set inactive model
      store.modelStatus.dropout_risk.status = 'error'
      expect(store.isDropoutModelActive).toBe(false)
    })
  })

  describe('Dashboard Metrics', () => {
    it('should fetch and update dashboard metrics', async () => {
      const mockMetrics: DashboardMetrics = {
        model_performance: {
          accuracy: 0.87,
          precision: 0.82,
          recall: 0.85,
          f1_score: 0.83,
          test_samples: 200
        },
        risk_distribution: {
          very_low: 50,
          low: 40,
          moderate: 30,
          high: 20,
          critical: 10
        },
        average_risk_score: 0.35,
        total_profiles: 150,
        high_risk_count: 30,
        recent_alerts: 5,
        profiles_analyzed_today: 25,
        interventions_active: 8,
        last_update: '2024-01-15T10:00:00Z'
      }

      vi.mocked(aiModulesAPI.getDashboardMetrics).mockResolvedValue(mockMetrics)

      await store.fetchDashboardMetrics()

      expect(store.dashboardMetrics).toEqual(mockMetrics)
      expect(store.lastMetricsUpdate).toBeTruthy()
    })

    it('should compute derived metrics correctly', () => {
      store.dashboardMetrics = {
        model_performance: {
          accuracy: 0.87,
          precision: 0.82,
          recall: 0.85,
          f1_score: 0.83,
          test_samples: 200
        },
        risk_distribution: {
          very_low: 50,
          low: 40,
          moderate: 30,
          high: 20,
          critical: 10
        },
        average_risk_score: 0.42,
        total_profiles: 150,
        high_risk_count: 30,
        recent_alerts: 5,
        profiles_analyzed_today: 25,
        interventions_active: 8,
        last_update: '2024-01-15T10:00:00Z'
      }

      expect(store.totalRiskProfiles).toBe(150)
      expect(store.highRiskStudents).toBe(30)
      expect(store.averageRiskScore).toBe(0.42)
      expect(store.recentAlertsCount).toBe(5)
    })
  })

  describe('Appreciation Generation', () => {
    it('should generate single appreciation', async () => {
      const mockResponse = {
        success: true,
        appreciation: {
          content: 'Excellent travail en mathématiques. L\'élève fait preuve d\'une grande rigueur.',
          confidence: 0.92,
          metadata: {
            type: 'bulletin',
            tone: 'bienveillant',
            length: 'standard',
            generated_at: '2024-01-15T14:30:00Z',
            model_version: '1.0'
          }
        },
        student: {
          id: 'student-123',
          name: 'Marie Dupont'
        },
        subject: {
          id: 'math',
          name: 'Mathématiques'
        },
        period: {
          id: 'T1',
          name: 'Trimestre 1'
        },
        average: 15.5
      }

      vi.mocked(aiModulesAPI.generateAppreciation).mockResolvedValue(mockResponse)

      const options: AppreciationOptions = {
        type: 'bulletin',
        tone: 'bienveillant',
        length: 'standard'
      }

      const result = await store.generateAppreciation('student-123', 'math', 'T1', options)

      expect(result).toEqual(mockResponse)
      expect(store.recentAppreciations.has('student-123-math-T1')).toBe(true)
      expect(store.appreciationHistory.length).toBe(1)
    })

    it('should generate multiple appreciations', async () => {
      const mockResponse = {
        success: true,
        total_students: 2,
        successful_generations: 2,
        failed_generations: 0,
        results: [
          {
            student_id: 'student-1',
            appreciation: {
              content: 'Très bon travail.',
              confidence: 0.88,
              metadata: {
                type: 'bulletin',
                tone: 'bienveillant',
                length: 'standard',
                generated_at: '2024-01-15T14:30:00Z',
                model_version: '1.0'
              }
            },
            status: 'success' as const
          },
          {
            student_id: 'student-2',
            appreciation: {
              content: 'Progrès encourageants.',
              confidence: 0.85,
              metadata: {
                type: 'bulletin',
                tone: 'bienveillant',
                length: 'standard',
                generated_at: '2024-01-15T14:30:00Z',
                model_version: '1.0'
              }
            },
            status: 'success' as const
          }
        ],
        options_used: {
          type: 'bulletin' as const,
          tone: 'bienveillant' as const,
          length: 'standard' as const
        }
      }

      vi.mocked(aiModulesAPI.generateMultipleAppreciations).mockResolvedValue(mockResponse)

      const result = await store.generateMultipleAppreciations(
        'class-123',
        undefined,
        'math',
        'T1'
      )

      expect(result).toEqual(mockResponse)
      expect(store.recentAppreciations.size).toBe(2)
    })

    it('should cache appreciations correctly', async () => {
      const mockResponse = {
        success: true,
        appreciation: {
          content: 'Test appreciation',
          confidence: 0.9,
          metadata: {
            type: 'bulletin',
            tone: 'bienveillant',
            length: 'standard',
            generated_at: '2024-01-15T14:30:00Z',
            model_version: '1.0'
          }
        },
        student: { id: 'student-123', name: 'Test Student' },
        subject: { id: 'math', name: 'Mathématiques' },
        period: { id: 'T1', name: 'Trimestre 1' },
        average: 14.0
      }

      vi.mocked(aiModulesAPI.generateAppreciation).mockResolvedValue(mockResponse)

      await store.generateAppreciation('student-123', 'math', 'T1')

      const cached = store.getCachedAppreciation('student-123', 'math', 'T1')
      expect(cached).toEqual(mockResponse.appreciation)
    })
  })

  describe('Risk Prediction', () => {
    it('should predict student risk', async () => {
      const mockResponse = {
        student: {
          id: 'student-123',
          name: 'Paul Martin'
        },
        prediction: {
          dropout_probability: 0.75,
          risk_level: 'élevé',
          risk_score: 0.75,
          main_risk_factors: [
            {
              factor: 'Absentéisme',
              value: 0.4,
              importance: 0.3,
              impact: 'négatif'
            }
          ],
          recommendations: [
            {
              priority: 'high',
              action: 'Intervention immédiate',
              details: 'Planifier un entretien avec la famille'
            }
          ]
        },
        data_collected: {
          analysis_date: '2024-01-15T10:00:00Z',
          features_count: 18
        }
      }

      vi.mocked(aiModulesAPI.predictStudentRisk).mockResolvedValue(mockResponse)

      const result = await store.predictStudentRisk('student-123')

      expect(result).toEqual(mockResponse)
      expect(store.riskPredictions.has('student-123')).toBe(true)
      expect(store.getCachedRiskPrediction('student-123')).toEqual(mockResponse.prediction)
    })
  })

  describe('Model Training', () => {
    it('should train model successfully', async () => {
      const mockResponse = {
        message: 'Entraînement lancé avec succès',
        task_id: 'train-task-123',
        force_retrain: false
      }

      vi.mocked(aiModulesAPI.trainModel).mockResolvedValue(mockResponse)

      const result = await store.trainModel('dropout_risk', false)

      expect(result).toEqual(mockResponse)
      expect(store.trainingStatus.isTraining).toBe(true)
      expect(store.trainingStatus.model_type).toBe('dropout_risk')
      expect(store.trainingStatus.task_id).toBe('train-task-123')
    })

    it('should clear training status', () => {
      // Set training status first
      store.trainingStatus.isTraining = true
      store.trainingStatus.model_type = 'dropout_risk'
      store.trainingStatus.task_id = 'task-123'

      store.clearTrainingStatus()

      expect(store.trainingStatus.isTraining).toBe(false)
      expect(store.trainingStatus.model_type).toBe(null)
      expect(store.trainingStatus.task_id).toBe(null)
    })
  })

  describe('Cache Management', () => {
    it('should clear all cache', () => {
      // Add some cached data
      store.recentAppreciations.set('key1', {
        content: 'test',
        confidence: 0.9,
        metadata: {
          type: 'bulletin',
          tone: 'bienveillant',
          length: 'standard',
          generated_at: '2024-01-15T14:30:00Z',
          model_version: '1.0'
        }
      })
      store.riskPredictions.set('student1', {
        dropout_probability: 0.5,
        risk_level: 'modéré',
        risk_score: 0.5,
        main_risk_factors: [],
        recommendations: []
      })
      store.appreciationHistory.push({
        id: 'hist1',
        student_name: 'Test',
        subject_name: 'Math',
        appreciation: {
          content: 'test',
          confidence: 0.9,
          metadata: {
            type: 'bulletin',
            tone: 'bienveillant',
            length: 'standard',
            generated_at: '2024-01-15T14:30:00Z',
            model_version: '1.0'
          }
        },
        generated_at: '2024-01-15T14:30:00Z'
      })

      store.clearCache()

      expect(store.recentAppreciations.size).toBe(0)
      expect(store.riskPredictions.size).toBe(0)
      expect(store.appreciationHistory.length).toBe(0)
    })

    it('should clear error state', () => {
      store.error = 'Test error'
      store.clearError()
      expect(store.error).toBe(null)
    })
  })

  describe('Auto-refresh', () => {
    it('should start and stop metrics auto-refresh', () => {
      // Mock window.setInterval and clearInterval
      const mockSetInterval = vi.fn()
      const mockClearInterval = vi.fn()
      global.setInterval = mockSetInterval
      global.clearInterval = mockClearInterval

      // Start auto-refresh
      store.startMetricsAutoRefresh()
      expect(mockSetInterval).toHaveBeenCalledWith(
        expect.any(Function),
        5 * 60 * 1000 // 5 minutes
      )

      // Stop auto-refresh
      store.stopMetricsAutoRefresh()
      expect(mockClearInterval).toHaveBeenCalled()
    })

    it('should not start multiple intervals', () => {
      const mockSetInterval = vi.fn()
      global.setInterval = mockSetInterval

      // Start twice
      store.startMetricsAutoRefresh()
      store.startMetricsAutoRefresh()

      // Should only be called once
      expect(mockSetInterval).toHaveBeenCalledTimes(1)
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const errorResponse = {
        response: {
          data: {
            error: 'Modèle non disponible'
          }
        }
      }

      vi.mocked(aiModulesAPI.getModelStatus).mockRejectedValue(errorResponse)

      try {
        await store.fetchModelStatus()
      } catch (error) {
        // Expected
      }

      expect(store.error).toBe('Modèle non disponible')
    })

    it('should handle network errors', async () => {
      vi.mocked(aiModulesAPI.getDashboardMetrics).mockRejectedValue(new Error('Network error'))

      try {
        await store.fetchDashboardMetrics()
      } catch (error) {
        // Expected
      }

      expect(store.error).toBe('Erreur lors de la récupération des métriques')
    })
  })

  describe('Data Validation', () => {
    it('should handle malformed API responses', async () => {
      const malformedResponse = {
        models: {
          // Missing appreciation_generator
          dropout_risk: { name: 'Test', status: 'active' }
        }
      }

      vi.mocked(aiModulesAPI.getModelStatus).mockResolvedValue(malformedResponse as any)

      await store.fetchModelStatus()

      expect(store.modelStatus.dropout_risk).toBeDefined()
      expect(store.modelStatus.appreciation_generator).toBe(null)
    })

    it('should limit appreciation history', async () => {
      // Add 60 items to history (more than the 50 limit)
      for (let i = 0; i < 60; i++) {
        store.appreciationHistory.push({
          id: `hist-${i}`,
          student_name: `Student ${i}`,
          subject_name: 'Math',
          appreciation: {
            content: `Test ${i}`,
            confidence: 0.9,
            metadata: {
              type: 'bulletin',
              tone: 'bienveillant',
              length: 'standard',
              generated_at: '2024-01-15T14:30:00Z',
              model_version: '1.0'
            }
          },
          generated_at: '2024-01-15T14:30:00Z'
        })
      }

      const mockResponse = {
        success: true,
        appreciation: {
          content: 'New appreciation',
          confidence: 0.9,
          metadata: {
            type: 'bulletin',
            tone: 'bienveillant',
            length: 'standard',
            generated_at: '2024-01-15T14:30:00Z',
            model_version: '1.0'
          }
        },
        student: { id: 'new-student', name: 'New Student' },
        subject: { id: 'math', name: 'Math' },
        period: { id: 'T1', name: 'T1' },
        average: 15
      }

      vi.mocked(aiModulesAPI.generateAppreciation).mockResolvedValue(mockResponse)

      await store.generateAppreciation('new-student', 'math', 'T1')

      // Should be limited to 50 items
      expect(store.appreciationHistory.length).toBe(50)
      expect(store.appreciationHistory[0].student_name).toBe('New Student') // Most recent first
    })
  })
})