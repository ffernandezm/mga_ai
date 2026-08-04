import { useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { surveyQuestions } from "../data/surveyQuestions";
import "./Survey.css";

import SurveyQuestionCard from "../components/survey/SurveyQuestionCard";
import SurveyProgress from "../components/survey/SurveyProgress";

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
        setResponses(prev => ({
            ...prev,
            [id]: Number(value),
        }));
    };

    const answeredCount = useMemo(() => Object.keys(responses).length, [responses]);
    const completion = useMemo(
        () => Math.round((answeredCount / surveyQuestions.length) * 100),
        [answeredCount]
    );



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
        if (answeredCount < surveyQuestions.length) {
            setError("Completa todas las preguntas antes de enviar.");
            return;
        }

        if (!projectId) {
            setError("No se pudo identificar el proyecto asociado a la encuesta.");
            return;
        }

        setError(null);
        setSubmitting(true);

        try {
            const summary = calculateScoreSummary();
            const payload = {
                project_id: projectId,
                is_completed: true,
                survey_json: responses,
                score_summary: summary,
                comment: comment.trim(),
            };
            await api.post(`/survey/${projectId}`, payload);
            setScoreSummary(summary);
            setSubmitted(true);
        } catch (err) {
            console.error("Error al enviar encuesta:", err);
            const message =
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                err?.message ||
                "Ocurrió un error al enviar la encuesta. Intenta nuevamente.";
            setError(message);
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

    const goToFormulation = () => navigate(`/edit-project/${projectId}`);
    const goToProjectsList = () => navigate(`/projects`);

    if (submitted) {
        return (
            <div className="survey-thankyou">
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
            </div>
        );
    }

    return (
        <section className="survey-page">
            <div className="survey-page-bg survey-page-bg-left" aria-hidden />
            <div className="survey-page-bg survey-page-bg-right" aria-hidden />
            <div className="survey-shell">
                <header className="survey-hero">
                    <p className="survey-overline">Evaluacion de experiencia</p>
                    <h1>Encuesta de validacion del sistema</h1>
                    <p>
                        Califica cada aspecto del 1 al 10, donde 1 es muy bajo y 10 es excelente.
                        Solo toma unos minutos.
                    </p>
                </header>

                <SurveyProgress completion={completion} answered={answeredCount} total={surveyQuestions.length} />
                <div className="survey-question-list">
                    {surveyQuestions.map((question) => (
                        <SurveyQuestionCard
                            key={question.id}
                            question={question}
                            value={responses[question.id]}
                            onChange={(value) =>
                                handleChange(question.id, value)
                            }
                        />
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
            </div>
        </section>
    );
}

export default Survey;
