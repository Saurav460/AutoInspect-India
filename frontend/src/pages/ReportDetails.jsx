import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  getReport,
  downloadPDF,
  downloadJSON,
} from "../services/api";


function ReportDetails() {

  const {
    inspectionId,
  } = useParams();

  const [
    report,
    setReport,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  /* =====================================================
     LOAD REPORT
  ===================================================== */

  useEffect(() => {

    const loadReport =
      async () => {

        try {

          setLoading(true);
          setError("");

          const data =
            await getReport(
              inspectionId
            );

          setReport(data);

        } catch (err) {

          setError(
            err.message ||
              "Unable to load report."
          );

        } finally {

          setLoading(false);

        }
      };


    loadReport();

  }, [inspectionId]);


  /* =====================================================
     LOADING
  ===================================================== */

  if (loading) {

    return (
      <div className="dashboard-page">

        <div className="loading-panel">

          <div className="loader">
          </div>

          <h3>
            Loading inspection report...
          </h3>

          <p>
            Please wait.
          </p>

        </div>

      </div>
    );
  }


  /* =====================================================
     ERROR
  ===================================================== */

  if (error) {

    return (
      <div className="dashboard-page">

        <div className="error-box">

          <strong>
            Error:
          </strong>{" "}

          {error}

        </div>

        <Link to="/history">

          <button className="
            secondary-button
            back-button
          ">
            ← Back to History
          </button>

        </Link>

      </div>
    );
  }


  if (!report) {
    return null;
  }


  const vehicle =
    report.vehicle || {};

  const result =
    report.result || {};

  const isSingle =
    report.report_type ===
    "Single Image Inspection";


  return (
    <div className="dashboard-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="report-details-header">

        <div>

          <span className="page-tag">
            INSPECTION REPORT
          </span>

          <h1>
            Inspection Report
          </h1>

          <p>
            Complete details for this
            vehicle inspection.
          </p>

        </div>


        <div className="
          report-details-actions
        ">

          <button
            className="report-button"
            onClick={
              async () => {

                try {

                  await downloadPDF(
                    report.inspection_id
                  );

                } catch (err) {

                  setError(
                    err.message
                  );

                }

              }
            }
          >
            ↓ Download PDF
          </button>


          <button
            className="
              report-button
              secondary-report
            "
            onClick={
              async () => {

                try {

                  await downloadJSON(
                    report.inspection_id
                  );

                } catch (err) {

                  setError(
                    err.message
                  );

                }

              }
            }
          >
            ↓ JSON
          </button>

        </div>

      </div>


      {/* =================================================
          REPORT ID
      ================================================= */}

      <div className="
        report-identity-card
      ">

        <div>

          <span>
            INSPECTION ID
          </span>

          <strong>
            {
              report.inspection_id
            }
          </strong>

        </div>


        <div>

          <span>
            CREATED
          </span>

          <strong>
            {
              report.created_at
                ?.replace(
                  "T",
                  " "
                )
            }
          </strong>

        </div>


        <div>

          <span>
            REPORT TYPE
          </span>

          <strong>
            {
              report.report_type
            }
          </strong>

        </div>

      </div>


      {/* =================================================
          VEHICLE INFO
      ================================================= */}

      <section className="
        detail-report-section
      ">

        <div className="
          detail-section-heading
        ">

          <span className="small-label">
            VEHICLE INFORMATION
          </span>

          <h2>
            Vehicle Details
          </h2>

        </div>


        <div className="
          vehicle-report-grid
        ">

          <div className="
            vehicle-report-item
          ">

            <span>
              Registration Number
            </span>

            <strong>
              {
                vehicle.vehicle_number ||
                "Not provided"
              }
            </strong>

          </div>


          <div className="
            vehicle-report-item
          ">

            <span>
              Vehicle Model
            </span>

            <strong>
              {
                vehicle.vehicle_model ||
                "Not provided"
              }
            </strong>

          </div>


          <div className="
            vehicle-report-item
          ">

            <span>
              Customer / Driver
            </span>

            <strong>
              {
                vehicle.customer_name ||
                "Not provided"
              }
            </strong>

          </div>


          <div className="
            vehicle-report-item
          ">

            <span>
              Inspector
            </span>

            <strong>
              {
                vehicle.inspector_name ||
                "Not provided"
              }
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          SINGLE INSPECTION
      ================================================= */}

      {isSingle ? (

        <>
          <section className="
            detail-report-section
          ">

            <div className="
              detail-section-heading
            ">

              <span className="small-label">
                INSPECTION SUMMARY
              </span>

              <h2>
                Analysis Summary
              </h2>

            </div>


            <div className="
              detail-summary-grid
            ">

              <div>

                <span>
                  Status
                </span>

                <strong
                  className={
                    result.status
                      ?.toLowerCase()
                      .includes("damage")
                      ? "status-warning"
                      : "status-safe"
                  }
                >
                  {
                    result.status
                  }
                </strong>

              </div>


              <div>

                <span>
                  Total Damage
                </span>

                <strong>
                  {
                    result.detection_count ||
                    0
                  }
                </strong>

              </div>

            </div>

          </section>


          <section className="
            detail-report-section
          ">

            <div className="
              detail-section-heading
            ">

              <span className="small-label">
                DAMAGE ANALYSIS
              </span>

              <h2>
                Detected Damage
              </h2>

            </div>


            {
              !result.detections ||
              result.detections.length === 0 ? (

                <div className="no-damage">

                  <div className="no-damage-icon">
                    ✓
                  </div>

                  <div>

                    <h3>
                      No visible damage detected
                    </h3>

                    <p>
                      No damage was detected
                      above the configured
                      confidence threshold.
                    </p>

                  </div>

                </div>

              ) : (

                <div className="
                  report-damage-table
                ">

                  <div className="
                    report-table-header
                  ">

                    <span>
                      Damage
                    </span>

                    <span>
                      Confidence
                    </span>

                    <span>
                      Severity
                    </span>

                    <span>
                      Location
                    </span>

                    <span>
                      Area
                    </span>

                  </div>


                  {
                    result.detections.map(
                      (damage, index) => (

                        <div
                          className="
                            report-table-row
                          "
                          key={index}
                        >

                          <strong>
                            {damage.type}
                          </strong>

                          <span>
                            {
                              (
                                damage.confidence *
                                100
                              ).toFixed(1)
                            }%
                          </span>

                          <span className={
                            `severity ${
                              damage.severity
                                ?.toLowerCase()
                            }`
                          }>
                            {
                              damage.severity
                            }
                          </span>

                          <span>
                            {
                              damage.location
                            }
                          </span>

                          <span>
                            {
                              damage.relative_area
                            }%
                          </span>

                        </div>

                      )
                    )
                  }

                </div>

              )
            }

          </section>
        </>

      ) : (

        /* =================================================
           COMPARE REPORT
        ================================================= */

        <>

          <section className="
            detail-report-section
          ">

            <div className="
              detail-section-heading
            ">

              <span className="small-label">
                COMPARISON SUMMARY
              </span>

              <h2>
                Before / After Analysis
              </h2>

            </div>


            <div className="
              comparison-report-summary
            ">

              <div>

                <span>
                  Overall Status
                </span>

                <strong>
                  {
                    result.summary
                      ?.overall_status
                  }
                </strong>

              </div>


              <div>

                <span>
                  Existing Damage
                </span>

                <strong>
                  {
                    result.summary
                      ?.existing_damage_count ||
                    0
                  }
                </strong>

              </div>


              <div>

                <span>
                  Potential New Damage
                </span>

                <strong className="new-report-number">
                  {
                    result.summary
                      ?.potential_new_damage_count ||
                    0
                  }
                </strong>

              </div>

            </div>

          </section>


          {/* EXISTING */}

          <section className="
            detail-report-section
          ">

            <div className="
              detail-section-heading
            ">

              <span className="small-label">
                MATCHED DAMAGE
              </span>

              <h2>
                Existing Damage
              </h2>

            </div>


            {
              !result.existing_damage ||
              result.existing_damage.length === 0 ? (

                <div className="no-damage">
                  No existing damage matches found.
                </div>

              ) : (

                <div className="
                  report-damage-table
                ">

                  <div className="
                    report-table-header
                  ">

                    <span>
                      Damage
                    </span>

                    <span>
                      Confidence
                    </span>

                    <span>
                      IoU
                    </span>

                    <span>
                      Severity
                    </span>

                    <span>
                      Location
                    </span>

                  </div>


                  {
                    result.existing_damage.map(
                      (damage, index) => (

                        <div
                          className="
                            report-table-row
                          "
                          key={index}
                        >

                          <strong>
                            {damage.type}
                          </strong>

                          <span>
                            {
                              (
                                damage.confidence *
                                100
                              ).toFixed(1)
                            }%
                          </span>

                          <span>
                            {
                              damage.iou
                            }
                          </span>

                          <span className={
                            `severity ${
                              damage.severity
                                ?.toLowerCase()
                            }`
                          }>
                            {
                              damage.severity
                            }
                          </span>

                          <span>
                            {
                              damage.location
                            }
                          </span>

                        </div>

                      )
                    )
                  }

                </div>

              )
            }

          </section>


          {/* NEW DAMAGE */}

          <section className="
            detail-report-section
          ">

            <div className="
              detail-section-heading
            ">

              <span className="
                small-label
                new-label
              ">
                ATTENTION REQUIRED
              </span>

              <h2>
                Potential New Damage
              </h2>

            </div>


            {
              !result.potential_new_damage ||
              result.potential_new_damage.length === 0 ? (

                <div className="no-damage">
                  No potential new damage detected.
                </div>

              ) : (

                <div className="
                  report-damage-table
                  new-report-table
                ">

                  <div className="
                    report-table-header
                  ">

                    <span>
                      Damage
                    </span>

                    <span>
                      Confidence
                    </span>

                    <span>
                      Severity
                    </span>

                    <span>
                      Location
                    </span>

                    <span>
                      Area
                    </span>

                  </div>


                  {
                    result
                      .potential_new_damage
                      .map(
                        (damage, index) => (

                          <div
                            className="
                              report-table-row
                            "
                            key={index}
                          >

                            <strong>
                              {damage.type}
                            </strong>

                            <span>
                              {
                                (
                                  damage.confidence *
                                  100
                                ).toFixed(1)
                              }%
                            </span>

                            <span className={
                              `severity ${
                                damage.severity
                                  ?.toLowerCase()
                              }`
                            }>
                              {
                                damage.severity
                              }
                            </span>

                            <span>
                              {
                                damage.location
                              }
                            </span>

                            <span>
                              {
                                damage.relative_area
                              }%
                            </span>

                          </div>

                        )
                      )
                  }

                </div>

              )
            }

          </section>

        </>
      )}


      {/* =================================================
          FOOTER
      ================================================= */}

      <div className="
        report-disclaimer
      ">

        <strong>
          Important:
        </strong>

        {" "}
        This report contains
        AI-generated visual inspection
        results. Severity is based on a
        project-level visual heuristic and
        potential new damage should be
        manually verified.

      </div>


      <div className="
        report-back-link
      ">

        <Link to="/history">

          ← Back to Inspection History

        </Link>

      </div>

    </div>
  );
}

export default ReportDetails;