import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-500 to-indigo-600 p-6">
      <div className="bg-white p-10 rounded-2xl shadow-lg text-center max-w-2xl">
        <h1 className="text-4xl font-bold text-blue-600">Bienvenido a MGA con IA Generativa</h1>
        <p className="mt-4 text-lg text-gray-700">
          Optimiza la gestión de proyectos con la Metodología General Ajustable (MGA)
          y el poder de la inteligencia artificial generativa. Simplifica procesos,
          mejora la toma de decisiones y potencia tu productividad.
        </p>
        <div className="mt-6 flex justify-center space-x-4">
          <Link to="/projects">
            <button className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg shadow-md hover:bg-blue-100 transition">
              Empezar
            </button>
          </Link>

        </div>
        <br />
        <br />
      </div>
      
    </div>
  );
}

export default Home;