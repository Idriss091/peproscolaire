import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '@/test/utils'
import BaseButton from '../BaseButton.vue'

describe('BaseButton', () => {
  it('renders with default props', () => {
    renderWithProviders(BaseButton, {
      slots: {
        default: 'Click me'
      }
    })

    const button = screen.getByRole('button', { name: 'Click me' })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('bg-primary-600', 'text-white')
  })

  it('applies variant classes correctly', () => {
    const { rerender } = renderWithProviders(BaseButton, {
      props: { variant: 'secondary' },
      slots: { default: 'Secondary' }
    })

    let button = screen.getByRole('button')
    expect(button).toHaveClass('bg-white', 'text-gray-700', 'border-gray-300')

    rerender({ variant: 'danger' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('bg-red-600', 'text-white')

    rerender({ variant: 'success' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('bg-green-600', 'text-white')

    rerender({ variant: 'warning' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('bg-yellow-600', 'text-white')

    rerender({ variant: 'ghost' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('text-gray-700', 'hover:bg-gray-50')
  })

  it('applies size classes correctly', () => {
    const { rerender } = renderWithProviders(BaseButton, {
      props: { size: 'xs' },
      slots: { default: 'Extra Small' }
    })

    let button = screen.getByRole('button')
    expect(button).toHaveClass('px-2.5', 'py-1.5', 'text-xs')

    rerender({ size: 'sm' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('px-3', 'py-2', 'text-sm')

    rerender({ size: 'lg' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('px-4', 'py-2', 'text-base')

    rerender({ size: 'xl' })
    button = screen.getByRole('button')
    expect(button).toHaveClass('px-6', 'py-3', 'text-base')
  })

  it('handles disabled state', () => {
    renderWithProviders(BaseButton, {
      props: { disabled: true },
      slots: { default: 'Disabled' }
    })

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveClass('opacity-50', 'cursor-not-allowed')
  })

  it('shows loading state', () => {
    renderWithProviders(BaseButton, {
      props: { loading: true },
      slots: { default: 'Loading' }
    })

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveClass('opacity-50', 'cursor-not-allowed')
    
    // Check for loading spinner
    const spinner = button.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('emits click event when clicked', async () => {
    const user = userEvent.setup()
    const clickHandler = vi.fn()

    renderWithProviders(BaseButton, {
      props: { onClick: clickHandler },
      slots: { default: 'Clickable' }
    })

    const button = screen.getByRole('button')
    await user.click(button)

    expect(clickHandler).toHaveBeenCalledTimes(1)
  })

  it('does not emit click when disabled', async () => {
    const user = userEvent.setup()
    const clickHandler = vi.fn()

    renderWithProviders(BaseButton, {
      props: { 
        disabled: true,
        onClick: clickHandler 
      },
      slots: { default: 'Disabled' }
    })

    const button = screen.getByRole('button')
    await user.click(button)

    expect(clickHandler).not.toHaveBeenCalled()
  })

  it('does not emit click when loading', async () => {
    const user = userEvent.setup()
    const clickHandler = vi.fn()

    renderWithProviders(BaseButton, {
      props: { 
        loading: true,
        onClick: clickHandler 
      },
      slots: { default: 'Loading' }
    })

    const button = screen.getByRole('button')
    await user.click(button)

    expect(clickHandler).not.toHaveBeenCalled()
  })

  it('renders as different HTML elements based on type', () => {
    const { rerender } = renderWithProviders(BaseButton, {
      props: { type: 'submit' },
      slots: { default: 'Submit' }
    })

    let button = screen.getByRole('button')
    expect(button).toHaveAttribute('type', 'submit')

    rerender({ type: 'reset' })
    button = screen.getByRole('button')
    expect(button).toHaveAttribute('type', 'reset')
  })

  it('applies full width when specified', () => {
    renderWithProviders(BaseButton, {
      props: { fullWidth: true },
      slots: { default: 'Full Width' }
    })

    const button = screen.getByRole('button')
    expect(button).toHaveClass('w-full')
  })

  it('applies custom classes', () => {
    renderWithProviders(BaseButton, {
      props: { class: 'custom-class' },
      slots: { default: 'Custom' }
    })

    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('handles keyboard events', async () => {
    const user = userEvent.setup()
    const clickHandler = vi.fn()

    renderWithProviders(BaseButton, {
      props: { onClick: clickHandler },
      slots: { default: 'Keyboard' }
    })

    const button = screen.getByRole('button')
    
    // Test Enter key
    button.focus()
    await user.keyboard('{Enter}')
    expect(clickHandler).toHaveBeenCalledTimes(1)

    // Test Space key
    await user.keyboard(' ')
    expect(clickHandler).toHaveBeenCalledTimes(2)
  })

  it('renders icon with text', () => {
    renderWithProviders(BaseButton, {
      slots: {
        default: () => [
          'Icon Button'
        ]
      }
    })

    const button = screen.getByRole('button', { name: 'Icon Button' })
    expect(button).toBeInTheDocument()
  })

  it('maintains accessibility attributes', () => {
    renderWithProviders(BaseButton, {
      props: { 
        'aria-label': 'Custom aria label',
        'aria-describedby': 'help-text'
      },
      slots: { default: 'Accessible' }
    })

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-label', 'Custom aria label')
    expect(button).toHaveAttribute('aria-describedby', 'help-text')
  })
})