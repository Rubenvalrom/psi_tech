import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="container">
      <header>
        <h1>🏛️ Olympus Smart Government</h1>
        <p>Inteligencia Artificial para Gobiernos Inteligentes</p>
      </header>
      
      <main>
        <section className="hero">
          <h2>Bienvenido a Olympus</h2>
          <p>Este es el frontend de la plataforma de gobierno inteligente.</p>
          <button onClick={() => setCount(count + 1)}>
            Contador: {count}
          </button>
        </section>
      </main>
      
      <footer>
        <p>&copy; 2026 Olympus Tech. Todos los derechos reservados.</p>
      </footer>
    </div>
  )
}

export default App
