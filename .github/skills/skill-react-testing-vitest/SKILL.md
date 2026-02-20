---
name: skill-react-testing-vitest
description: Test React components and hooks using Vitest and Testing Library. Includes unit tests, integration tests, mocking patterns, and snapshot testing. Use when building robust UI components requiring coverage validation and regression prevention.
---

# React Component Testing (Vitest + Testing Library)

## Quick Start

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ExpedienteForm from './ExpedienteForm';

describe('ExpedienteForm', () => {
  it('renders form with required fields', () => {
    render(<ExpedienteForm />);
    expect(screen.getByLabelText(/asunto/i)).toBeInTheDocument();
  });
  
  it('submits form with valid data', async () => {
    const mockSubmit = vi.fn();
    render(<ExpedienteForm onSubmit={mockSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/asunto/i), { target: { value: 'Test' } });
    fireEvent.click(screen.getByText(/submit/i));
    
    expect(mockSubmit).toHaveBeenCalled();
  });
});
```

See [references/component-testing.md](references/component-testing.md):
- Setup Vitest config
- Render components in tests
- Assert DOM elements

See [references/hooks-testing.md](references/hooks-testing.md):
- Test custom hooks (useAuth, useExpedientes)
- Mock API calls
- Test state updates
