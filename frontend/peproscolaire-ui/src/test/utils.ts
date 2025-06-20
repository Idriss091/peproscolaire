import { render, RenderOptions } from '@testing-library/vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { vi } from 'vitest'
import type { Component } from 'vue'

// Mock router for testing
export const createMockRouter = (initialRoute = '/') => {
  return createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/login', component: { template: '<div>Login</div>' } },
      { path: '/risk-detection/profiles', component: { template: '<div>Risk Profiles</div>' } },
      { path: '/risk-detection/alerts', component: { template: '<div>Alerts</div>' } },
      { path: '/risk-detection/interventions', component: { template: '<div>Interventions</div>' } },
      { path: '/settings', component: { template: '<div>Settings</div>' } },
      { path: '/:pathMatch(.*)*', component: { template: '<div>Not Found</div>' } }
    ]
  })
}

// Custom render function with Vue ecosystem setup
export const renderWithProviders = (
  component: Component,
  options: RenderOptions & {
    initialRoute?: string
    piniaInitialState?: any
    routerMock?: boolean
  } = {}
) => {
  const {
    initialRoute = '/',
    piniaInitialState = {},
    routerMock = true,
    ...renderOptions
  } = options

  // Create Pinia store
  const pinia = createPinia()

  // Create router
  const router = routerMock ? createMockRouter(initialRoute) : undefined

  // Set initial route
  if (router && initialRoute !== '/') {
    router.push(initialRoute)
  }

  const globalPlugins = [pinia]
  if (router) {
    globalPlugins.push(router)
  }

  return render(component, {
    global: {
      plugins: globalPlugins,
      ...renderOptions.global
    },
    ...renderOptions
  })
}

// Mock user data factory
export const createMockUser = (overrides = {}) => ({
  id: '1',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  user_type: 'teacher' as const,
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
})

// Mock risk profile data factory
export const createMockRiskProfile = (overrides = {}) => ({
  id: '1',
  student: createMockUser({ user_type: 'student' }),
  academic_year: {
    id: '1',
    name: '2024-2025',
    start_date: '2024-09-01',
    end_date: '2025-06-30',
    is_current: true
  },
  risk_score: 75,
  risk_level: 'high' as const,
  academic_risk: 80,
  attendance_risk: 70,
  behavioral_risk: 60,
  social_risk: 85,
  risk_factors: {},
  indicators: {},
  dropout_probability: 0.75,
  recommendations: ['Suivi personnalisé'],
  priority_actions: ['Entretien avec les parents'],
  last_analysis: '2024-01-01T00:00:00Z',
  analysis_version: '1.0',
  is_monitored: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
})

// Mock alert data factory
export const createMockAlert = (overrides = {}) => ({
  id: '1',
  risk_profile: createMockRiskProfile(),
  alert_configuration: {
    id: '1',
    name: 'Test Alert',
    alert_type: 'risk_increase',
    description: 'Test description',
    notify_student: false,
    notify_parents: true,
    notify_main_teacher: true,
    notify_administration: false,
    additional_recipients: [],
    is_active: true,
    priority: 'high' as const,
    cooldown_days: 7,
    message_template: 'Test message',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  title: 'Test Alert',
  message: 'This is a test alert',
  priority: 'high' as const,
  context_data: {},
  is_read: false,
  read_by: [],
  is_acknowledged: false,
  actions_taken: '',
  notifications_sent: {},
  created_at: '2024-01-01T00:00:00Z',
  ...overrides
})

// Mock intervention plan data factory
export const createMockInterventionPlan = (overrides = {}) => ({
  id: '1',
  title: 'Test Intervention Plan',
  description: 'Test description',
  risk_profile: createMockRiskProfile(),
  status: 'active' as const,
  priority: 'normal' as const,
  start_date: '2024-01-01',
  target_date: '2024-06-01',
  progress_percentage: 50,
  objectives: [
    {
      id: '1',
      description: 'Test objective',
      target_date: '2024-03-01',
      priority: 'normal' as const,
      status: 'pending' as const,
      created_at: '2024-01-01T00:00:00Z'
    }
  ],
  actions: [
    {
      id: '1',
      title: 'Test action',
      description: 'Test action description',
      due_date: '2024-02-01',
      priority: 'normal' as const,
      status: 'pending' as const,
      created_at: '2024-01-01T00:00:00Z'
    }
  ],
  participants: [createMockUser()],
  created_by: createMockUser(),
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
})

// Mock notification data factory
export const createMockNotification = (overrides = {}) => ({
  id: '1',
  title: 'Test Notification',
  message: 'This is a test notification',
  type: 'info' as const,
  read: false,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides
})

// API response mocks
export const createMockApiResponse = <T>(data: T, pagination = false) => {
  if (pagination) {
    return {
      data: {
        count: Array.isArray(data) ? data.length : 1,
        next: null,
        previous: null,
        results: Array.isArray(data) ? data : [data]
      },
      error: null
    }
  }
  
  return {
    data,
    error: null
  }
}

export const createMockApiError = (message = 'Test error', status = 400) => ({
  data: null,
  error: {
    message,
    status,
    details: {}
  }
})

// Event simulation helpers
export const fireEvent = {
  click: (element: Element) => {
    element.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  },
  input: (element: Element, value: string) => {
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      element.value = value
      element.dispatchEvent(new Event('input', { bubbles: true }))
    }
  },
  submit: (element: Element) => {
    element.dispatchEvent(new Event('submit', { bubbles: true }))
  },
  keyDown: (element: Element, key: string) => {
    element.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true }))
  }
}

// Wait utilities
export const waitFor = (condition: () => boolean, timeout = 1000): Promise<void> => {
  return new Promise((resolve, reject) => {
    const start = Date.now()
    const check = () => {
      if (condition()) {
        resolve()
      } else if (Date.now() - start > timeout) {
        reject(new Error('Timeout waiting for condition'))
      } else {
        setTimeout(check, 10)
      }
    }
    check()
  })
}

// Mock implementations
export const mockFetch = (response: any, ok = true) => {
  return vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 400,
    json: () => Promise.resolve(response),
    text: () => Promise.resolve(JSON.stringify(response))
  })
}

export const mockLocalStorage = () => {
  const storage: Record<string, string> = {}
  
  return {
    getItem: vi.fn((key: string) => storage[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      storage[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete storage[key]
    }),
    clear: vi.fn(() => {
      Object.keys(storage).forEach(key => delete storage[key])
    })
  }
}

// Component testing helpers
export const getByTestId = (container: Element, testId: string) => {
  return container.querySelector(`[data-testid="${testId}"]`)
}

export const getAllByTestId = (container: Element, testId: string) => {
  return container.querySelectorAll(`[data-testid="${testId}"]`)
}

// Date/time testing utilities
export const mockDate = (dateString: string) => {
  const mockDate = new Date(dateString)
  vi.useFakeTimers()
  vi.setSystemTime(mockDate)
  return mockDate
}

export const restoreDate = () => {
  vi.useRealTimers()
}