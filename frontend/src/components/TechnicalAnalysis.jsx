import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function TechnicalAnalysis({ projectId }) {

    const navigate = useNavigate();

    const [technicalAnalysisId, setTechnicalAnalysisId] = useState(null);
    const [analysis, setAnalysis] = useState("");
    const [loading, setLoading] = useState(false);


    // ==========================
    // FETCH
    // ==========================

    const fetchTechnicalAnalysis = async () => {

        if (!projectId) return;

        try {

            setLoading(true);

            const res = await api.get(
                `/technical_analysis/project/${projectId}`
            );

            const data = res.data;

            setTechnicalAnalysisId(data.id);
            setAnalysis(data.analysis || "");

        } catch (error) {

            // Si no existe aún, no es error crítico
            if (error.response?.status !== 404) {
                console.error("Error cargando análisis técnico:", error);
            }

        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchTechnicalAnalysis();
    }, [projectId]);


    // ==========================
    // SAVE
    // ==========================

    const handleSubmit = async () => {

        if (!analysis.trim()) {
            alert("El análisis no puede estar vacío");
            return;
        }

        const payload = {
            project_id: projectId,
            analysis: analysis
        };

        try {

            if (technicalAnalysisId) {

                await api.put(
                    `/technical_analysis/${technicalAnalysisId}`,
                    { analysis }
                );

            } else {

                const res = await api.post(
                    `/technical_analysis/`,
                    payload
                );

                setTechnicalAnalysisId(res.data.id);
            }

            alert("Análisis técnico guardado");

        } catch (error) {

            console.error(error);
            alert("Error guardando análisis técnico");

        }
    };


    // ==========================
    // DELETE
    // ==========================

    const handleDelete = async () => {

        if (!technicalAnalysisId) return;

        if (!window.confirm("Limpiar análisis técnico?")) return;

        try {

            await api.delete(
                `/technical_analysis/${technicalAnalysisId}`
            );

            setTechnicalAnalysisId(null);
            setAnalysis("");

            alert("Análisis eliminado");

        } catch (error) {

            console.error(error);
            alert("Error eliminando");

        }
    };


    return (

        <div className="container mt-4">

            <h2>Análisis Técnico</h2>

            {loading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <textarea
                        className="form-control mb-4"
                        rows="10"
                        value={analysis}
                        onChange={(e) => setAnalysis(e.target.value)}
                        placeholder="Escribe aquí el análisis técnico del proyecto..."
                    />

                    <div>

                        <button
                            className="btn btn-secondary me-2"
                            onClick={() => navigate("/projects")}
                        >
                            Regresar
                        </button>

                        {technicalAnalysisId && (
                            <button
                                className="btn btn-warning me-2"
                                onClick={handleDelete}
                            >
                                Limpiar
                            </button>
                        )}

                        <button
                            className="btn btn-primary"
                            onClick={handleSubmit}
                        >
                            Guardar
                        </button>

                    </div>
                </>
            )}

        </div>
    );
}

export default TechnicalAnalysis;