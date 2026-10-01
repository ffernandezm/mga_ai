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
    const [error, setError] = useState(null);

    const handleChange = (id, value) => {
        setResponses((previous) => ({
            ...previous,
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
            const existingGroup = groups.find(
                ({ dimension }) => dimension === question.dimension
            );

            if (existingGroup) {
                existingGroup.questions.push(question);
            } else {
                groups.push({
                    dimension: question.dimension,
                    questions: [question],
                });
            }

            return groups;
        }, []);
    }, []);

    const answeredCount = useMemo(() => {
        return surveyQuestions.filter((question) => {
            const value = Number(responses[question.id]);
            return Number.isFinite(value) && value >= 1 && value <= 10;
        }).length;
    }, [responses]);

    const completion = useMemo(() => {
        if (!surveyQuestions.length) return 0;
        return Math.round((answeredCount / surveyQuestions.length) * 100);
    }, [answeredCount]);

    const calculateScoreSummary = () => {
        const getAverage = (ids) => {
            const values = ids
                .map((id) => Number(responses[id]))
                .filter(
                    (value) =>
                        Number.isFinite(value) && value >= 1 && value <= 10
                );

            if (!values.length) return null;

            const average =
                values.reduce((accumulator, value) => accumulator + value, 0) /
                values.length;

            return Number(average.toFixed(2));
        };

        const dimensions = Object.fromEntries(
            questionsByDimension.map(({ dimension, questions }) => [
                dimension,
                getAverage(questions.map(({ id }) => id)),
            ])
        );

        return {
            answeredCount,
            totalQuestions: surveyQuestions.length,
            completion,
            scale: {
                min: 1,
                max: 10,
                min_label: "Totalmente en desacuerdo",
                max_label: "Totalmente de acuerdo",
            },
            dimensions,
        };
    };

    const handleSubmit = async () => {
        if (answeredCount < surveyQuestions.length) {
            setError(
                "Completa todas las preguntas de valoración antes de enviar la encuesta."
            );
            return;
        }

        if (!projectId) {
            setError(
                "No se pudo identificar el proyecto asociado a la encuesta."
            );
            return;
        }

        setError(null);
        setSubmitting(true);

        try {
            const summary = calculateScoreSummary();

            const payload = {
                project_id: projectId,
                is_completed: true,
                survey_json: {
                    ...responses,
                    ...openResponses,
                },
                score_summary: summary,
                comment: "",
            };

            await api.post(`/survey/${projectId}`, payload);
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

    const goToFormulation = () => navigate(`/edit-project/${projectId}`);
    const goToProjectsList = () => navigate("/projects");

    if (submitted) {
        return (
            <div className="survey-thankyou">
                <div className="survey-thankyou-icon" aria-hidden>
                    ✓
                </div>

                <p className="survey-thankyou-badge">Encuesta recibida</p>

                <h2 className="mb-2">Gracias por tu participación</h2>

                <p className="survey-thankyou-copy">
                    Tus respuestas fueron registradas correctamente y serán
                    utilizadas exclusivamente para la evaluación académica de
                    MGA_IA.
                </p>

                <p className="survey-thankyou-copy">
                    No se muestra una calificación individual porque esta encuesta
                    evalúa el sistema y no el desempeño del participante.
                </p>

                <div className="mt-4 d-flex gap-3 flex-wrap">
                    <button
                        className="btn btn-outline-primary"
                        onClick={goToFormulation}
                    >
                        🔙 Volver a la Formulación
                    </button>

                    <button
                        className="btn btn-outline-secondary"
                        onClick={goToProjectsList}
                    >
                        Volver a Proyectos
                    </button>
                </div>
            </div>
        );
    }

    return (
        <section className="survey-page">
            <div
                className="survey-page-bg survey-page-bg-left"
                aria-hidden
            />
            <div
                className="survey-page-bg survey-page-bg-right"
                aria-hidden
            />

            <div className="survey-shell">
                <header className="survey-hero">
                    <p className="survey-overline">
                        Evaluación de experiencia
                    </p>

                    <h1>Encuesta de validación del sistema</h1>

                    <p>
                        Indica tu nivel de acuerdo con cada afirmación en una
                        escala de 1 a 10, donde <strong>1</strong> significa
                        <strong> “Totalmente en desacuerdo”</strong> y
                        <strong> 10</strong> significa
                        <strong> “Totalmente de acuerdo”</strong>.
                    </p>

                    <p>
                        Responde según tu experiencia durante la prueba de MGA_IA.
                        No existen respuestas correctas o incorrectas: estamos
                        evaluando el sistema, no tu desempeño profesional.
                    </p>
                </header>

                <div className="alert alert-light border mb-4" role="note">
                    <strong>Escala de respuesta:</strong>{" "}
                    1 = Totalmente en desacuerdo · 10 = Totalmente de acuerdo.
                    Las preguntas de valoración son obligatorias; las preguntas
                    abiertas son opcionales.
                </div>

                <SurveyProgress
                    completion={completion}
                    answered={answeredCount}
                    total={surveyQuestions.length}
                />

                {questionsByDimension.map(({ dimension, questions }) => (
                    <section className="survey-dimension" key={dimension}>
                        <h2 className="survey-dimension-title">
                            {dimension}
                        </h2>

                        <div className="survey-question-list">
                            {questions.map((question) => (
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
                    </section>
                ))}

                <section className="survey-comment-card">
                    <h2 className="survey-dimension-title">
                        Preguntas abiertas
                    </h2>

                    <p>
                        Estas preguntas son opcionales y permiten ampliar tu
                        valoración.
                    </p>

                    {openSurveyQuestions.map((question) => (
                        <div
                            className="survey-open-question"
                            key={question.id}
                        >
                            <label
                                htmlFor={`survey-question-${question.id}`}
                            >
                                {question.text}
                            </label>

                            <textarea
                                id={`survey-question-${question.id}`}
                                rows={4}
                                value={openResponses[question.id] || ""}
                                onChange={(event) =>
                                    handleOpenResponseChange(
                                        question.id,
                                        event.target.value
                                    )
                                }
                                placeholder="Respuesta opcional..."
                            />
                        </div>
                    ))}
                </section>

                {error && (
                    <div
                        className="alert alert-danger text-center survey-alert"
                        role="alert"
                    >
                        {error}
                    </div>
                )}

                <div className="survey-actions">
                    <button
                        className="btn btn-primary px-5 py-2"
                        onClick={handleSubmit}
                        disabled={
                            answeredCount < surveyQuestions.length || submitting
                        }
                    >
                        {submitting ? "Enviando..." : "Enviar respuestas"}
                    </button>
                </div>

                <div className="survey-nav-actions">
                    <button
                        className="btn btn-outline-primary"
                        onClick={goToFormulation}
                    >
                        🔙 Volver a la Formulación
                    </button>

                    <button
                        className="btn btn-outline-secondary"
                        onClick={goToProjectsList}
                    >
                        Volver a Proyectos
                    </button>
                </div>
            </div>
        </section>
    );
}

export default Survey;
