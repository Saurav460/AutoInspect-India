function ResultSummary({
  result,
}) {
  const total =
    result?.detection_count || 0;

  const hasDamage =
    total > 0;

  return (
    <div className="summary-grid">

      <div className="summary-card">

        <div className="summary-icon">
          #
        </div>

        <div>

          <span>
            Total Damage
          </span>

          <strong>
            {total}
          </strong>

        </div>

      </div>


      <div className="summary-card">

        <div className="summary-icon">
          ●
        </div>

        <div>

          <span>
            Status
          </span>

          <strong
            className={
              hasDamage
                ? "status-warning"
                : "status-safe"
            }
          >
            {result?.status ||
              "Completed"}
          </strong>

        </div>

      </div>


      <div className="summary-card">

        <div className="summary-icon">
          AI
        </div>

        <div>

          <span>
            Analysis
          </span>

          <strong>
            Completed
          </strong>

        </div>

      </div>

    </div>
  );
}

export default ResultSummary;