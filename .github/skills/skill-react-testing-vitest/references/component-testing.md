# Component Testing Patterns

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProtectedRoute from './ProtectedRoute';

describe('ProtectedRoute', () => {
  it('renders component for authenticated user', () => {
    const mockUser = { id: '1', roles: ['FUNCIONARIO'] };
    render(<ProtectedRoute requiredRole="FUNCIONARIO" user={mockUser} />);
    expect(screen.getByText(/protected/i)).toBeInTheDocument();
  });
  
  it('redirects unauthenticated user', () => {
    render(<ProtectedRoute requiredRole="ADMIN" user={null} />);
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });
});
```

# Hooks Testing

```javascript
import { renderHook, act } from '@testing-library/react';
import useAuth from './useAuth';

describe('useAuth hook', () => {
  it('returns user after login', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login('user', 'pass');
    });
    
    expect(result.current.user).toBeDefined();
    expect(result.current.isLoading).toBe(false);
  });
});
```
