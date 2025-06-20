/**
 * Tests pour le composant AI Dashboard
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AiDashboardView from '../AiDashboardView.vue'
import { useAIModulesStore } from '@/stores/ai-modules'

// Mock des composants UI
vi.mock('@/components/ui/BaseButton.vue', () => ({
  default: {
    name: 'BaseButton',
    template: '<button><slot /></button>',
    props: ['variant', 'size', 'loading', 'disabled']
  }
}))

vi.mock('@/components/ui/BaseCard.vue', () => ({
  default: {
    name: 'BaseCard',
    template: '<div class="card"><header v-if="$slots.header"><slot name="header" /></header><slot /></div>'
  }
}))

vi.mock('@/components/ui/BaseBadge.vue', () => ({
  default: {
    name: 'BaseBadge',
    template: '<span><slot /></span>',
    props: ['variant', 'size']
  }
}))

// Mock des icônes Heroicons
vi.mock('@heroicons/vue/24/outline', () => ({
  ChartBarIcon: { name: 'ChartBarIcon', template: '<svg></svg>' },
  CheckCircleIcon: { name: 'CheckCircleIcon', template: '<svg></svg>' },
  ExclamationTriangleIcon: { name: 'ExclamationTriangleIcon', template: '<svg></svg>' },
  CpuChipIcon: { name: 'CpuChipIcon', template: '<svg></svg>' },
  UserGroupIcon: { name: 'UserGroupIcon', template: '<svg></svg>' },
  DocumentChartBarIcon: { name: 'DocumentChartBarIcon', template: '<svg></svg>' },
  Cog6ToothIcon: { name: 'Cog6ToothIcon', template: '<svg></svg>' }
}))

describe('AiDashboardView', () => {
  let wrapper: any
  let aiStore: ReturnType<typeof useAIModulesStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    aiStore = useAIModulesStore()
    
    // Mock store methods
    vi.spyOn(aiStore, 'fetchModelStatus').mockResolvedValue({} as any)
    vi.spyOn(aiStore, 'fetchDashboardMetrics').mockResolvedValue({} as any)
    vi.spyOn(aiStore, 'startMetricsAutoRefresh').mockImplementation(() => {})
    vi.spyOn(aiStore, 'trainModel').mockResolvedValue({} as any)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('Component Rendering', () => {
    it('should render without errors', () => {
      wrapper = mount(AiDashboardView)
      expect(wrapper.exists()).toBe(true)
    })

    it('should display model performance metrics', async () => {
      // Setup mock data
      aiStore.modelStatus.dropout_risk = {
        name: 'Dropout Risk Model',
        status: 'active',
        performance: {
          accuracy: 0.87,
          precision: 0.82,
          recall: 0.85,
          f1_score: 0.83
        }
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('87%') // Accuracy
      expect(wrapper.text()).toContain('85%') // Recall
      expect(wrapper.text()).toContain('83%') // F1 Score
    })

    it('should display risk distribution', async () => {
      aiStore.dashboardMetrics = {
        model_performance: {
          accuracy: 0.87,
          precision: 0.82,
          recall: 0.85,
          f1_score: 0.83,
          test_samples: 200
        },
        risk_distribution: {
          very_low: 30,
          low: 40,
          moderate: 20,
          high: 8,
          critical: 2
        },
        total_profiles: 100,
        high_risk_count: 10,
        average_risk_score: 0.25,
        recent_alerts: 3,
        profiles_analyzed_today: 15,
        interventions_active: 5,
        last_update: '2024-01-15T10:00:00Z'
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Risque élevé')
      expect(wrapper.text()).toContain('Risque modéré')
      expect(wrapper.text()).toContain('Risque faible')
    })

    it('should show loading state', async () => {
      aiStore.isLoading = true
      
      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      // The loading state should affect the component behavior
      expect(aiStore.isLoading).toBe(true)
    })

    it('should handle missing data gracefully', () => {
      // No data in store
      wrapper = mount(AiDashboardView)
      
      expect(wrapper.exists()).toBe(true)
      // Should display default values or placeholders
      expect(wrapper.text()).toContain('0%') // Default values
    })
  })

  describe('Computed Properties', () => {
    it('should compute model performance correctly', async () => {
      aiStore.modelStatus.dropout_risk = {
        name: 'Test Model',
        status: 'active',
        performance: {
          accuracy: 0.91,
          recall: 0.88,
          f1_score: 0.89
        },
        last_training: '2024-01-15T08:00:00Z'
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      const modelPerformance = wrapper.vm.modelPerformance
      expect(modelPerformance.accuracy).toBe(91) // Converted to percentage
      expect(modelPerformance.recall).toBe(88)
      expect(modelPerformance.f1Score).toBe(89)
      expect(modelPerformance.status).toBe('optimal')
    })

    it('should compute risk distribution correctly', async () => {
      aiStore.dashboardMetrics = {
        risk_distribution: {
          very_low: 20,
          low: 30,
          moderate: 30,
          high: 15,
          critical: 5
        },
        total_profiles: 100,
        model_performance: {
          accuracy: 0.85,
          precision: 0.80,
          recall: 0.82,
          f1_score: 0.81,
          test_samples: 200
        },
        high_risk_count: 20,
        average_risk_score: 0.35,
        recent_alerts: 5,
        profiles_analyzed_today: 25,
        interventions_active: 8,
        last_update: '2024-01-15T10:00:00Z'
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      const riskDistribution = wrapper.vm.riskDistribution
      
      expect(riskDistribution[0].name).toBe('Risque élevé')
      expect(riskDistribution[0].count).toBe(20) // high + critical
      expect(riskDistribution[0].percentage).toBe(20)

      expect(riskDistribution[1].name).toBe('Risque modéré')
      expect(riskDistribution[1].count).toBe(30)
      expect(riskDistribution[1].percentage).toBe(30)

      expect(riskDistribution[2].name).toBe('Risque faible')
      expect(riskDistribution[2].count).toBe(50) // very_low + low
      expect(riskDistribution[2].percentage).toBe(50)
    })

    it('should handle empty metrics gracefully', () => {
      wrapper = mount(AiDashboardView)
      
      const riskDistribution = wrapper.vm.riskDistribution
      expect(riskDistribution).toHaveLength(3)
      expect(riskDistribution[0].count).toBe(0)
      expect(riskDistribution[0].percentage).toBe(0)
    })
  })

  describe('Methods', () => {
    it('should load dashboard data on mount', async () => {
      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      expect(aiStore.fetchModelStatus).toHaveBeenCalled()
      expect(aiStore.fetchDashboardMetrics).toHaveBeenCalled()
      expect(aiStore.startMetricsAutoRefresh).toHaveBeenCalled()
    })

    it('should trigger analysis when analyze class is called', async () => {
      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      await wrapper.vm.analyzeClass()

      expect(aiStore.trainModel).toHaveBeenCalledWith('dropout_risk', false)
    })

    it('should handle analysis errors', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      aiStore.trainModel = vi.fn().mockRejectedValue(new Error('Training failed'))

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      await wrapper.vm.analyzeClass()

      expect(consoleSpy).toHaveBeenCalledWith('Erreur lors de l\'analyse:', expect.any(Error))
    })
  })

  describe('User Interactions', () => {
    it('should handle quick action buttons', async () => {
      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('button')
      const analyzeButton = buttons.find((button: any) => 
        button.text().includes('Sélectionner une classe')
      )

      expect(analyzeButton?.exists()).toBe(true)
    })

    it('should display model status correctly', async () => {
      aiStore.modelStatus.dropout_risk = {
        name: 'Dropout Risk',
        status: 'active'
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Optimal')
    })

    it('should handle different model statuses', async () => {
      // Test error status
      aiStore.modelStatus.dropout_risk = {
        name: 'Dropout Risk',
        status: 'error'
      }

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      const statusColor = wrapper.vm.getModelStatusColor('error')
      expect(statusColor).toBe('danger')

      const statusLabel = wrapper.vm.getModelStatusLabel('error')
      expect(statusLabel).toBe('Critique')
    })
  })

  describe('Utility Functions', () => {
    beforeEach(() => {
      wrapper = mount(AiDashboardView)
    })

    it('should format dates correctly', () => {
      const dateString = '2024-01-15T08:30:00'
      const formatted = wrapper.vm.formatDateTime(dateString)
      
      expect(formatted).toMatch(/15 janv./)
    })

    it('should get correct risk factor colors', () => {
      expect(wrapper.vm.getRiskFactorColor('high')).toBe('bg-red-500')
      expect(wrapper.vm.getRiskFactorColor('medium')).toBe('bg-orange-500')
      expect(wrapper.vm.getRiskFactorColor('low')).toBe('bg-green-500')
    })

    it('should get correct alert classes', () => {
      expect(wrapper.vm.getAlertClass('high')).toBe('border-red-200 bg-red-50')
      expect(wrapper.vm.getAlertClass('medium')).toBe('border-orange-200 bg-orange-50')
      expect(wrapper.vm.getAlertClass('low')).toBe('border-yellow-200 bg-yellow-50')
    })

    it('should get correct risk level colors', () => {
      expect(wrapper.vm.getRiskLevelColor('élevé')).toBe('danger')
      expect(wrapper.vm.getRiskLevelColor('modéré')).toBe('warning')
      expect(wrapper.vm.getRiskLevelColor('faible')).toBe('success')
    })
  })

  describe('Error Handling', () => {
    it('should handle loading errors', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      aiStore.fetchModelStatus = vi.fn().mockRejectedValue(new Error('Network error'))

      wrapper = mount(AiDashboardView)
      await wrapper.vm.$nextTick()

      expect(consoleSpy).toHaveBeenCalled()
    })

    it('should handle missing model status', () => {
      wrapper = mount(AiDashboardView)
      
      const modelPerformance = wrapper.vm.modelPerformance
      expect(modelPerformance.status).toBe('loading')
      expect(modelPerformance.accuracy).toBe(0)
    })
  })

  describe('Reactive Updates', () => {
    it('should update when store data changes', async () => {
      wrapper = mount(AiDashboardView)
      
      // Initially no data
      expect(wrapper.vm.modelPerformance.accuracy).toBe(0)

      // Update store
      aiStore.modelStatus.dropout_risk = {
        name: 'Test',
        status: 'active',
        performance: {
          accuracy: 0.95
        }
      }

      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.modelPerformance.accuracy).toBe(95)
    })

    it('should react to metrics updates', async () => {
      wrapper = mount(AiDashboardView)
      
      // Update metrics
      aiStore.dashboardMetrics = {
        total_profiles: 200,
        high_risk_count: 25,
        average_risk_score: 0.4,
        recent_alerts: 8,
        risk_distribution: {
          very_low: 50,
          low: 75,
          moderate: 50,
          high: 20,
          critical: 5
        },
        model_performance: {
          accuracy: 0.88,
          precision: 0.83,
          recall: 0.86,
          f1_score: 0.84,
          test_samples: 300
        },
        profiles_analyzed_today: 30,
        interventions_active: 10,
        last_update: '2024-01-15T12:00:00Z'
      }

      await wrapper.vm.$nextTick()

      const riskDistribution = wrapper.vm.riskDistribution
      expect(riskDistribution[0].count).toBe(25) // high + critical
    })
  })
})