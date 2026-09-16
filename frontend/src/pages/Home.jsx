import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home-page">

      <section className="hero-section">

        <div className="hero-left">

          <span className="hero-badge">
            AI POWERED VEHICLE
            INSPECTION
          </span>

          <h1>
            Inspect Your Car
            <br />
            <span>Smarter.</span>{" "}
            Faster.
          </h1>

          <p className="hero-description">
            AutoInspect India uses
            computer vision and a
            YOLO-based AI model to
            detect visible vehicle
            damage, estimate visual
            severity, and compare
            before-and-after
            inspections.
          </p>

          <div className="hero-buttons">

            <Link to="/inspect">
              <button className="primary-button">
                Start Inspection →
              </button>
            </Link>

            <Link to="/compare">
              <button className="secondary-button">
                Compare Vehicle
              </button>
            </Link>

          </div>


          <div className="hero-stats">

            <div className="hero-stat">

              <strong>
                6
              </strong>

              <span>
                Damage Classes
              </span>

            </div>


            <div className="hero-stat">

              <strong>
                YOLO
              </strong>

              <span>
                Detection Model
              </span>

            </div>


            <div className="hero-stat">

              <strong>
                AI
              </strong>

              <span>
                Visual Analysis
              </span>

            </div>

          </div>

        </div>


        <div className="hero-right">

          <div className="ai-card">

            <div className="ai-card-header">

              <span>
                LIVE AI ANALYSIS
              </span>

              <span className="online-dot">
                ● ONLINE
              </span>

            </div>


            <div className="car-visual">

              <div className="car-glow">
              </div>


              <div className="car-outline">

                <div className="car-roof">
                </div>

                <div className="car-body">

                  <div className="car-window">
                  </div>

                  <div className="car-window-small">
                  </div>

                  <div className="car-door">
                  </div>

                  <div className="
                    car-wheel
                    wheel-one
                  ">
                  </div>

                  <div className="
                    car-wheel
                    wheel-two
                  ">
                  </div>

                </div>

              </div>


              <div className="scan-line">
              </div>


              <div className="
                damage-marker
                marker-one
              ">
                Scratch
              </div>


              <div className="
                damage-marker
                marker-two
              ">
                Dent
              </div>

            </div>


            <div className="ai-card-footer">

              <span>
                Computer Vision
              </span>

              <strong>
                Scanning vehicle...
              </strong>

            </div>

          </div>

        </div>

      </section>


      <section className="feature-section">

        <div className="section-heading">

          <span className="page-tag">
            HOW IT WORKS
          </span>

          <h2>
            Vehicle inspection,
            <br />
            powered by AI.
          </h2>

          <p>
            A simple workflow from
            vehicle image to
            inspection information.
          </p>

        </div>


        <div className="feature-grid">

          <div className="feature-card">

            <div className="feature-number">
              01
            </div>

            <h3>
              Upload Vehicle
            </h3>

            <p>
              Upload a clear image
              of the vehicle that
              you want to inspect.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-number">
              02
            </div>

            <h3>
              AI Detection
            </h3>

            <p>
              The trained YOLO model
              analyzes the image for
              visible vehicle damage.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-number">
              03
            </div>

            <h3>
              Inspection Report
            </h3>

            <p>
              View detected damage,
              confidence, location,
              severity and report ID.
            </p>

          </div>

        </div>

      </section>


      <section className="home-cta">

        <div>

          <span className="page-tag">
            READY TO INSPECT?
          </span>

          <h2>
            Start your AI vehicle
            inspection.
          </h2>

        </div>

        <Link to="/inspect">

          <button className="primary-button">
            Start Inspection →
          </button>

        </Link>

      </section>

    </div>
  );
}

export default Home;