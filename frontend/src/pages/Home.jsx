import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <section className="home-page">
      <div className="home-bg-shape home-bg-shape-top" />
      <div className="home-bg-shape home-bg-shape-bottom" />

      <article className="home-hero-card">
        <p className="home-badge">MGA WEB + IA Generativa</p>
        <h1>
          Prototipo de apoyo inteligente para la formulacion de proyectos de
          inversion publica
        </h1>

        <p className="home-lead">
          Esta herramienta esta basada en <strong>MGA Web</strong> del
          <strong> Departamento Nacional de Planeacion de Colombia</strong> y
          fue concebida como un prototipo para fortalecer el proceso de registro
          y analisis de informacion de proyectos.
        </p>

        <div className="home-feature-grid">
          <div className="home-feature-item">
            <h2>Base metodologica oficial</h2>
            <p>
              Conserva la estructura y el enfoque de MGA Web para mantener
              consistencia tecnica durante la formulacion.
            </p>
          </div>

          <div className="home-feature-item">
            <h2>LLM + RAG para chatbot</h2>
            <p>
              Integra un modelo de lenguaje con recuperacion aumentada para
              brindar respuestas contextualizadas y asistencia oportuna.
            </p>
          </div>

          <div className="home-feature-item">
            <h2>Apoyo durante el registro</h2>
            <p>
              El chatbot orienta la captura de datos y ayuda a mejorar claridad,
              calidad y coherencia de la informacion diligenciada.
            </p>
          </div>
        </div>

        <div className="home-footer-row">
          <p className="home-author">
            Desarrollado por <strong>Nelson Fernando Fernandez Maje</strong>
          </p>

          <Link to="/projects" className="home-primary-action">
            Comenzar ahora
          </Link>
        </div>
      </article>
    </section>
  );
}

export default Home;