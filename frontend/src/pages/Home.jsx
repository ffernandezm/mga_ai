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
          Prototipo de apoyo inteligente para la formulación de proyectos de
          inversión pública
        </h1>

        <p className="home-lead">
          Esta herramienta está basada en <strong>MGA Web</strong> del
          <strong> Departamento Nacional de Planeación de Colombia</strong> y
          fue concebida como un prototipo para fortalecer el proceso de registro
          y análisis de información de proyectos.
        </p>

        <div className="home-feature-grid">
          <div className="home-feature-item">
            <h2>Base metodologica oficial</h2>
            <p>
              Conserva la estructura y el enfoque de MGA Web para mantener
              consistencia técnica durante la formulación.
            </p>
          </div>

          <div className="home-feature-item">
            <h2>Asistente LLM para chatbot</h2>
            <p>
              Integra un modelo de lenguaje para brindar respuestas
              contextualizadas y asistencia oportuna.
            </p>
          </div>

          <div className="home-feature-item">
            <h2>Apoyo durante el registro</h2>
            <p>
              El chatbot orienta la captura de datos y ayuda a mejorar claridad,
              calidad y coherencia de la información diligenciada.
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