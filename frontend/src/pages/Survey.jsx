import { useState } from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { surveyQuestions } from "../data/surveyQuestions";

function Survey() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [responses, setResponses] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (id, value) => {
        setResponses({ ...responses, [id]: value });
    };

    const handleSubmit = async () => {
        try {
            const payload = { survey_json: responses };
            await api.post(`/survey/${projectId}`, payload);
            setSubmitted(true);
        } catch (err) {
            console.error("Error al enviar encuesta:", err);
            setError("Ocurrió un error al enviar la encuesta. Intenta nuevamente.");
        }
    };

    const handleExportJSON = () => {
        const dataStr = JSON.stringify({ project_id: projectId, survey_json: responses }, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = `encuesta_project_${projectId}.json`;
        link.click();

        URL.revokeObjectURL(url);
    };

    // 🟢 Botones de navegación
    const goToFormulation = () => navigate(`/edit-project/${projectId}`);
    const goToProjectsList = () => navigate(`/projects`);

    if (submitted) {
        return (
            <motion.div
                className="d-flex flex-column align-items-center justify-content-center vh-100 text-center p-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <div className="text-success mb-3" style={{ fontSize: "3rem" }}>✔</div>
                <h2 className="mb-2">¡Gracias por tu participación!</h2>
                <p>Tus respuestas ayudarán a mejorar la experiencia del sistema y del asistente LLM.</p>

                <div className="mt-4 d-flex gap-3">
                    <button className="btn btn-outline-primary" onClick={goToFormulation}>
                        🔙 Volver a la Formulación
                    </button>
                    <button className="btn btn-outline-secondary" onClick={goToProjectsList}>
                        🏠 Volver a Proyectos
                    </button>
                </div>
            </motion.div>
        );
    }

    return (
        <div className="container py-5">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="text-center mb-4">Encuesta de Validación del Sistema</h1>
                <p className="text-center text-muted mb-5">
                    Califique cada aspecto del 1 al 10, donde 1 es “Muy bajo” y 10 es “Excelente”.
                </p>

                {surveyQuestions.map((q) => (
                    <div key={q.id} className="card mb-4 shadow-sm">
                        <div className="card-body">
                            <p className="fw-medium">{q.text}</p>
                            <div className="d-flex align-items-center justify-content-between mt-3">
                                <span>1</span>
                                <input
                                    type="range"
                                    className="form-range mx-3"
                                    min="1"
                                    max="10"
                                    step="1"
                                    defaultValue="5"
                                    onChange={(e) => handleChange(q.id, e.target.value)}
                                    style={{ flex: 1 }}
                                />
                                <span>10</span>
                            </div>
                            <p className="text-end text-muted small mt-1">
                                Puntuación: {responses[q.id] ?? "-"}
                            </p>
                        </div>
                    </div>
                ))}

                {error && (
                    <div className="alert alert-danger text-center">{error}</div>
                )}

                <div className="text-center mt-4 d-flex justify-content-center gap-3">
                    <button
                        className="btn btn-primary px-5 py-2"
                        onClick={handleSubmit}
                        disabled={Object.keys(responses).length < surveyQuestions.length}
                    >
                        Enviar respuestas
                    </button>

                    <button
                        className="btn btn-outline-secondary px-4 py-2"
                        onClick={handleExportJSON}
                    >
                        Ver JSON
                    </button>
                </div>

                {/* Botones fijos abajo */}
                <div className="text-center mt-5 d-flex justify-content-center gap-3">
                    <button className="btn btn-outline-primary" onClick={goToFormulation}>
                        🔙 Volver a la Formulación
                    </button>
                    <button className="btn btn-outline-secondary" onClick={goToProjectsList}>
                        🏠 Volver a Proyectos
                    </button>
                </div>
            </motion.div>
        </div>
    );
}

export default Survey;
