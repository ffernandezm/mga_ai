function ProjectHeader({ id, project, loading, error }) {
    return (
        <div className="card shadow-sm border-0">
            <div className="card-body">
                <h5 className="card-title text-primary mb-3">
                    Información del Proyecto #{id}
                </h5>

                {loading && (
                    <div className="alert alert-info mb-0 p-2" role="alert">
                        Cargando proyecto...
                    </div>
                )}

                {error && (
                    <div className="alert alert-danger mb-0 p-2" role="alert">
                        Error: {error}
                    </div>
                )}

                {project && (
                    <div className="text-secondary">
                        <p className="mb-1"><strong>Nombre:</strong> {project.name}</p>
                        <p className="mb-0"><strong>Descripción:</strong> {project.description}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ProjectHeader;
