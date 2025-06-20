/**
 * Tests pour l'API AI Modules
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { aiModulesAPI } from '../ai-modules'
import { api } from '../client'
import type { AppreciationOptions, GenerateAppreciationRequest } from '../ai-modules'

// Mock du client API
vi.mock('../client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('AI Modules API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
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
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const request: GenerateAppreciationRequest = {
        student_id: 'student-123',
        subject_id: 'math',
        period_id: 'T1',
        options: {
          type: 'bulletin',
          tone: 'bienveillant',
          length: 'standard'
        }
      }

      const result = await aiModulesAPI.generateAppreciation(request)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/ai/appreciation/generate/', request)
      expect(result).toEqual(mockResponse.data)
    })

    it('should generate multiple appreciations', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_students: 3,
          successful_generations: 2,
          failed_generations: 1,
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
              status: 'success'
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
              status: 'success'
            },
            {
              student_id: 'student-3',
              appreciation: null,
              status: 'error',
              error: 'Données insuffisantes'
            }
          ],
          options_used: {
            type: 'bulletin',
            tone: 'bienveillant',
            length: 'standard'
          }
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const request = {
        class_id: 'class-123',
        subject_id: 'math',
        period_id: 'T1',
        options: {
          type: 'bulletin',
          tone: 'bienveillant',
          length: 'standard'
        } as AppreciationOptions
      }

      const result = await aiModulesAPI.generateMultipleAppreciations(request)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/ai/appreciation/generate-multiple/', request)
      expect(result.successful_generations).toBe(2)
      expect(result.failed_generations).toBe(1)
      expect(result.results).toHaveLength(3)
    })

    it('should handle appreciation generation errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: 'Données invalides'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValue(errorResponse)

      const request: GenerateAppreciationRequest = {
        student_id: 'invalid-id',
        subject_id: '',
        period_id: ''
      }

      await expect(aiModulesAPI.generateAppreciation(request)).rejects.toEqual(errorResponse)
    })
  })

  describe('Risk Prediction', () => {
    it('should predict student risk', async () => {
      const mockResponse = {
        data: {
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
              },
              {
                factor: 'Notes en baisse',
                value: 0.6,
                importance: 0.25,
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
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.predictStudentRisk('student-123')

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/ai/prediction/risk/', { student_id: 'student-123' })
      expect(result.prediction.risk_level).toBe('élevé')
      expect(result.prediction.main_risk_factors).toHaveLength(2)
    })

    it('should handle risk prediction errors', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: {
            error: 'Étudiant non trouvé'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValue(errorResponse)

      await expect(aiModulesAPI.predictStudentRisk('nonexistent-id')).rejects.toEqual(errorResponse)
    })
  })

  describe('Model Status and Metrics', () => {
    it('should get model status', async () => {
      const mockResponse = {
        data: {
          models: {
            dropout_risk: {
              name: 'Dropout Risk Model',
              status: 'active',
              performance: {
                accuracy: 0.87,
                precision: 0.82,
                recall: 0.85,
                f1_score: 0.83,
                auc: 0.91
              },
              last_training: '2024-01-15T08:00:00Z',
              features_count: 18,
              training_samples: 1000
            },
            appreciation_generator: {
              name: 'Appreciation Generator',
              status: 'active',
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
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getModelStatus()

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/ai/model/status/')
      expect(result.models.dropout_risk.status).toBe('active')
      expect(result.models.dropout_risk.performance?.accuracy).toBe(0.87)
    })

    it('should get dashboard metrics', async () => {
      const mockResponse = {
        data: {
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
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getDashboardMetrics()

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/ai/dashboard/metrics/')
      expect(result.total_profiles).toBe(150)
      expect(result.risk_distribution.high).toBe(20)
    })
  })

  describe('Model Training', () => {
    it('should train model successfully', async () => {
      const mockResponse = {
        data: {
          message: 'Entraînement lancé avec succès',
          task_id: 'train-task-123',
          force_retrain: false
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.trainModel('dropout_risk', false)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/ai/model/train/', {
        model_type: 'dropout_risk',
        force_retrain: false
      })
      expect(result.task_id).toBe('train-task-123')
    })

    it('should force retrain model', async () => {
      const mockResponse = {
        data: {
          message: 'Entraînement forcé lancé',
          task_id: 'force-train-456',
          force_retrain: true
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await aiModulesAPI.trainModel('performance_prediction', true)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/ai/model/train/', {
        model_type: 'performance_prediction',
        force_retrain: true
      })
    })

    it('should handle training errors', async () => {
      const errorResponse = {
        response: {
          status: 403,
          data: {
            error: 'Permission insuffisante'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValue(errorResponse)

      await expect(aiModulesAPI.trainModel('dropout_risk')).rejects.toEqual(errorResponse)
    })
  })

  describe('Risk Profiles Management', () => {
    it('should get risk profiles with filters', async () => {
      const mockResponse = {
        data: {
          count: 50,
          next: null,
          previous: null,
          results: [
            {
              id: 'profile-1',
              student: {
                id: 'student-1',
                name: 'Jean Dupont'
              },
              risk_level: 'élevé',
              risk_score: 0.85,
              last_analysis: '2024-01-15T10:00:00Z'
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const filters = {
        risk_level: ['élevé'],
        is_monitored: true,
        min_risk_score: 0.7,
        search: 'Jean'
      }

      const result = await aiModulesAPI.getRiskProfiles(filters)

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/risk-profiles/', { params: filters })
      expect(result.results).toHaveLength(1)
    })

    it('should get specific risk profile', async () => {
      const mockResponse = {
        data: {
          id: 'profile-123',
          student: {
            id: 'student-123',
            name: 'Marie Martin'
          },
          risk_level: 'modéré',
          risk_score: 0.6,
          main_risk_factors: [
            {
              factor: 'Assiduité',
              value: 0.8,
              importance: 0.3
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getRiskProfile('profile-123')

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/risk-profiles/profile-123/')
      expect(result.risk_level).toBe('modéré')
    })

    it('should analyze risk profile', async () => {
      const mockResponse = {
        data: {
          message: 'Analyse lancée',
          task_id: 'analyze-task-789'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.analyzeRiskProfile('profile-123')

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/risk-profiles/profile-123/analyze/')
      expect(result.task_id).toBe('analyze-task-789')
    })

    it('should start monitoring', async () => {
      const mockResponse = {
        data: {
          message: 'Surveillance activée',
          assigned_to: 'teacher-456'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.startMonitoring('profile-123', 'teacher-456')

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/risk-profiles/profile-123/start_monitoring/', {
        assigned_to: 'teacher-456'
      })
      expect(result.assigned_to).toBe('teacher-456')
    })
  })

  describe('Alerts Management', () => {
    it('should get alerts with filters', async () => {
      const mockResponse = {
        data: {
          count: 10,
          results: [
            {
              id: 'alert-1',
              message: 'Risque de décrochage détecté',
              priority: 'high',
              is_acknowledged: false,
              created_at: '2024-01-15T10:00:00Z'
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const filters = {
        is_acknowledged: false,
        priority: 'high'
      }

      const result = await aiModulesAPI.getAlerts(filters)

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/alerts/', { params: filters })
      expect(result.results[0].priority).toBe('high')
    })

    it('should acknowledge alert', async () => {
      const mockResponse = {
        data: {
          message: 'Alerte acquittée',
          acknowledged_at: '2024-01-15T11:00:00Z'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.acknowledgeAlert('alert-123', 'Intervention planifiée')

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/alerts/alert-123/acknowledge/', {
        actions_taken: 'Intervention planifiée'
      })
      expect(result.acknowledged_at).toBeTruthy()
    })

    it('should get alerts dashboard', async () => {
      const mockResponse = {
        data: {
          total_alerts: 25,
          unacknowledged_alerts: 8,
          high_priority_alerts: 3,
          alerts_today: 5
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.getAlertsDashboard()

      expect(api.get).toHaveBeenCalledWith('/ai-analytics/alerts/dashboard/')
      expect(result.total_alerts).toBe(25)
    })
  })

  describe('Intervention Plans', () => {
    it('should create intervention plan', async () => {
      const mockResponse = {
        data: {
          id: 'plan-123',
          title: 'Plan de remédiation',
          status: 'en_cours',
          created_at: '2024-01-15T10:00:00Z'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const planData = {
        risk_profile: 'profile-123',
        title: 'Plan de remédiation',
        description: 'Accompagnement personnalisé',
        start_date: '2024-01-15',
        end_date: '2024-02-15',
        objectives: ['Améliorer l\'assiduité'],
        planned_actions: ['Entretien hebdomadaire']
      }

      const result = await aiModulesAPI.createInterventionPlan(planData)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/intervention-plans/', planData)
      expect(result.title).toBe('Plan de remédiation')
    })

    it('should update intervention plan', async () => {
      const mockResponse = {
        data: {
          id: 'plan-123',
          status: 'terminé',
          effectiveness_score: 8
        }
      }

      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      const updateData = {
        status: 'terminé',
        effectiveness_score: 8
      }

      const result = await aiModulesAPI.updateInterventionPlan('plan-123', updateData)

      expect(api.patch).toHaveBeenCalledWith('/ai-analytics/intervention-plans/plan-123/', updateData)
      expect(result.effectiveness_score).toBe(8)
    })

    it('should evaluate intervention effectiveness', async () => {
      const mockResponse = {
        data: {
          message: 'Évaluation enregistrée',
          effectiveness_score: 7
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const evaluationData = {
        outcomes: 'Amélioration notable de l\'assiduité',
        effectiveness_score: 7
      }

      const result = await aiModulesAPI.evaluateInterventionEffectiveness('plan-123', evaluationData)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/intervention-plans/plan-123/evaluate_effectiveness/', evaluationData)
      expect(result.effectiveness_score).toBe(7)
    })
  })

  describe('Analysis Triggers', () => {
    it('should trigger risk analysis for student', async () => {
      const mockResponse = {
        data: {
          message: 'Analyse déclenchée',
          task_id: 'trigger-task-123'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const data = {
        student_id: 'student-123',
        force_update: true
      }

      const result = await aiModulesAPI.triggerRiskAnalysis(data)

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/analysis/trigger/', data)
      expect(result.task_id).toBe('trigger-task-123')
    })

    it('should trigger bulk analysis', async () => {
      const mockResponse = {
        data: {
          message: 'Analyse en masse déclenchée',
          type: 'daily',
          estimated_duration: 300
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await aiModulesAPI.triggerBulkAnalysis('daily')

      expect(api.post).toHaveBeenCalledWith('/ai-analytics/analysis/bulk/', { type: 'daily' })
      expect(result.type).toBe('daily')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      vi.mocked(api.get).mockRejectedValue(networkError)

      await expect(aiModulesAPI.getModelStatus()).rejects.toThrow('Network Error')
    })

    it('should handle HTTP errors', async () => {
      const httpError = {
        response: {
          status: 500,
          data: {
            error: 'Erreur interne du serveur'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValue(httpError)

      await expect(aiModulesAPI.generateAppreciation({
        student_id: 'test',
        subject_id: 'test',
        period_id: 'test'
      })).rejects.toEqual(httpError)
    })

    it('should handle authentication errors', async () => {
      const authError = {
        response: {
          status: 401,
          data: {
            detail: 'Token invalide'
          }
        }
      }

      vi.mocked(api.get).mockRejectedValue(authError)

      await expect(aiModulesAPI.getDashboardMetrics()).rejects.toEqual(authError)
    })
  })
})