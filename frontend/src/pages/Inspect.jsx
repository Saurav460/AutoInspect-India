import { useState } from "react";

import {
  inspectImage,
  downloadPDF,
  downloadJSON,
} from "../services/api";

import DetectionViewer from "../components/DetectionViewer";
import DamageCard from "../components/DamageCard";
import ResultSummary from "../components/ResultSummary";
import VehicleDetails from "../components/VehicleDetails";


function Inspect() {

  const [file, setFile] =
    useState(null);

  const [preview, setPreview] =
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
     FILE CHANGE
  ========================================= */

  const handleFileChange = (
    event
  ) => {

    const selectedFile =
      event.target.files[0];

    if (!selectedFile) {
      return;
    }

    if (
      !selectedFile.type.startsWith(
        "image/"
      )
    ) {
      setError(
        "Please select a valid image file."
      );

      return;
    }

    setFile(selectedFile);

    setPreview(
      URL.createObjectURL(
        selectedFile
      )
    );

    setResult(null);
    setError("");
  };


  /* =========================================
     INSPECT
  ========================================= */

  const handleInspect =
    async () => {

      if (!file) {

        setError(
          "Please select a vehicle image first."
        );

        return;
      }

      try {

        setLoading(true);
        setError("");
        setResult(null);

        const data =
          await inspectImage(
            file,
            vehicle
          );

        setResult(data);

      } catch (err) {

        setError(
          err.message ||
            "Inspection failed."
        );

      } finally {

        setLoading(false);

      }
    };


  /* =========================================
     RESET
  ========================================= */

  const handleNewInspection =
    () => {

      setFile(null);
      setPreview("");
      setResult(null);
      setError("");

    };


  return (
    <div className="dashboard-page">

      {/* ===================================
          HEADER
      =================================== */}

      <div className="page-header">

        <span className="page-tag">
          AI INSPECTION
        </span>

        <h1>
          Vehicle Damage Inspection
        </h1>

        <p>
          Upload a vehicle image and let
          the AI model analyze visible damage.
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
          UPLOAD
      =================================== */}

      <div className="upload-panel">

        <div className="upload-icon">
          ↑
        </div>

        <h2>
          Upload Vehicle Image
        </h2>

        <p>
          Supported formats:
          JPG, PNG, WEBP
        </p>

        <label className="upload-button">

          Choose Image

          <input
            type="file"
            accept="
              image/jpeg,
              image/png,
              image/webp
            "
            onChange={
              handleFileChange
            }
            hidden
          />

        </label>

        {file && (
          <div className="selected-file">

            <span>
              Selected file
            </span>

            <strong>
              {file.name}
            </strong>

          </div>
        )}

      </div>


      {/* ===================================
          PREVIEW
      =================================== */}

      {preview && !result && (

        <div className="preview-panel">

          <div className="panel-header">

            <div>

              <span className="small-label">
                IMAGE PREVIEW
              </span>

              <h2>
                Ready for analysis
              </h2>

              <p>
                Review your image before
                starting AI inspection.
              </p>

            </div>

            <button
              className="primary-button"
              onClick={
                handleInspect
              }
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Run AI Inspection →"}
            </button>

          </div>

          <img
            src={preview}
            alt="Selected vehicle"
            className="large-preview"
          />

        </div>

      )}


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
            AI is analyzing your vehicle
          </h3>

          <p>
            YOLO model is processing
            the image.
          </p>

        </div>

      )}


      {/* ===================================
          RESULT
      =================================== */}

      {result && !loading && (

        <div className="results-container">

          <div className="results-heading">

            <div>

              <span className="page-tag">
                ANALYSIS COMPLETE
              </span>

              <h2>
                Inspection Results
              </h2>

              <p>
                AI-generated visual
                inspection of the vehicle.
              </p>

              <div className="report-meta">

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

            </div>

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

              <button
                className="secondary-button"
                onClick={
                  handleNewInspection
                }
              >
                New Inspection
              </button>

            </div>

          </div>


          {/* SUMMARY */}

          <ResultSummary
            result={result}
          />


          {/* IMAGE */}

          <div className="result-image-panel">

            <div className="panel-title">

              <h2>
                AI Detection View
              </h2>

              <span>
                {result.detection_count}{" "}
                detection
                {result.detection_count !== 1
                  ? "s"
                  : ""}
              </span>

            </div>

            <DetectionViewer
              image={preview}
              detections={
                result.detections
              }
            />

          </div>


          {/* DAMAGE */}

          <section className="damage-section">

            <div className="section-title-row">

              <div>

                <span className="small-label">
                  DAMAGE ANALYSIS
                </span>

                <h2>
                  Detected Damage
                </h2>

              </div>

              <span className="count-badge">
                {result.detection_count}
              </span>

            </div>


            {result.detections.length ===
            0 ? (

              <div className="no-damage">

                <div className="no-damage-icon">
                  ✓
                </div>

                <div>

                  <h3>
                    No visible damage detected
                  </h3>

                  <p>
                    The AI model did not detect
                    damage above the configured
                    confidence threshold.
                  </p>

                </div>

              </div>

            ) : (

              <div className="damage-grid">

                {result.detections.map(
                  (damage, index) => (

                    <DamageCard
                      key={index}
                      damage={damage}
                      index={index}
                    />

                  )
                )}

              </div>

            )}

          </section>

        </div>
      )}

    </div>
  );
}

export default Inspect;