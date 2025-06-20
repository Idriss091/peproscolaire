import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, createMockRiskProfile } from '@/test/utils'
import RiskProfileCard from '../RiskProfileCard.vue'

describe('RiskProfileCard', () => {
  const mockProfile = createMockRiskProfile({
    student: {
      id: '1',
      first_name: 'Jean',
      last_name: 'Dupont',
      email: 'jean.dupont@example.com',
      user_type: 'student',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    risk_score: 75,
    risk_level: 'high',
    academic_risk: 80,
    attendance_risk: 70,
    behavioral_risk: 60,
    social_risk: 85
  })

  it('renders profile information correctly', () => {
    renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    expect(screen.getByText('jean.dupont@example.com')).toBeInTheDocument()
    expect(screen.getByText('75/100')).toBeInTheDocument()
  })

  it('displays correct risk level badge', () => {
    const { rerender } = renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    expect(screen.getByText('Élevé')).toBeInTheDocument()
    expect(screen.getByText('Élevé')).toHaveClass('bg-red-100', 'text-red-800')

    // Test different risk levels
    rerender({
      profile: {
        ...mockProfile,
        risk_level: 'low',
        risk_score: 25
      }
    })

    expect(screen.getByText('Faible')).toBeInTheDocument()
    expect(screen.getByText('Faible')).toHaveClass('bg-green-100', 'text-green-800')
  })

  it('shows risk factor breakdown', () => {
    renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    expect(screen.getByText('Académique:')).toBeInTheDocument()
    expect(screen.getByText('80')).toBeInTheDocument()
    expect(screen.getByText('Présence:')).toBeInTheDocument()
    expect(screen.getByText('70')).toBeInTheDocument()
    expect(screen.getByText('Comportement:')).toBeInTheDocument()
    expect(screen.getByText('60')).toBeInTheDocument()
    expect(screen.getByText('Social:')).toBeInTheDocument()
    expect(screen.getByText('85')).toBeInTheDocument()
  })

  it('emits view-details event when card is clicked', async () => {
    const user = userEvent.setup()
    const viewDetailsHandler = vi.fn()

    renderWithProviders(RiskProfileCard, {
      props: { 
        profile: mockProfile,
        'onView-details': viewDetailsHandler
      }
    })

    const card = screen.getByRole('article')
    await user.click(card)

    expect(viewDetailsHandler).toHaveBeenCalledWith(mockProfile)
  })

  it('emits start-monitoring event when monitor button is clicked', async () => {
    const user = userEvent.setup()
    const startMonitoringHandler = vi.fn()

    const unmonitoredProfile = {
      ...mockProfile,
      is_monitored: false
    }

    renderWithProviders(RiskProfileCard, {
      props: { 
        profile: unmonitoredProfile,
        'onStart-monitoring': startMonitoringHandler
      }
    })

    const monitorButton = screen.getByText('Surveiller')
    await user.click(monitorButton)

    expect(startMonitoringHandler).toHaveBeenCalledWith(unmonitoredProfile.id)
  })

  it('shows monitoring status correctly', () => {
    const { rerender } = renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    expect(screen.getByText('Surveillé')).toBeInTheDocument()

    rerender({
      profile: {
        ...mockProfile,
        is_monitored: false
      }
    })

    expect(screen.getByText('Surveiller')).toBeInTheDocument()
  })

  it('displays last analysis date', () => {
    renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    expect(screen.getByText(/Dernière analyse/)).toBeInTheDocument()
  })

  it('shows priority actions when available', () => {
    const profileWithActions = {
      ...mockProfile,
      priority_actions: [
        'Entretien avec les parents',
        'Suivi personnalisé'
      ]
    }

    renderWithProviders(RiskProfileCard, {
      props: { profile: profileWithActions }
    })

    expect(screen.getByText('Actions prioritaires:')).toBeInTheDocument()
    expect(screen.getByText('Entretien avec les parents')).toBeInTheDocument()
    expect(screen.getByText('Suivi personnalisé')).toBeInTheDocument()
  })

  it('handles empty priority actions', () => {
    const profileWithoutActions = {
      ...mockProfile,
      priority_actions: []
    }

    renderWithProviders(RiskProfileCard, {
      props: { profile: profileWithoutActions }
    })

    expect(screen.queryByText('Actions prioritaires:')).not.toBeInTheDocument()
  })

  it('applies correct risk score color classes', () => {
    const { rerender } = renderWithProviders(RiskProfileCard, {
      props: { profile: { ...mockProfile, risk_score: 25 } }
    })

    let scoreElement = screen.getByText('25/100')
    expect(scoreElement).toHaveClass('text-green-600')

    rerender({ profile: { ...mockProfile, risk_score: 50 } })
    scoreElement = screen.getByText('50/100')
    expect(scoreElement).toHaveClass('text-yellow-600')

    rerender({ profile: { ...mockProfile, risk_score: 75 } })
    scoreElement = screen.getByText('75/100')
    expect(scoreElement).toHaveClass('text-red-600')

    rerender({ profile: { ...mockProfile, risk_score: 95 } })
    scoreElement = screen.getByText('95/100')
    expect(scoreElement).toHaveClass('text-red-700')
  })

  it('shows assigned staff member when available', () => {
    const profileWithAssignment = {
      ...mockProfile,
      assigned_to: {
        id: '2',
        first_name: 'Marie',
        last_name: 'Martin',
        email: 'marie.martin@example.com',
        user_type: 'teacher' as const,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    }

    renderWithProviders(RiskProfileCard, {
      props: { profile: profileWithAssignment }
    })

    expect(screen.getByText('Assigné à:')).toBeInTheDocument()
    expect(screen.getByText('Marie Martin')).toBeInTheDocument()
  })

  it('displays dropout probability when available', () => {
    const profileWithDropoutProb = {
      ...mockProfile,
      dropout_probability: 0.75
    }

    renderWithProviders(RiskProfileCard, {
      props: { profile: profileWithDropoutProb }
    })

    expect(screen.getByText('Probabilité de décrochage:')).toBeInTheDocument()
    expect(screen.getByText('75%')).toBeInTheDocument()
  })

  it('handles click events on action buttons without triggering card click', async () => {
    const user = userEvent.setup()
    const viewDetailsHandler = vi.fn()
    const startMonitoringHandler = vi.fn()

    const unmonitoredProfile = {
      ...mockProfile,
      is_monitored: false
    }

    renderWithProviders(RiskProfileCard, {
      props: { 
        profile: unmonitoredProfile,
        'onView-details': viewDetailsHandler,
        'onStart-monitoring': startMonitoringHandler
      }
    })

    const monitorButton = screen.getByText('Surveiller')
    await user.click(monitorButton)

    expect(startMonitoringHandler).toHaveBeenCalledTimes(1)
    expect(viewDetailsHandler).not.toHaveBeenCalled()
  })

  it('is accessible with proper ARIA attributes', () => {
    renderWithProviders(RiskProfileCard, {
      props: { profile: mockProfile }
    })

    const card = screen.getByRole('article')
    expect(card).toHaveAttribute('tabindex', '0')
    expect(card).toHaveClass('cursor-pointer')
  })
})