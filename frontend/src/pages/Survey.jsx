import { useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { openSurveyQuestions, surveyQuestions } from "../data/surveyQuestions";
import "./Survey.css";

import SurveyQuestionCard from "../components/survey/SurveyQuestionCard";
import SurveyProgress from "../components/survey/SurveyProgress";

function Survey() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [responses, setResponses] = useState({});
    const [openResponses, setOpenResponses] = useState({});
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

    const handleOpenResponseChange = (id, value) => {
        setOpenResponses((previous) => ({
            ...previous,
            [id]: value,
        }));
    };

    const questionsByDimension = useMemo(() => {
        return surveyQuestions.reduce((groups, question) => {
            const group = groups.find(({ dimension }) => dimension === question.dimension);
            if (group) {
                group.questions.push(question);
            } else {
                groups.push({ dimension: question.dimension, questions: [question] });
            }
            return groups;
        }, []);
    }, []);

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

        const dimensions = Object.fromEntries(
            questionsByDimension.map(({ dimension, questions }) => [
                dimension,
                Number(getAvg(questions.map(({ id }) => id)).toFixed(2)),
            ])
        );
        const globalIndex = Math.round(getAvg(surveyQuestions.map(({ id }) => id)) * 10);

        let rating = "Por mejorar";
        if (globalIndex >= 90) rating = "Excelente";
        else if (globalIndex >= 75) rating = "Muy bueno";
        else if (globalIndex >= 60) rating = "Bueno";
        else if (globalIndex >= 45) rating = "Regular";

        return {
            answeredCount,
            totalQuestions: surveyQuestions.length,
            completion,
            dimensions,
            globalIndex,
            rating,
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
                survey_json: { ...responses, ...openResponses },
                score_summary: summary,
                comment: "",
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
                survey_json: { ...responses, ...openResponses },
                score_summary: calculateScoreSummary(),
                comment: "",
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
                            <span>Preguntas respondidas</span>
                            <strong>{scoreSummary.answeredCount}/{scoreSummary.totalQuestions}</strong>
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
                {questionsByDimension.map(({ dimension, questions }) => (
                    <section className="survey-dimension" key={dimension}>
                        <h2 className="survey-dimension-title">{dimension}</h2>
                        <div className="survey-question-list">
                            {questions.map((question) => (
                                <SurveyQuestionCard
                                    key={question.id}
                                    question={question}
                                    value={responses[question.id]}
                                    onChange={(value) => handleChange(question.id, value)}
                                />
                            ))}
                        </div>
                    </section>
                ))}

                <section className="survey-comment-card">
                    <h2 className="survey-dimension-title">Preguntas abiertas</h2>
                    {openSurveyQuestions.map((question) => (
                        <div className="survey-open-question" key={question.id}>
                            <label htmlFor={`survey-question-${question.id}`}>{question.text}</label>
                            <textarea
                                id={`survey-question-${question.id}`}
                                rows={4}
                                value={openResponses[question.id] || ""}
                                onChange={(event) => handleOpenResponseChange(question.id, event.target.value)}
                            />
                        </div>
                    ))}
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
