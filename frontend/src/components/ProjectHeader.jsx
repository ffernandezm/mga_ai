import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function ProjectHeader({ id, project, loading, error }) {
    const navigate = useNavigate();
    const storageKey = `projectHeaderCollapsed_${id}`;

    // Leer estado inicial desde localStorage
    const [collapsed, setCollapsed] = useState(() => {
        const saved = localStorage.getItem(storageKey);
        return saved === "true";
    });

    // Persistir cambios
    useEffect(() => {
        localStorage.setItem(storageKey, collapsed);
    }, [collapsed, storageKey]);

    const toggleCollapse = () => setCollapsed(prev => !prev);

    const headerStyle = {
        cursor: "pointer",
        userSelect: "none",
        backgroundColor: "#375572", // Azul solicitado
        color: "white",
        borderBottom: "1px solid rgba(255,255,255,0.1)"
    };

    return (
        <div className="card shadow-sm border-0 mb-4">
            {/* Header clickeable con fondo azul personalizado */}
            <div
                className="card-header d-flex justify-content-between align-items-center"
                style={headerStyle}
                onClick={toggleCollapse}
            >
                <h5 className="mb-0 fw-semibold">
                    <i className="bi bi-info-circle-fill me-2"></i>
                    Información del Proyecto #{id}
                </h5>
                <div className="d-flex align-items-center gap-3">
                    {/* Botones de acción - evitamos que el clic propague al toggle */}
                    <div onClick={(e) => e.stopPropagation()}>
                        <button
                            className="btn btn-sm btn-outline-light me-2"
                            style={{ borderWidth: "1.5px" }}
                            onClick={() => navigate(`/projects/${id}/edit`)}
                        >
                            ✏️ Editar Proyecto
                        </button>
                        <button
                            className="btn btn-sm btn-success"
                            style={{ backgroundColor: "#28a745", borderColor: "#28a745" }}
                            onClick={() => navigate(`/projects/${id}/survey`)}
                        >
                            📝 Ir a la encuesta
                        </button>
                    </div>
                    <span style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
                        {collapsed ? "▼" : "▲"}
                    </span>
                </div>
            </div>

            {/* Contenido colapsable */}
            {!collapsed && (
                <div className="card-body" style={{ backgroundColor: "#f8f9fc" }}>
                    {loading && (
                        <div className="alert alert-info mb-0 p-2" role="alert">
                            <i className="bi bi-arrow-repeat me-1"></i>
                            Cargando proyecto...
                        </div>
                    )}

                    {error && (
                        <div className="alert alert-danger mb-0 p-2" role="alert">
                            <i className="bi bi-exclamation-triangle-fill me-1"></i>
                            Error: {error}
                        </div>
                    )}

                    {project && (
                        <div className="text-secondary">
                            <div className="mb-2 pb-2 border-bottom">
                                <strong className="text-primary">Nombre del proyecto:</strong>
                                <p className="mb-0 mt-1">{project.name}</p>
                            </div>
                            <div>
                                <strong className="text-primary">Descripción general:</strong>
                                <p className="mb-0 mt-1 text-muted">{project.description || "Sin descripción"}</p>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default ProjectHeader;