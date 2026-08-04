const COLORS = {
    1: "danger",
    2: "danger",
    3: "danger",
    4: "warning",
    5: "warning",
    6: "warning",
    7: "primary",
    8: "primary",
    9: "success",
    10: "success",
};

export default function ScoreSelector({
    value,
    onChange,
}) {
    return (
        <div className="survey-score-grid">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((score) => {
                const selected = value === score;

                return (
                    <button
                        key={score}
                        type="button"
                        className={`survey-score-btn ${COLORS[score]} ${selected ? "selected" : ""}`}
                        aria-pressed={selected}
                        onClick={() => onChange(score)}
                    >
                        <span>{score}</span>
                    </button>

                );

            })}
        </div>
    );
}