import { NavBar } from "./NavBar";

export function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="container mx-auto py-8">
        {children}
      </main>
    </div>
  );
}
