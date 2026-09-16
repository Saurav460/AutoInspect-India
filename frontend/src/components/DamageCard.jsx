function DamageCard({
  damage,
  index,
  isNew = false,
}) {
  const confidence =
    Number(
      damage.confidence || 0
    ) * 100;

  const confidenceText =
    confidence.toFixed(1);

  const severity =
    damage.severity?.toLowerCase() ||
    "moderate";

  return (
    <div
      className={
        `damage-card ${
          isNew ? "new-damage" : ""
        }`
      }
    >

      <div className="damage-card-header">

        <div className="damage-title-area">

          <span className="damage-number">
            #
            {String(
              index + 1
            ).padStart(2, "0")}
          </span>

          <h3>
            {damage.type}
          </h3>

        </div>

        <span
          className={
            `severity ${severity}`
          }
        >
          {damage.severity}
        </span>

      </div>


      <div className="damage-details">

        <div className="detail-item">

          <span>
            Confidence
          </span>

          <strong>
            {confidenceText}%
          </strong>

        </div>


        <div className="detail-item">

          <span>
            Location
          </span>

          <strong>
            {damage.location ||
              "Unknown"}
          </strong>

        </div>


        <div className="detail-item">

          <span>
            Area
          </span>

          <strong>
            {damage.relative_area ??
              0}
            %
          </strong>

        </div>


        {damage.iou !==
          undefined && (

          <div className="detail-item">

            <span>
              IoU Match
            </span>

            <strong>
              {damage.iou}
            </strong>

          </div>

        )}

      </div>


      <div className="confidence-wrapper">

        <div className="confidence-label">

          <span>
            AI Confidence
          </span>

          <span>
            {confidenceText}%
          </span>

        </div>

        <div className="confidence-bar">

          <div
            className="confidence-fill"
            style={{
              width:
                `${Math.min(
                  confidence,
                  100
                )}%`,
            }}
          />

        </div>

      </div>


      {isNew && (

        <div className="new-damage-label">
          Potential New Damage
        </div>

      )}

    </div>
  );
}

export default DamageCard;