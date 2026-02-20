# Hook Testing with Vitest

## Testing Custom Hooks

```javascript
import { renderHook, act } from 'vitest';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('should increment counter', () => {
    const { result } = renderHook(() => useCounter());
    
    expect(result.current.count).toBe(0);
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('should decrement counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(-1);
  });
});
```

## Testing Async Hooks

```javascript
import { renderHook, waitFor } from 'vitest';
import { useFetchExpedientes } from './useFetchExpedientes';

describe('useFetchExpedientes', () => {
  test('should fetch expedientes on mount', async () => {
    const { result } = renderHook(() => useFetchExpedientes());
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });

  test('should handle fetch errors', async () => {
    // Mock API error
    vi.mock('./api', () => ({
      fetchExpedientes: vi.fn().mockRejectedValue(new Error('API Error'))
    }));
    
    const { result } = renderHook(() => useFetchExpedientes());
    
    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
    
    expect(result.current.error.message).toBe('API Error');
  });
});
```

## Testing Zustand Hooks

```javascript
import { renderHook, act } from 'vitest';
import { useExpedientesStore } from './store';

describe('useExpedientesStore', () => {
  beforeEach(() => {
    // Reset store state
    useExpedientesStore.setState({ expedientes: [] });
  });

  test('should add expediente', () => {
    const { result } = renderHook(() => useExpedientesStore());
    
    act(() => {
      result.current.addExpediente({
        id: 1,
        numero: 'EXP-2024-001',
        estado: 'iniciado'
      });
    });
    
    expect(result.current.expedientes).toHaveLength(1);
  });

  test('should update expediente', () => {
    const { result } = renderHook(() => useExpedientesStore());
    
    act(() => {
      result.current.addExpediente({ id: 1, numero: 'EXP-001' });
      result.current.updateExpediente(1, { estado: 'aprobado' });
    });
    
    expect(result.current.expedientes[0].estado).toBe('aprobado');
  });
});
```

## Testing useEffect Hooks

```javascript
import { renderHook, waitFor } from 'vitest';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  test('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );
    
    expect(result.current).toBe('initial');
    
    rerender({ value: 'updated', delay: 500 });
    
    expect(result.current).toBe('initial');
    
    await waitFor(() => {
      expect(result.current).toBe('updated');
    }, { timeout: 600 });
  });
});
```

## Testing Hook Dependencies

```javascript
import { renderHook } from 'vitest';
import { useMemo } from 'react';

describe('Hook dependencies', () => {
  test('should use correct dependencies', () => {
    const fn = vi.fn(() => ({ id: 1, name: 'test' }));
    
    const { rerender } = renderHook(
      ({ value }) => useMemo(() => fn(), [value]),
      { initialProps: { value: 'a' } }
    );
    
    expect(fn).toHaveBeenCalledTimes(1);
    
    rerender({ value: 'a' }); // Same value
    expect(fn).toHaveBeenCalledTimes(1); // Should not recompute
    
    rerender({ value: 'b' }); // Different value
    expect(fn).toHaveBeenCalledTimes(2); // Should recompute
  });
});
```

## Testing Hook Cleanup

```javascript
import { renderHook } from 'vitest';
import { useEffect } from 'react';

describe('Hook cleanup', () => {
  test('should cleanup on unmount', () => {
    const cleanup = vi.fn();
    
    const { unmount } = renderHook(() => {
      useEffect(() => {
        return cleanup;
      }, []);
    });
    
    expect(cleanup).not.toHaveBeenCalled();
    
    unmount();
    
    expect(cleanup).toHaveBeenCalled();
  });
});
```
