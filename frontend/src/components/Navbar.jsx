import { NavLink } from "react-router-dom";

function Navbar() {
    return (
        <aside className="app-sidebar">
            <div className="app-sidebar-header">
                <p className="app-brand">MGA IA</p>
                <span className="app-brand-sub">Asistente de formulacion</span>
            </div>

            <nav className="app-sidebar-nav" aria-label="Navegacion principal">
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