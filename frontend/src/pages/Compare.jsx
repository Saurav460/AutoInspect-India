import { useState } from "react";

import {
  compareImages,
  downloadPDF,
  downloadJSON,
} from "../services/api";

import DamageCard from "../components/DamageCard";
import VehicleDetails from "../components/VehicleDetails";


function Compare() {

  const [beforeFile, setBeforeFile] =
    useState(null);

  const [afterFile, setAfterFile] =
    useState(null);

  const [beforePreview, setBeforePreview] =
    useState("");

  const [afterPreview, setAfterPreview] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [vehicle, setVehicle] =
    useState({
      vehicle_number: "",
      vehicle_model: "",
      customer_name: "",
      inspector_name: "",
    });


  /* =========================================
     BEFORE FILE
  ========================================= */

  const handleBeforeChange = (
    event
  ) => {

    const file =
      event.target.files[0];

    if (!file) {
      return;
    }

    setBeforeFile(file);

    setBeforePreview(
      URL.createObjectURL(file)
    );

    setResult(null);
    setError("");
  };


  /* =========================================
     AFTER FILE
  ========================================= */

  const handleAfterChange = (
    event
  ) => {

    const file =
      event.target.files[0];

    if (!file) {
      return;
    }

    setAfterFile(file);

    setAfterPreview(
      URL.createObjectURL(file)
    );

    setResult(null);
    setError("");
  };


  /* =========================================
     COMPARE
  ========================================= */

  const handleCompare =
    async () => {

      if (
        !beforeFile ||
        !afterFile
      ) {

        setError(
          "Please select both before and after images."
        );

        return;
      }

      try {

        setLoading(true);
        setError("");
        setResult(null);

        const data =
          await compareImages(
            beforeFile,
            afterFile,
            vehicle
          );

        setResult(data);

      } catch (err) {

        setError(
          err.message ||
            "Comparison failed."
        );

      } finally {

        setLoading(false);

      }
    };


  return (
    <div className="dashboard-page">

      {/* ===================================
          HEADER
      =================================== */}

      <div className="page-header">

        <span className="page-tag">
          BEFORE / AFTER ANALYSIS
        </span>

        <h1>
          Compare Vehicle Inspections
        </h1>

        <p>
          Compare two vehicle images and
          identify potential new damage.
        </p>

      </div>


      {/* ===================================
          VEHICLE DETAILS
      =================================== */}

      <VehicleDetails
        vehicle={vehicle}
        setVehicle={setVehicle}
      />


      {/* ===================================
          IMAGE UPLOADS
      =================================== */}

      <div className="comparison-upload-grid">

        {/* BEFORE */}

        <div className="image-upload-card">

          <div className="comparison-top">

            <span className="comparison-label">
              BEFORE
            </span>

            <span className="image-status">
              Previous
            </span>

          </div>

          <h2>
            Previous Inspection
          </h2>

          <p>
            Upload the earlier vehicle image.
          </p>

          <label className="upload-button">

            Select Before Image

            <input
              type="file"
              accept="
                image/jpeg,
                image/png,
                image/webp
              "
              hidden
              onChange={
                handleBeforeChange
              }
            />

          </label>

          {beforePreview ? (

            <img
              src={beforePreview}
              alt="Before vehicle"
              className="compare-preview"
            />

          ) : (

            <div className="empty-image">

              <span>
                +
              </span>

              <p>
                Before image preview
              </p>

            </div>

          )}

          {beforeFile && (

            <div className="file-name">
              {beforeFile.name}
            </div>

          )}

        </div>


        {/* AFTER */}

        <div className="image-upload-card">

          <div className="comparison-top">

            <span className="comparison-label">
              AFTER
            </span>

            <span className="image-status">
              Current
            </span>

          </div>

          <h2>
            Current Inspection
          </h2>

          <p>
            Upload the current vehicle image.
          </p>

          <label className="upload-button">

            Select After Image

            <input
              type="file"
              accept="
                image/jpeg,
                image/png,
                image/webp
              "
              hidden
              onChange={
                handleAfterChange
              }
            />

          </label>

          {afterPreview ? (

            <img
              src={afterPreview}
              alt="After vehicle"
              className="compare-preview"
            />

          ) : (

            <div className="empty-image">

              <span>
                +
              </span>

              <p>
                After image preview
              </p>

            </div>

          )}

          {afterFile && (

            <div className="file-name">
              {afterFile.name}
            </div>

          )}

        </div>

      </div>


      {/* ===================================
          BUTTON
      =================================== */}

      <div className="compare-action">

        <button
          className="compare-button"
          onClick={
            handleCompare
          }
          disabled={
            !beforeFile ||
            !afterFile ||
            loading
          }
        >
          {loading
            ? "Analyzing Comparison..."
            : "Compare Vehicle Images →"}
        </button>

      </div>


      {/* ===================================
          ERROR
      =================================== */}

      {error && (

        <div className="error-box">

          <strong>
            Error:
          </strong>{" "}

          {error}

        </div>

      )}


      {/* ===================================
          LOADING
      =================================== */}

      {loading && (

        <div className="loading-panel">

          <div className="loader"></div>

          <h3>
            Comparing vehicle inspections
          </h3>

          <p>
            AI is matching detected damage
            between both images.
          </p>

        </div>

      )}


      {/* ===================================
          RESULT
      =================================== */}

      {result && !loading && (

        <div className="compare-results">

          <div className="comparison-status">

            <span className="status-label">
              OVERALL STATUS
            </span>

            <h2>
              {
                result.summary
                  .overall_status
              }
            </h2>

            <p>
              AI comparison completed using
              detected damage and bounding-box
              matching.
            </p>


            {/* COUNTS */}

            <div className="comparison-counts">

              <div className="comparison-count">

                <strong>
                  {
                    result.summary
                      .existing_damage_count
                  }
                </strong>

                <span>
                  Existing Damage
                </span>

              </div>

              <div className="comparison-divider"></div>

              <div className="
                comparison-count
                new-count
              ">

                <strong>
                  {
                    result.summary
                      .potential_new_damage_count
                  }
                </strong>

                <span>
                  Potential New Damage
                </span>

              </div>

            </div>


            {/* REPORT INFO */}

            <div className="
              report-meta
              dark-meta
            ">

              <div>

                <span>
                  Inspection ID
                </span>

                <strong>
                  {result.inspection_id}
                </strong>

              </div>

              <div>

                <span>
                  Date &amp; Time
                </span>

                <strong>
                  {result.created_at}
                </strong>

              </div>

            </div>


            {/* REPORT BUTTONS */}

            <div className="report-actions">

              <button
                className="report-button"
                onClick={
                  async () => {

                    try {

                      await downloadPDF(
                        result.inspection_id
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
                        result.inspection_id
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


          {/* =================================
              EXISTING DAMAGE
          ================================= */}

          <section className="damage-section">

            <div className="section-title-row">

              <div>

                <span className="small-label">
                  MATCHED DAMAGE
                </span>

                <h2>
                  Existing Damage
                </h2>

              </div>

              <span className="count-badge">
                {
                  result.existing_damage
                    .length
                }
              </span>

            </div>


            {result.existing_damage
              .length === 0 ? (

              <div className="no-damage">
                No matched existing damage
                found.
              </div>

            ) : (

              <div className="damage-grid">

                {
                  result.existing_damage.map(
                    (damage, index) => (
                      <DamageCard
                        key={index}
                        damage={damage}
                        index={index}
                      />
                    )
                  )
                }

              </div>

            )}

          </section>


          {/* =================================
              NEW DAMAGE
          ================================= */}

          <section className="damage-section">

            <div className="section-title-row">

              <div>

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

              <span className="
                count-badge
                new-badge
              ">
                {
                  result
                    .potential_new_damage
                    .length
                }
              </span>

            </div>


            {
              result
                .potential_new_damage
                .length === 0 ? (

              <div className="no-damage">
                No potential new damage
                detected.
              </div>

            ) : (

              <div className="damage-grid">

                {
                  result
                    .potential_new_damage
                    .map(
                      (damage, index) => (
                        <DamageCard
                          key={index}
                          damage={damage}
                          index={index}
                          isNew={true}
                        />
                      )
                    )
                }

              </div>

            )}

          </section>

        </div>
      )}

    </div>
  );
}

export default Compare;