# Mocking Patterns for React Testing

## HTTP Client Mocking

```javascript
import { vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';


describe('API Mocking', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('should handle successful API response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, nombre: 'Juan' })
    });
    
    global.fetch = mockFetch;
    
    render(<UserComponent />);
    
    await waitFor(() => {
      expect(screen.getByText('Juan')).toBeInTheDocument();
    });
    
    expect(mockFetch).toHaveBeenCalledWith('/api/users/1');
  });

  test('should handle API errors', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found'
    });
    
    global.fetch = mockFetch;
    
    render(<UserComponent />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  test('should handle network errors', async () => {
    const mockFetch = vi.fn().mockRejectedValue(
      new Error('Network error')
    );
    
    global.fetch = mockFetch;
    
    render(<UserComponent />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

## Module Mocking

```javascript
import { vi } from 'vitest';

// Mock entire module
vi.mock('./api/expedientes', () => ({
  fetchExpedientes: vi.fn().mockResolvedValue([
    { id: 1, numero: 'EXP-001' },
    { id: 2, numero: 'EXP-002' }
  ])
}));

// Partial mock (keep some functions real)
vi.mock('./services/auth', async () => {
  const actual = await vi.importActual('./services/auth');
  return {
    ...actual,
    login: vi.fn().mockResolvedValue({ token: 'mock-token' })
  };
});
```

## Component Dependency Mocking

```javascript
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';


test('should render with mocked router', () => {
  const mockNavigate = vi.fn();
  
  // Mock useNavigate hook
  vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
      ...actual,
      useNavigate: () => mockNavigate
    };
  });
  
  render(
    <BrowserRouter>
      <NavigationComponent />
    </BrowserRouter>
  );
  
  // Verify navigation was called
  expect(mockNavigate).toHaveBeenCalled();
});
```

## Store Mocking (Zustand)

```javascript
import { vi } from 'vitest';
import { render, screen } from '@testing-library/react';


test('should use mock store', () => {
  const mockStore = {
    expedientes: [{ id: 1, numero: 'EXP-001' }],
    loading: false,
    error: null,
    fetchExpedientes: vi.fn()
  };
  
  vi.mock('./store', () => ({
    useExpedientesStore: () => mockStore
  }));
  
  render(<ExpedientesList />);
  
  expect(screen.getByText('EXP-001')).toBeInTheDocument();
});

test('should handle store updates', async () => {
  const mockStore = {
    expedientes: [],
    loading: true,
    fetchExpedientes: vi.fn(async () => {
      // Simulate async update
      mockStore.expedientes = [{ id: 1, numero: 'EXP-001' }];
      mockStore.loading = false;
    })
  };
  
  vi.mock('./store', () => ({
    useExpedientesStore: () => mockStore
  }));
  
  render(<ExpedientesList />);
  
  expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  
  await mockStore.fetchExpedientes();
  
  // Note: Would need re-render in real test
  expect(mockStore.expedientes).toHaveLength(1);
});
```

## LocalStorage Mocking

```javascript
import { vi } from 'vitest';


beforeEach(() => {
  // Clear mocks
  vi.clearAllMocks();
  
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn()
  };
  
  global.localStorage = localStorageMock;
});

test('should save to localStorage', () => {
  const { setItem } = global.localStorage;
  
  render(<PreferencesComponent />);
  
  expect(setItem).toHaveBeenCalledWith(
    'theme',
    'dark'
  );
});
```

## Event Mocking

```javascript
import { fireEvent, render } from '@testing-library/react';
import { vi } from 'vitest';


test('should handle click events', () => {
  const handleClick = vi.fn();
  
  const { getByRole } = render(
    <button onClick={handleClick}>Aprobar</button>
  );
  
  fireEvent.click(getByRole('button'));
  
  expect(handleClick).toHaveBeenCalledOnce();
});

test('should handle form submission', () => {
  const handleSubmit = vi.fn(e => e.preventDefault());
  
  const { container } = render(
    <form onSubmit={handleSubmit}>
      <input type="text" defaultValue="test" />
      <button type="submit">Enviar</button>
    </form>
  );
  
  fireEvent.submit(container.querySelector('form'));
  
  expect(handleSubmit).toHaveBeenCalledOnce();
});

test('should handle change events', () => {
  const handleChange = vi.fn();
  
  const { getByRole } = render(
    <input onChange={handleChange} />
  );
  
  fireEvent.change(getByRole('textbox'), {
    target: { value: 'new value' }
  });
  
  expect(handleChange).toHaveBeenCalledWith(
    expect.objectContaining({
      target: expect.objectContaining({
        value: 'new value'
      })
    })
  );
});
```

## Timer Mocking

```javascript
import { vi } from 'vitest';


test('should handle setTimeout', () => {
  vi.useFakeTimers();
  
  const callback = vi.fn();
  
  setTimeout(callback, 1000);
  
  expect(callback).not.toHaveBeenCalled();
  
  vi.advanceTimersByTime(1000);
  
  expect(callback).toHaveBeenCalledOnce();
  
  vi.useRealTimers();
});

test('should handle setInterval', () => {
  vi.useFakeTimers();
  
  const callback = vi.fn();
  const intervalId = setInterval(callback, 500);
  
  expect(callback).not.toHaveBeenCalled();
  
  vi.advanceTimersByTime(1500);
  
  expect(callback).toHaveBeenCalledTimes(3);
  
  clearInterval(intervalId);
  vi.useRealTimers();
});
```

## API Server Mocking (MSW)

```javascript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';


const server = setupServer(
  http.get('/api/expedientes', () => {
    return HttpResponse.json([
      { id: 1, numero: 'EXP-001' }
    ]);
  }),
  
  http.post('/api/expedientes', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: 2, ...body },
      { status: 201 }
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('should fetch expedientes', async () => {
  render(<ExpedientesList />);
  
  await waitFor(() => {
    expect(screen.getByText('EXP-001')).toBeInTheDocument();
  });
});
```
