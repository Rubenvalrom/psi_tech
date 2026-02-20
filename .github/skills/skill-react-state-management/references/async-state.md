# Async State Management with Zustand

## Basic Async Store

```javascript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { devtools } from 'zustand/middleware';

export const useExpedientesStore = create(
  devtools(
    immer((set) => ({
      expedientes: [],
      loading: false,
      error: null,

      // Async actions
      fetchExpedientes: async () => {
        set((state) => {
          state.loading = true;
          state.error = null;
        });

        try {
          const response = await fetch('/api/expedientes');
          const data = await response.json();
          set((state) => {
            state.expedientes = data;
            state.loading = false;
          });
        } catch (error) {
          set((state) => {
            state.error = error.message;
            state.loading = false;
          });
        }
      },

      createExpediente: async (expediente) => {
        try {
          const response = await fetch('/api/expedientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expediente),
          });
          const newExpediente = await response.json();
          set((state) => {
            state.expedientes.push(newExpediente);
          });
          return newExpediente;
        } catch (error) {
          set((state) => {
            state.error = error.message;
          });
          throw error;
        }
      },
    })),
    { name: 'expedientes-store' }
  )
);
```

## Store with Loading States

```javascript
const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  loginLoading: false,
  loginError: null,

  login: async (username, password) => {
    set({ loginLoading: true, loginError: null });
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      const { token, user } = await response.json();
      localStorage.setItem('token', token);
      set({
        user,
        isAuthenticated: true,
        loginLoading: false,
      });
    } catch (error) {
      set({
        loginError: error.message,
        loginLoading: false,
      });
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({
      user: null,
      isAuthenticated: false,
    });
  },
}));
```

## Middleware for Request Management

```javascript
const withRequestStatus = (config) =>
  (set, get) => {
    const requests = new Map();

    return {
      ...config(set, get),

      setRequestLoading: (requestId, loading) => {
        const current = requests.get(requestId) || {};
        requests.set(requestId, { ...current, loading });
        set((state) => ({
          requests: Object.fromEntries(requests),
        }));
      },

      setRequestError: (requestId, error) => {
        const current = requests.get(requestId) || {};
        requests.set(requestId, { ...current, error });
        set((state) => ({
          requests: Object.fromEntries(requests),
        }));
      },
    };
  };

export const useStore = create(
  withRequestStatus((set) => ({
    requests: {},
    data: [],
  }))
);
```

## Persisting Async State

```javascript
import { persist } from 'zustand/middleware';

export const useUserPreferences = create(
  persist(
    (set) => ({
      theme: 'light',
      language: 'es',
      notifications: true,

      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
      toggleNotifications: () =>
        set((state) => ({
          notifications: !state.notifications,
        })),
    }),
    {
      name: 'user-preferences',
      storage: localStorage, // or sessionStorage
      version: 1,
      migrate: (persistedState, version) => {
        // Handle migrations
        if (version === 0) {
          return {
            ...persistedState,
            language: persistedState.locale || 'es',
          };
        }
        return persistedState;
      },
    }
  )
);
```

## Combining Multiple Stores

```javascript
export const useAppState = create((set) => {
  const unsubscribeExpedientes = useExpedientesStore.subscribe(
    (state) => state.expedientes,
    (expedientes) => {
      set((state) => ({
        totalExpedientes: expedientes.length,
      }));
    }
  );

  const unsubscribeAuth = useAuthStore.subscribe(
    (state) => state.isAuthenticated,
    (isAuthenticated) => {
      set((state) => ({
        isLoggedIn: isAuthenticated,
      }));
    }
  );

  return {
    totalExpedientes: 0,
    isLoggedIn: false,
    cleanup: () => {
      unsubscribeExpedientes();
      unsubscribeAuth();
    },
  };
});
```

## Using Async Store in Components

```javascript
import { useShallow } from 'zustand/react';

function ExpedientesList() {
  const { expedientes, loading, error, fetchExpedientes } = useShallow(
    useExpedientesStore
  );

  useEffect(() => {
    fetchExpedientes();
  }, [fetchExpedientes]);

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {expedientes.map((exp) => (
        <li key={exp.id}>{exp.numero} - {exp.estado}</li>
      ))}
    </ul>
  );
}
```
