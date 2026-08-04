export default function SurveyProgress({
    completion,
    answered,
    total,
}) {
    return (
        <section className="survey-status-card">
            <div className="survey-status-top">
                <strong>Progreso</strong>
                <span>{answered} / {total}</span>
            </div>

            <div className="survey-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={completion}>
                <div className="survey-progress-fill" style={{ width: `${completion}%` }} />
            </div>
            <small>{completion}% completado</small>
        </section>
    );
}