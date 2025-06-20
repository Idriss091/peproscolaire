import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/vue'
import { setActivePinia, createPinia } from 'pinia'
import { renderWithProviders, createMockApiResponse, createMockRiskProfile, createMockAlert } from '@/test/utils'
import DashboardView from '../DashboardView.vue'
import { useAuthStore } from '@/stores/auth'
import { useRiskDetectionStore } from '@/stores/risk-detection'

// Mock the API
vi.mock('@/api/risk-detection', () => ({
  riskDetectionAPI: {
    getDashboard: vi.fn(),
    getRiskProfiles: vi.fn(),
    getAlerts: vi.fn()
  }
}))

// Mock chart component
vi.mock('@/components/charts/RiskDistributionChart.vue', () => ({
  default: {
    name: 'RiskDistributionChart',
    template: '<div data-testid="risk-chart">Risk Chart</div>'
  }
}))

// Mock real-time status component
vi.mock('@/components/dashboard/RealTimeStatus.vue', () => ({
  default: {
    name: 'RealTimeStatus',
    template: '<div data-testid="realtime-status">Real-time Status</div>'
  }
}))

describe('DashboardView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders dashboard layout correctly', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    const mockDashboardData = {
      summary: {
        total_students: 150,
        at_risk_students: 25,
        monitored_students: 15,
        active_interventions: 8,
        unacknowledged_alerts: 3
      },
      risk_distribution: {
        very_low: 50,
        low: 40,
        moderate: 35,
        high: 20,
        critical: 5
      }
    }

    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse(mockDashboardData)
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    // Check main heading
    expect(screen.getByText('Tableau de bord')).toBeInTheDocument()

    // Wait for data to load and check statistics
    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument() // Total students
      expect(screen.getByText('25')).toBeInTheDocument() // At risk students
      expect(screen.getByText('15')).toBeInTheDocument() // Monitored students
      expect(screen.getByText('8')).toBeInTheDocument() // Active interventions
      expect(screen.getByText('3')).toBeInTheDocument() // Unacknowledged alerts
    })
  })

  it('shows loading states correctly', () => {
    const { riskDetectionAPI } = import('@/api/risk-detection')
    
    // Mock delayed API responses
    riskDetectionAPI.then(api => {
      api.riskDetectionAPI.getDashboard = vi.fn().mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )
      api.riskDetectionAPI.getAlerts = vi.fn().mockImplementation(
        () => new Promise(() => {})
      )
      api.riskDetectionAPI.getRiskProfiles = vi.fn().mockImplementation(
        () => new Promise(() => {})
      )
    })

    renderWithProviders(DashboardView)

    // Should show loading spinners
    const loadingSpinners = screen.getAllByRole('status')
    expect(loadingSpinners.length).toBeGreaterThan(0)
  })

  it('displays recent alerts section', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    const mockAlerts = [
      createMockAlert({
        id: '1',
        title: 'Risque critique détecté',
        message: 'Élève en difficulté',
        is_acknowledged: false
      }),
      createMockAlert({
        id: '2',
        title: 'Absence prolongée',
        message: 'Pattern d\'absence détecté',
        is_acknowledged: true
      })
    ]

    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: mockAlerts, count: 2 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.getByText('Alertes récentes')).toBeInTheDocument()
      expect(screen.getByText('Risque critique détecté')).toBeInTheDocument()
      expect(screen.getByText('Absence prolongée')).toBeInTheDocument()
    })
  })

  it('displays high-risk students table for authorized users', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: '1',
      email: 'teacher@example.com',
      first_name: 'Test',
      last_name: 'Teacher',
      user_type: 'teacher',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }

    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    const mockProfiles = [
      createMockRiskProfile({
        id: '1',
        risk_level: 'high',
        risk_score: 85
      })
    ]

    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: mockProfiles, count: 1 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.getByText('Élèves à risque élevé')).toBeInTheDocument()
    })
  })

  it('hides high-risk students section for unauthorized users', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: '1',
      email: 'student@example.com',
      first_name: 'Test',
      last_name: 'Student',
      user_type: 'student',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }

    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.queryByText('Élèves à risque élevé')).not.toBeInTheDocument()
    })
  })

  it('renders risk distribution chart', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({
        summary: {},
        risk_distribution: { high: 10, low: 20 }
      })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.getByText('Distribution des risques')).toBeInTheDocument()
      expect(screen.getByTestId('risk-chart')).toBeInTheDocument()
    })
  })

  it('renders real-time status component', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.getByTestId('realtime-status')).toBeInTheDocument()
    })
  })

  it('formats dates correctly', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    const mockAlert = createMockAlert({
      created_at: '2024-01-01T12:00:00Z'
    })

    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [mockAlert], count: 1 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    renderWithProviders(DashboardView)

    await waitFor(() => {
      // Should display relative time format (e.g., "il y a 2 heures")
      expect(screen.getByText(/il y a/)).toBeInTheDocument()
    })
  })

  it('handles empty states correctly', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    riskDetectionAPI.getDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    riskDetectionAPI.getAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    riskDetectionAPI.getRiskProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    const authStore = useAuthStore()
    authStore.user = {
      id: '1',
      email: 'teacher@example.com',
      first_name: 'Test',
      last_name: 'Teacher',
      user_type: 'teacher',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(screen.getByText('Aucune alerte récente')).toBeInTheDocument()
      expect(screen.getByText('Aucun élève à risque élevé')).toBeInTheDocument()
    })
  })

  it('calls correct API endpoints on mount', async () => {
    const { riskDetectionAPI } = await import('@/api/risk-detection')
    
    const mockDashboard = vi.fn().mockResolvedValue(
      createMockApiResponse({ summary: {}, risk_distribution: {} })
    )
    const mockAlerts = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )
    const mockProfiles = vi.fn().mockResolvedValue(
      createMockApiResponse({ results: [], count: 0 }, true)
    )

    riskDetectionAPI.getDashboard = mockDashboard
    riskDetectionAPI.getAlerts = mockAlerts
    riskDetectionAPI.getRiskProfiles = mockProfiles

    renderWithProviders(DashboardView)

    await waitFor(() => {
      expect(mockDashboard).toHaveBeenCalled()
      expect(mockAlerts).toHaveBeenCalledWith({
        is_acknowledged: false,
        ordering: '-created_at',
        page_size: 5
      })
      expect(mockProfiles).toHaveBeenCalledWith({
        risk_level__in: 'high,critical',
        ordering: '-risk_score',
        page_size: 10
      })
    })
  })
})