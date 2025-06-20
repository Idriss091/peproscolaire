/**
 * Tests pour l'API AI Modules
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { aiModulesAPI } from '../ai-modules'
import { apiClient } from '../apiClient'
import type { AppreciationOptions, GenerateAppreciationRequest } from '../ai-modules'

// Les mocks sont configurés globalement dans vitest.setup.ts

describe('AI Modules API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Appreciation Generation', () => {
    it('should generate single appreciation', async () => {
      const mockResponse = {
        data: {
          success: true,
          appreciation: {
            content: 'Excellent travail en mathématiques.',
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
            id: 123,
            name: 'Marie Dupont'
          },
          subject: {
            id: 1,
            name: 'Mathématiques'
          },
          period: {
            id: 1,
            name: 'Trimestre 1'
          },
          average: 15.5
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const request: GenerateAppreciationRequest = {
        student_id: 123,
        subject_id: 1,
        period_id: 1,
        options: {
          type: 'bulletin',
          tone: 'bienveillant',
          length: 'standard'
        }
      }

      const result = await aiModulesAPI.generateAppreciation(request)

      expect(apiClient.post).toHaveBeenCalledWith('/ai-analytics/ai/appreciation/generate/', request)
      expect(result).toEqual(mockResponse.data)
    })

    it('should generate multiple appreciations', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_students: 2,
          successful_generations: 2,
          failed_generations: 0,
          results: [
            {
              student_id: 1,
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
              status: 'success'
            },
            {
              student_id: 2,
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
              status: 'success'
            }
          ]
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const request = {
        class_id: 123,
        subject_id: 1,
        period_id: 1,
        options: {
          type: 'bulletin',
          tone: 'bienveillant',
          length: 'standard'
        } as AppreciationOptions
      }

      const result = await aiModulesAPI.generateMultipleAppreciations(request)

      expect(apiClient.post).toHaveBeenCalledWith('/ai-analytics/ai/appreciation/generate-multiple/', request)
      expect(result.successful_generations).toBe(2)
      expect(result.failed_generations).toBe(0)
    })

    it('should handle appreciation generation errors', async () => {
      const errorResponse = new Error('API Error')
      Object.assign(errorResponse, {
        response: {
          status: 400,
          data: {
            error: 'Données invalides'
          }
        }
      })

      vi.mocked(apiClient.post).mockRejectedValue(errorResponse)

      const request: GenerateAppreciationRequest = {
        student_id: 999,
        subject_id: 1,
        period_id: 1
      }

      await expect(aiModulesAPI.generateAppreciation(request)).rejects.toThrow('API Error')
    })
  })

  describe('Risk Prediction', () => {
    it('should predict student risk', async () => {
      const mockResponse = {
        data: {
          student: {
            id: 123,
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
          }
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.predictStudentRisk(123)

      expect(apiClient.post).toHaveBeenCalledWith('/ai-analytics/ai/prediction/risk/', { student_id: 123 })
      expect(result.prediction.risk_level).toBe('élevé')
    })

    it('should handle risk prediction errors', async () => {
      const errorResponse = new Error('API Error')
      Object.assign(errorResponse, {
        response: {
          status: 404,
          data: {
            error: 'Étudiant non trouvé'
          }
        }
      })

      vi.mocked(apiClient.post).mockRejectedValue(errorResponse)

      await expect(aiModulesAPI.predictStudentRisk(999)).rejects.toThrow('API Error')
    })
  })

  describe('Model Status and Metrics', () => {
    it('should get model status', async () => {
      const mockResponse = {
        data: {
          models: {
            dropout_risk: {
              status: 'active',
              last_training: '2024-01-15T10:00:00Z',
              accuracy: 87.5,
              performance: {
                precision: 0.85,
                recall: 0.90,
                f1_score: 0.87
              }
            },
            appreciation_generator: {
              status: 'active',
              last_training: '2024-01-14T15:30:00Z',
              performance: {
                average_confidence: 0.88,
                generation_success_rate: 0.95
              }
            }
          }
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getModelStatus()

      expect(apiClient.get).toHaveBeenCalledWith('/ai-analytics/ai/model/status/')
      expect(result.models.dropout_risk.status).toBe('active')
    })

    it('should get dashboard metrics', async () => {
      const mockResponse = {
        data: {
          total_profiles: 150,
          high_risk_count: 12,
          medium_risk_count: 25,
          low_risk_count: 113,
          average_risk_score: 25.5,
          recent_alerts: 5,
          model_performance: {
            accuracy: 87.5,
            last_update: '2024-01-15T10:00:00Z'
          }
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getDashboardMetrics()

      expect(apiClient.get).toHaveBeenCalledWith('/ai-analytics/ai/dashboard/metrics/')
      expect(result.total_profiles).toBe(150)
    })
  })

  describe('Model Training', () => {
    it('should train model successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          task_id: 'task-123-456',
          message: 'Entraînement commencé',
          model_type: 'dropout_risk',
          estimated_duration: 300
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.trainModel('dropout_risk', false)

      expect(apiClient.post).toHaveBeenCalledWith('/ai-analytics/ai/model/train/', {
        model_type: 'dropout_risk',
        force_retrain: false
      })
      expect(result.success).toBe(true)
    })

    it('should force retrain model', async () => {
      const mockResponse = {
        data: {
          success: true,
          task_id: 'task-789-012',
          message: 'Réentraînement forcé commencé',
          model_type: 'performance_prediction',
          estimated_duration: 450
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.trainModel('performance_prediction', true)

      expect(apiClient.post).toHaveBeenCalledWith('/ai-analytics/ai/model/train/', {
        model_type: 'performance_prediction',
        force_retrain: true
      })
      expect(result.success).toBe(true)
    })

    it('should handle training errors', async () => {
      const errorResponse = new Error('API Error')
      Object.assign(errorResponse, {
        response: {
          status: 403,
          data: {
            error: 'Permission insuffisante'
          }
        }
      })

      vi.mocked(apiClient.post).mockRejectedValue(errorResponse)

      await expect(aiModulesAPI.trainModel('dropout_risk', false)).rejects.toThrow('API Error')
    })
  })
})