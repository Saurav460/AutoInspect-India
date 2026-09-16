import {
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  getReports,
  downloadPDF,
  downloadJSON,
  deleteReport,
} from "../services/api";


function History() {

  const [reports, setReports] =
    useState([]);

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =====================================================
     LOAD REPORTS
  ===================================================== */

  const loadReports = async (
    searchValue = ""
  ) => {

    try {

      setLoading(true);
      setError("");

      const data =
        await getReports(
          searchValue
        );

      setReports(
        data.reports || []
      );

    } catch (err) {

      setError(
        err.message ||
          "Unable to load inspection history."
      );

    } finally {

      setLoading(false);

    }
  };


  /* =====================================================
     INITIAL LOAD
  ===================================================== */

  useEffect(() => {

    loadReports();

  }, []);


  /* =====================================================
     SEARCH
  ===================================================== */

  const handleSearch = (
    event
  ) => {

    const value =
      event.target.value;

    setSearch(value);

    loadReports(value);
  };


  /* =====================================================
     DELETE REPORT
  ===================================================== */

  const handleDelete = async (
    inspectionId
  ) => {

    const confirmed =
      window.confirm(
        "Are you sure you want to delete this inspection report?"
      );

    if (!confirmed) {
      return;
    }

    try {

      setError("");

      await deleteReport(
        inspectionId
      );

      // Immediately remove deleted report
      setReports(
        (previousReports) =>
          previousReports.filter(
            (report) =>
              report.inspection_id !==
              inspectionId
          )
      );

    } catch (err) {

      setError(
        err.message ||
          "Unable to delete report."
      );

    }
  };


  /* =====================================================
     CLEAR SEARCH
  ===================================================== */

  const handleClearSearch = () => {

    setSearch("");

    loadReports("");

  };


  return (
    <div className="dashboard-page">

      {/* =================================================
          PAGE HEADER
      ================================================= */}

      <div className="page-header">

        <span className="page-tag">
          INSPECTION HISTORY
        </span>

        <h1>
          Previous Inspections
        </h1>

        <p>
          View, search and manage your
          previous vehicle inspection reports.
        </p>

      </div>


      {/* =================================================
          SEARCH TOOLBAR
      ================================================= */}

      <div className="history-toolbar">

        <div className="search-box">

          <span className="search-icon">
            ⌕
          </span>

          <input
            type="text"
            value={search}
            onChange={
              handleSearch
            }
            placeholder={
              "Search vehicle number, " +
              "model or inspection ID..."
            }
          />

          {search && (
            <button
              className="clear-search"
              onClick={
                handleClearSearch
              }
              type="button"
            >
              ×
            </button>
          )}

        </div>


        <div className="history-count">

          <strong>
            {reports.length}
          </strong>

          <span>
            {reports.length === 1
              ? " Report"
              : " Reports"}
          </span>

        </div>

      </div>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <div className="error-box">

          <strong>
            Error:
          </strong>{" "}

          {error}

        </div>

      )}


      {/* =================================================
          LOADING
      ================================================= */}

      {loading ? (

        <div className="loading-panel">

          <div className="loader">
          </div>

          <h3>
            Loading inspection history...
          </h3>

          <p>
            Fetching your saved reports.
          </p>

        </div>

      ) : reports.length === 0 ? (

        /* =================================================
           EMPTY STATE
        ================================================= */

        <div className="history-empty">

          <div className="history-empty-icon">
            ◫
          </div>

          <h2>
            No inspections found
          </h2>

          <p>
            {search
              ? "No reports match your search."
              : "Your completed inspections will appear here."
            }
          </p>

          {search ? (

            <button
              className="secondary-button"
              onClick={
                handleClearSearch
              }
            >
              Clear Search
            </button>

          ) : (

            <Link to="/inspect">

              <button className="primary-button">
                Start First Inspection →
              </button>

            </Link>

          )}

        </div>

      ) : (

        /* =================================================
           REPORT LIST
        ================================================= */

        <div className="history-list">

          {reports.map(
            (report) => (

              <div
                className="history-card"
                key={
                  report.inspection_id
                }
              >

                {/* =======================================
                    MAIN INFORMATION
                ======================================= */}

                <div className="history-card-main">

                  <div className="history-card-top">

                    <div className="history-title-block">

                      <span className="
                        history-type
                      ">

                        {
                          report.report_type ===
                          "Single Image Inspection"
                            ? "SINGLE INSPECTION"
                            : "BEFORE / AFTER"
                        }

                      </span>

                      <h2>

                        {
                          report.vehicle_model ||
                          "Vehicle Inspection"
                        }

                      </h2>

                    </div>


                    {/* STATUS */}

                    <span
                      className={`
                        history-status
                        ${
                          report.status
                            ?.toLowerCase()
                            .includes("damage")
                            ? "status-damage"
                            : "status-clear"
                        }
                      `}
                    >
                      {report.status}
                    </span>

                  </div>


                  {/* ===================================
                      META
                  =================================== */}

                  <div className="
                    history-meta-grid
                  ">

                    <div>

                      <span>
                        Inspection ID
                      </span>

                      <strong>
                        {
                          report.inspection_id
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Vehicle Number
                      </span>

                      <strong>
                        {
                          report.vehicle_number ||
                          "Not provided"
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Date
                      </span>

                      <strong>
                        {
                          report.created_at
                            ?.replace(
                              "T",
                              " "
                            ) || "-"
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Total Damage
                      </span>

                      <strong>
                        {
                          report.damage_count ??
                          0
                        }
                      </strong>

                    </div>

                  </div>


                  {/* ===================================
                      COMPARE STATS
                  =================================== */}

                  {report.report_type !==
                    "Single Image Inspection" && (

                    <div className="
                      comparison-mini-stats
                    ">

                      <span>
                        Existing:
                        {" "}
                        <strong>
                          {
                            report
                              .existing_damage_count ??
                            0
                          }
                        </strong>
                      </span>

                      <span>
                        Potential New:
                        {" "}
                        <strong className="
                          new-count-text
                        ">
                          {
                            report
                              .new_damage_count ??
                            0
                          }
                        </strong>
                      </span>

                    </div>

                  )}

                </div>


                {/* =======================================
                    ACTIONS
                ======================================= */}

                <div className="
                  history-card-actions
                ">

                  {/* VIEW */}

                  <Link
                    to={
                      `/reports/` +
                      encodeURIComponent(
                        report.inspection_id
                      )
                    }
                  >
                    <button
                      className="
                        report-action-button
                        view-action
                      "
                    >
                      View Report
                    </button>
                  </Link>


                  {/* PDF */}

                  <button
                    className="
                      report-action-button
                      pdf-action
                    "
                    onClick={
                      async () => {

                        try {

                          setError("");

                          await downloadPDF(
                            report.inspection_id
                          );

                        } catch (err) {

                          setError(
                            err.message ||
                              "Unable to download PDF."
                          );

                        }

                      }
                    }
                  >
                    PDF
                  </button>


                  {/* JSON */}

                  <button
                    className="
                      report-action-button
                      json-action
                    "
                    onClick={
                      async () => {

                        try {

                          setError("");

                          await downloadJSON(
                            report.inspection_id
                          );

                        } catch (err) {

                          setError(
                            err.message ||
                              "Unable to download JSON."
                          );

                        }

                      }
                    }
                  >
                    JSON
                  </button>


                  {/* DELETE */}

                  <button
                    type="button"
                    className="
                      report-action-button
                      delete-action
                    "
                    onClick={() =>
                      handleDelete(
                        report.inspection_id
                      )
                    }
                  >
                    Delete
                  </button>

                </div>

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}

export default History;