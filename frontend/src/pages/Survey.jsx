import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { surveyQuestions } from "../data/surveyQuestions";
import "./Survey.css";

function Survey() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [responses, setResponses] = useState({});
    const [comment, setComment] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [scoreSummary, setScoreSummary] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (id, value) => {
        setResponses((prev) => ({ ...prev, [id]: Number(value) }));
    };

    const answeredCount = useMemo(() => Object.keys(responses).length, [responses]);
    const completion = useMemo(
        () => Math.round((answeredCount / surveyQuestions.length) * 100),
        [answeredCount]
    );

    const scorePreview = useMemo(() => {
        const values = Object.values(responses);
        if (!values.length) return null;

        const avg = values.reduce((acc, n) => acc + Number(n), 0) / values.length;
        const normalized = Math.round(avg * 10);

        if (normalized >= 90) return { label: "Excelente", tone: "excellent" };
        if (normalized >= 75) return { label: "Muy bueno", tone: "great" };
        if (normalized >= 60) return { label: "Bueno", tone: "good" };
        if (normalized >= 45) return { label: "Regular", tone: "regular" };
        return { label: "Por mejorar", tone: "improve" };
    }, [responses]);

    const calculateScoreSummary = () => {
        const getAvg = (ids) => {
            const values = ids
                .map((id) => Number(responses[id]))
                .filter((value) => Number.isFinite(value) && value >= 1 && value <= 10);
            if (!values.length) return 0;
            return values.reduce((acc, n) => acc + n, 0) / values.length;
        };

        const dimensions = {
            usability: getAvg([1, 2, 3, 4]),
            assistant: getAvg([5, 6, 7, 8, 9, 12]),
            satisfaction: getAvg([10, 11]),
        };

        const weightedScore =
            dimensions.usability * 0.35 + dimensions.assistant * 0.45 + dimensions.satisfaction * 0.2;

        const globalIndex = Math.round(weightedScore * 10);
        const recommendation = Number(responses[11]);

        let npsGroup = "detractor";
        if (recommendation >= 9) npsGroup = "promoter";
        if (recommendation >= 7 && recommendation <= 8) npsGroup = "passive";

        const npsScore = npsGroup === "promoter" ? 100 : npsGroup === "passive" ? 0 : -100;

        let rating = "Por mejorar";
        if (globalIndex >= 90) rating = "Excelente";
        else if (globalIndex >= 75) rating = "Muy bueno";
        else if (globalIndex >= 60) rating = "Bueno";
        else if (globalIndex >= 45) rating = "Regular";

        return {
            answeredCount,
            totalQuestions: surveyQuestions.length,
            completion,
            dimensions: {
                usability: Number(dimensions.usability.toFixed(2)),
                assistant: Number(dimensions.assistant.toFixed(2)),
                satisfaction: Number(dimensions.satisfaction.toFixed(2)),
            },
            globalIndex,
            rating,
            nps: {
                question11: recommendation,
                group: npsGroup,
                score: npsScore,
            },
        };
    };

    const handleSubmit = async () => {
        if (answeredCount < surveyQuestions.length) return;

        setError(null);
        setSubmitting(true);

        try {
            const summary = calculateScoreSummary();
            const payload = {
                survey_json: responses,
                score_summary: summary,
                comment: comment.trim(),
            };
            await api.post(`/survey/${projectId}`, payload);
            setScoreSummary(summary);
            setSubmitted(true);
        } catch (err) {
            console.error("Error al enviar encuesta:", err);
            setError("Ocurrió un error al enviar la encuesta. Intenta nuevamente.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleExportJSON = () => {
        const dataStr = JSON.stringify(
            {
                project_id: projectId,
                survey_json: responses,
                score_summary: calculateScoreSummary(),
                comment: comment.trim(),
            },
            null,
            2
        );
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
                className="survey-thankyou"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, y: [10, 0] }}
            >
                <div className="survey-thankyou-icon" aria-hidden>
                    ✓
                </div>
                <p className="survey-thankyou-badge">Encuesta recibida</p>
                <h2 className="mb-2">Gracias por tu participación</h2>
                <p className="survey-thankyou-copy">
                    Tus respuestas ya fueron registradas y se usarán para mejorar la experiencia del sistema y del asistente.
                </p>

                {scoreSummary && (
                    <div className="survey-thankyou-score-grid">
                        <article className="survey-score-card">
                            <span>Índice global</span>
                            <strong>{scoreSummary.globalIndex}/100</strong>
                        </article>
                        <article className="survey-score-card">
                            <span>Resultado</span>
                            <strong>{scoreSummary.rating}</strong>
                        </article>
                        <article className="survey-score-card">
                            <span>NPS</span>
                            <strong>{scoreSummary.nps.score}</strong>
                        </article>
                    </div>
                )}

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
        <section className="survey-page">
            <div className="survey-page-bg survey-page-bg-left" aria-hidden />
            <div className="survey-page-bg survey-page-bg-right" aria-hidden />
            <motion.div
                className="survey-shell"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <header className="survey-hero">
                    <p className="survey-overline">Evaluacion de experiencia</p>
                    <h1>Encuesta de validacion del sistema</h1>
                    <p>
                        Califica cada aspecto del 1 al 10, donde 1 es muy bajo y 10 es excelente.
                        Solo toma unos minutos.
                    </p>
                </header>

                <section className="survey-status-card">
                    <div className="survey-status-top">
                        <strong>Progreso de respuesta</strong>
                        <span>
                            {answeredCount}/{surveyQuestions.length} respondidas
                        </span>
                    </div>
                    <div className="survey-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={completion}>
                        <div className="survey-progress-fill" style={{ width: `${completion}%` }} />
                    </div>
                    <div className="survey-status-bottom">
                        <span>{completion}% completado</span>
                        {scorePreview && (
                            <span className={`survey-pill survey-pill-${scorePreview.tone}`}>
                                Tendencia actual: {scorePreview.label}
                            </span>
                        )}
                    </div>
                </section>

                <div className="survey-question-list">
                    {surveyQuestions.map((q, index) => (
                        <motion.article
                            key={q.id}
                            className="survey-question-card"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.03 }}
                        >
                            <div className="survey-question-head">
                                <span>Pregunta {q.id}</span>
                                <strong>{responses[q.id] ?? "-"}</strong>
                            </div>
                            <p>{q.text}</p>
                            <div className="survey-range-wrap">
                                <span>1</span>
                                <input
                                    type="range"
                                    className="form-range"
                                    min="1"
                                    max="10"
                                    step="1"
                                    value={responses[q.id] ?? 5}
                                    onChange={(e) => handleChange(q.id, e.target.value)}
                                />
                                <span>10</span>
                            </div>
                            <div className="survey-range-labels">
                                <small>Muy bajo</small>
                                <small>Excelente</small>
                            </div>
                        </motion.article>
                    ))}
                </div>

                <section className="survey-comment-card">
                    <label htmlFor="survey-comment">Comentario adicional (opcional)</label>
                    <textarea
                        id="survey-comment"
                        rows={4}
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Cuéntanos recomendaciones puntuales para mejorar la formulación, navegación o respuestas del asistente."
                    />
                </section>

                {error && (
                    <div className="alert alert-danger text-center survey-alert">{error}</div>
                )}

                <div className="survey-actions">
                    <button
                        className="btn btn-primary px-5 py-2"
                        onClick={handleSubmit}
                        disabled={answeredCount < surveyQuestions.length || submitting}
                    >
                        {submitting ? "Enviando..." : "Enviar respuestas"}
                    </button>

                    <button
                        className="btn btn-outline-secondary px-4 py-2"
                        onClick={handleExportJSON}
                    >
                        Ver JSON
                    </button>
                </div>

                {/* Botones fijos abajo */}
                <div className="survey-nav-actions">
                    <button className="btn btn-outline-primary" onClick={goToFormulation}>
                        🔙 Volver a la Formulación
                    </button>
                    <button className="btn btn-outline-secondary" onClick={goToProjectsList}>
                        🏠 Volver a Proyectos
                    </button>
                </div>
            </motion.div>
        </section>
    );
}

export default Survey;
