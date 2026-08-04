import ScoreSelector from "./ScoreSelector";

export default function SurveyQuestionCard({
    question,
    value,
    onChange,
}) {
    return (
        <article className={`survey-question-card ${value ? "answered" : ""}`}>
            <div className="survey-question-header">
                <div>
                    <span className="question-number">Pregunta {question.id}</span>
                    <h5>{question.text}</h5>
                </div>

                {value && <div className="answered-badge">✔ Respondida</div>}
            </div>

            <ScoreSelector value={value} onChange={onChange} />
            <div className="survey-label-row">
                <small>Muy bajo</small>
                <small>Excelente</small>
            </div>
        </article>

    );

}