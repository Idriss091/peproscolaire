/**
 * Configuration globale pour les tests Vitest
 */
import { beforeAll, afterAll, afterEach } from 'vitest'
import { cleanup } from '@vue/test-utils'
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
  cleanup()
})

// Nettoyage global
afterAll(() => {
  // Restaurer les méthodes originales si nécessaire
})