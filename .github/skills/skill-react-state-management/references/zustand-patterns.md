# Zustand Store Patterns

```javascript
// Store composition
const useAuthStore = create((set) => ({
  user: null,
  login: async (creds) => {
    const token = await keycloak.login(creds);
    set({ user: token });
  }
}));

// Use in component
function Dashboard() {
  const user = useAuthStore(state => state.user);
  const login = useAuthStore(state => state.login);
  
  return user ? <h1>{user.name}</h1> : <button onClick={login}>Login</button>;
}

// Testing
test('login updates user', () => {
  const { result } = renderHook(() => useAuthStore());
  act(() => result.current.login({username: 'test'}));
  expect(result.current.user).toBeDefined();
});
```
