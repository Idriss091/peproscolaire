# Testing Guide

This document provides comprehensive guidelines for testing the Vue.js application.

## Testing Stack

- **Vitest**: Fast unit test framework
- **Vue Testing Library**: Component testing utilities
- **jsdom**: DOM environment for tests
- **User Event**: Simulate user interactions
- **Coverage**: V8 coverage provider

## Test Structure

```
src/
├── test/
│   ├── setup.ts          # Global test setup
│   ├── utils.ts          # Testing utilities
│   └── README.md         # This file
├── components/
│   └── **/__tests__/     # Component tests
├── stores/
│   └── **/__tests__/     # Store tests
├── services/
│   └── **/__tests__/     # Service tests
└── views/
    └── **/__tests__/     # View tests
```

## Test Scripts

```bash
# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run tests with coverage
npm run test:coverage

# Open test UI
npm run test:ui

# Run tests in watch mode
npm run test:watch
```

## Writing Tests

### Component Testing

```typescript
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '@/test/utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    renderWithProviders(MyComponent, {
      props: { title: 'Test' }
    })

    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('handles user interactions', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    renderWithProviders(MyComponent, {
      props: { onClick: handleClick }
    })

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalled()
  })
})
```

### Store Testing

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMyStore } from '../myStore'

describe('My Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('has correct initial state', () => {
    const store = useMyStore()
    expect(store.items).toEqual([])
  })

  it('adds items correctly', () => {
    const store = useMyStore()
    store.addItem({ id: '1', name: 'Test' })
    expect(store.items).toHaveLength(1)
  })
})
```

### Service Testing

```typescript
import { describe, it, expect, vi } from 'vitest'
import { myService } from '../myService'

// Mock dependencies
vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('My Service', () => {
  it('fetches data correctly', async () => {
    const { apiClient } = await import('@/api/client')
    apiClient.get = vi.fn().mockResolvedValue({ data: 'test' })

    const result = await myService.getData()
    expect(result).toBe('test')
  })
})
```

## Testing Utilities

### renderWithProviders

Custom render function that sets up Vue ecosystem:

```typescript
renderWithProviders(Component, {
  props: { ... },
  slots: { ... },
  initialRoute: '/custom-route',
  piniaInitialState: { ... },
  routerMock: true
})
```

### Mock Data Factories

```typescript
import {
  createMockUser,
  createMockRiskProfile,
  createMockAlert,
  createMockInterventionPlan,
  createMockNotification
} from '@/test/utils'

const user = createMockUser({ user_type: 'admin' })
const profile = createMockRiskProfile({ risk_level: 'high' })
```

### API Response Mocks

```typescript
import { createMockApiResponse, createMockApiError } from '@/test/utils'

const successResponse = createMockApiResponse(data, true) // with pagination
const errorResponse = createMockApiError('Error message', 400)
```

## Best Practices

### 1. Test Structure

- **Arrange**: Set up test data and mocks
- **Act**: Execute the code under test
- **Assert**: Verify the results

### 2. Test Naming

```typescript
describe('ComponentName', () => {
  describe('when user is authenticated', () => {
    it('should display user menu', () => {
      // test implementation
    })
  })

  describe('when user clicks submit', () => {
    it('should call onSubmit handler', () => {
      // test implementation
    })
  })
})
```

### 3. Mock Guidelines

- Mock external dependencies
- Use `vi.fn()` for function mocks
- Mock at the module level when possible
- Reset mocks between tests

```typescript
vi.mock('@/api/auth', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn()
  }
}))
```

### 4. User Interactions

Always use `@testing-library/user-event` for user interactions:

```typescript
const user = userEvent.setup()
await user.click(button)
await user.type(input, 'text')
await user.selectOptions(select, 'option1')
```

### 5. Async Testing

Handle async operations properly:

```typescript
it('loads data on mount', async () => {
  renderWithProviders(Component)
  
  expect(screen.getByText('Loading...')).toBeInTheDocument()
  
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument()
  })
})
```

### 6. Error Testing

Test error states and edge cases:

```typescript
it('handles API errors gracefully', async () => {
  apiClient.get.mockRejectedValue(new Error('Network error'))
  
  renderWithProviders(Component)
  
  await waitFor(() => {
    expect(screen.getByText('Error loading data')).toBeInTheDocument()
  })
})
```

## Coverage Guidelines

Maintain minimum coverage thresholds:
- **Statements**: 70%
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%

Focus on testing:
- Critical business logic
- User interactions
- Error handling
- Edge cases
- Integration points

## Common Testing Patterns

### Testing Form Validation

```typescript
it('validates required fields', async () => {
  const user = userEvent.setup()
  renderWithProviders(LoginForm)

  await user.click(screen.getByRole('button', { name: 'Submit' }))
  
  expect(screen.getByText('Email is required')).toBeInTheDocument()
  expect(screen.getByText('Password is required')).toBeInTheDocument()
})
```

### Testing Navigation

```typescript
it('navigates to correct route', async () => {
  const { router } = renderWithProviders(Component)
  
  await user.click(screen.getByText('Go to Dashboard'))
  
  expect(router.currentRoute.value.path).toBe('/dashboard')
})
```

### Testing Loading States

```typescript
it('shows loading spinner during API call', async () => {
  let resolvePromise: (value: any) => void
  apiClient.get.mockReturnValue(new Promise(resolve => {
    resolvePromise = resolve
  }))

  renderWithProviders(Component)
  
  expect(screen.getByRole('status')).toBeInTheDocument()
  
  resolvePromise!(mockData)
  
  await waitFor(() => {
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})
```

### Testing WebSocket Integration

```typescript
it('handles WebSocket messages', async () => {
  const { webSocketService } = await import('@/services/websocket')
  
  renderWithProviders(Component)
  
  // Simulate WebSocket message
  webSocketService.handleMessage({
    type: 'notification',
    data: { title: 'Test', message: 'Test message' }
  })
  
  await waitFor(() => {
    expect(screen.getByText('Test message')).toBeInTheDocument()
  })
})
```

## Debugging Tests

### 1. Use screen.debug()

```typescript
it('debugs component structure', () => {
  renderWithProviders(Component)
  screen.debug() // Prints DOM structure
})
```

### 2. Test Queries

```typescript
// Find elements
screen.getByText('text')           // Throws if not found
screen.queryByText('text')         // Returns null if not found
screen.findByText('text')          // Async, waits for element

// Multiple elements
screen.getAllByText('text')
screen.queryAllByText('text')
screen.findAllByText('text')
```

### 3. Custom Queries

```typescript
const customButton = screen.getByRole('button', { 
  name: /submit/i 
})

const inputField = screen.getByLabelText(/email/i)
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Main branch pushes
- Release builds

Ensure all tests pass before merging code.

## Performance Testing

For performance-critical components:

```typescript
it('renders large lists efficiently', () => {
  const items = Array.from({ length: 1000 }, (_, i) => ({ id: i }))
  
  const start = performance.now()
  renderWithProviders(LargeList, { props: { items } })
  const end = performance.now()
  
  expect(end - start).toBeLessThan(100) // 100ms threshold
})
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Testing Library](https://testing-library.com/docs/vue-testing-library/intro/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Mock Service Worker](https://mswjs.io/) - For API mocking