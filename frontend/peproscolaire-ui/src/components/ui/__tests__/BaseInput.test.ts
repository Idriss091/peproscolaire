import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '@/test/utils'
import BaseInput from '../BaseInput.vue'

describe('BaseInput', () => {
  it('renders with default props', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test Label'
      }
    })

    const input = screen.getByRole('textbox')
    const label = screen.getByText('Test Label')

    expect(input).toBeInTheDocument()
    expect(label).toBeInTheDocument()
    expect(input).toHaveClass('border-gray-300')
  })

  it('displays the current value', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: 'test value',
        label: 'Test'
      }
    })

    const input = screen.getByRole('textbox') as HTMLInputElement
    expect(input.value).toBe('test value')
  })

  it('emits update:modelValue when value changes', async () => {
    const user = userEvent.setup()
    const updateHandler = vi.fn()

    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        'onUpdate:modelValue': updateHandler
      }
    })

    const input = screen.getByRole('textbox')
    await user.type(input, 'new value')

    expect(updateHandler).toHaveBeenCalledWith('new value')
  })

  it('shows error state and message', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        error: 'This field is required'
      }
    })

    const input = screen.getByRole('textbox')
    const errorMessage = screen.getByText('This field is required')

    expect(input).toHaveClass('border-red-300', 'focus:border-red-500', 'focus:ring-red-500')
    expect(errorMessage).toBeInTheDocument()
    expect(errorMessage).toHaveClass('text-red-600')
  })

  it('shows help text', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        help: 'This is helpful information'
      }
    })

    const helpText = screen.getByText('This is helpful information')
    expect(helpText).toBeInTheDocument()
    expect(helpText).toHaveClass('text-gray-500')
  })

  it('handles disabled state', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        disabled: true
      }
    })

    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
    expect(input).toHaveClass('bg-gray-50', 'text-gray-500')
  })

  it('handles required state', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        required: true
      }
    })

    const input = screen.getByRole('textbox')
    const label = screen.getByText('Test *')

    expect(input).toBeRequired()
    expect(label).toBeInTheDocument()
  })

  it('handles different input types', () => {
    const { rerender } = renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Email',
        type: 'email'
      }
    })

    let input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('type', 'email')

    rerender({
      modelValue: '',
      label: 'Password',
      type: 'password'
    })

    input = screen.getByLabelText('Password')
    expect(input).toHaveAttribute('type', 'password')

    rerender({
      modelValue: 0,
      label: 'Number',
      type: 'number'
    })

    input = screen.getByRole('spinbutton')
    expect(input).toHaveAttribute('type', 'number')
  })

  it('renders placeholder text', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        placeholder: 'Enter some text...'
      }
    })

    const input = screen.getByPlaceholderText('Enter some text...')
    expect(input).toBeInTheDocument()
  })

  it('handles min and max attributes for number inputs', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: 5,
        label: 'Number',
        type: 'number',
        min: 0,
        max: 100
      }
    })

    const input = screen.getByRole('spinbutton')
    expect(input).toHaveAttribute('min', '0')
    expect(input).toHaveAttribute('max', '100')
  })

  it('renders prefix slot content', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test'
      },
      slots: {
        prefix: '<span data-testid="prefix">@</span>'
      }
    })

    const prefix = screen.getByTestId('prefix')
    expect(prefix).toBeInTheDocument()
    expect(prefix).toHaveTextContent('@')
  })

  it('renders suffix slot content', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test'
      },
      slots: {
        suffix: '<span data-testid="suffix">%</span>'
      }
    })

    const suffix = screen.getByTestId('suffix')
    expect(suffix).toBeInTheDocument()
    expect(suffix).toHaveTextContent('%')
  })

  it('handles focus and blur events', async () => {
    const user = userEvent.setup()
    const focusHandler = vi.fn()
    const blurHandler = vi.fn()

    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        onFocus: focusHandler,
        onBlur: blurHandler
      }
    })

    const input = screen.getByRole('textbox')
    
    await user.click(input)
    expect(focusHandler).toHaveBeenCalledTimes(1)

    await user.tab()
    expect(blurHandler).toHaveBeenCalledTimes(1)
  })

  it('applies custom CSS classes', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        class: 'custom-input-class'
      }
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('custom-input-class')
  })

  it('handles maxlength attribute', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        maxlength: 50
      }
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('maxlength', '50')
  })

  it('supports readonly attribute', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: 'readonly value',
        label: 'Test',
        readonly: true
      }
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('readonly')
    expect(input).toHaveClass('bg-gray-50')
  })

  it('shows character count when maxlength is set', async () => {
    const user = userEvent.setup()
    
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        maxlength: 10,
        showCount: true
      }
    })

    const input = screen.getByRole('textbox')
    await user.type(input, 'hello')

    const count = screen.getByText('5/10')
    expect(count).toBeInTheDocument()
  })

  it('maintains accessibility attributes', () => {
    renderWithProviders(BaseInput, {
      props: {
        modelValue: '',
        label: 'Test',
        'aria-describedby': 'help-text',
        error: 'Error message'
      }
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input).toHaveAttribute('aria-describedby')
  })
})