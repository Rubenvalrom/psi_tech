export function Login() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-blue-50">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Olympus Smart Gov
        </h1>
        <p className="text-center text-gray-600 mb-6">
          Login with Keycloak (Fase 2)
        </p>
        <button
          disabled
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Sign In with Keycloak
        </button>
        <p className="text-xs text-gray-400 mt-4 text-center">
          Authentication integration coming in Phase 2
        </p>
      </div>
    </div>
  );
}
