---
name: skill-react-state-management
description: Implement state management in React using Zustand. Includes store creation, async actions, persistence, devtools integration, and testing patterns. Use when building complex UIs with shared state (expedientes list, filters, auth context) without Redux boilerplate.
---

# React State Management (Zustand)

## Quick Start

```javascript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useExpedientesStore = create(
  devtools(
    persist(
      (set, get) => ({
        expedientes: [],
        loading: false,
        error: null,
        
        // Actions
        fetchExpedientes: async (filters) => {
          set({ loading: true });
          try {
            const res = await fetch(`/api/v1/expedientes?${new URLSearchParams(filters)}`);
            const data = await res.json();
            set({ expedientes: data, error: null });
          } catch (err) {
            set({ error: err.message });
          } finally {
            set({ loading: false });
          }
        },
        
        addExpediente: (exp) => set((state) => ({
          expedientes: [...state.expedientes, exp]
        })),
        
        // Getters
        getById: (id) => get().expedientes.find(e => e.id === id),
      }),
      { name: 'expedientes-store' }
    )
  )
);

export default useExpedientesStore;
```

See [references/zustand-patterns.md](references/zustand-patterns.md) for:
- Store slices for different domains
- Async middleware patterns
- DevTools integration

See [references/async-state.md](references/async-state.md) for:
- Loading/error handling
- Optimistic updates
- Cancelation tokens
