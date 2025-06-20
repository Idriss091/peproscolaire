/**
 * Configuration globale pour les tests Vitest
 */
import { beforeAll, afterAll, afterEach, vi } from 'vitest'
import { config } from '@vue/test-utils'

// Configuration globale des composants de test
config.global.stubs = {
  // Stub des composants tiers
  'router-link': {
    template: '<a><slot /></a>',
    props: ['to']
  },
  'router-view': {
    template: '<div><slot /></div>'
  }
}

// Mock global de l'API client
vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

// Mock du client API
vi.mock('@/api/client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  },
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

// Configuration des mocks globaux
beforeAll(() => {
  // Mock de window.matchMedia pour les tests de responsive design
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => {},
    }),
  })

  // Mock de ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  // Mock de IntersectionObserver
  global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  // Mock de window.scrollTo
  window.scrollTo = () => {}

  // Mock de console methods pour les tests
  const originalError = console.error
  console.error = (...args: any[]) => {
    // Ignorer certaines erreurs attendues dans les tests
    const errorMessage = args[0]
    if (
      typeof errorMessage === 'string' &&
      (errorMessage.includes('Vue warn') ||
       errorMessage.includes('Failed to resolve component'))
    ) {
      return
    }
    originalError.apply(console, args)
  }
})

// Nettoyage après chaque test
afterEach(() => {
  // Le nettoyage est géré automatiquement par Vue Test Utils
  document.body.innerHTML = ''
})

// Nettoyage global
afterAll(() => {
  // Restaurer les méthodes originales si nécessaire
})