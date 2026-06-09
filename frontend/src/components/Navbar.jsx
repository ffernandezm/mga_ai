import { NavLink } from "react-router-dom";

function Navbar({ isCollapsed, onToggle }) {
    return (
        <aside className={`app-sidebar ${isCollapsed ? "collapsed" : ""}`}>
            <div className="app-sidebar-top">
                <div className="app-sidebar-header" aria-hidden={isCollapsed}>
                    <p className="app-brand">MGA IA</p>
                    <span className="app-brand-sub">Asistente de formulacion</span>
                </div>

                <button
                    type="button"
                    className="app-sidebar-toggle"
                    onClick={onToggle}
                    aria-expanded={!isCollapsed}
                    aria-label={isCollapsed ? "Mostrar barra lateral" : "Ocultar barra lateral"}
                    title={isCollapsed ? "Mostrar barra lateral" : "Ocultar barra lateral"}
                >
                    <span aria-hidden="true">{isCollapsed ? "»" : "«"}</span>
                </button>
            </div>

            <nav
                className="app-sidebar-nav"
                aria-label="Navegacion principal"
                aria-hidden={isCollapsed}
            >
                <NavLink
                    to="/"
                    end
                    className={({ isActive }) =>
                        `app-sidebar-link ${isActive ? "active" : ""}`
                    }
                >
                    Home
                </NavLink>
                <NavLink
                    to="/projects"
                    className={({ isActive }) =>
                        `app-sidebar-link ${isActive ? "active" : ""}`
                    }
                >
                    Proyectos
                </NavLink>
            </nav>
        </aside>
    );
}

export default Navbar;