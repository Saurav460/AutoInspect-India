function VehicleDetails({
  vehicle,
  setVehicle,
}) {
  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setVehicle((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  return (
    <div className="vehicle-details-panel">

      <div className="vehicle-details-header">

        <span className="small-label">
          VEHICLE INFORMATION
        </span>

        <h2>
          Inspection Details
        </h2>

        <p>
          Add vehicle information for
          the inspection report.
        </p>

      </div>

      <div className="vehicle-form-grid">

        <div className="form-group">

          <label>
            Registration Number
          </label>

          <input
            type="text"
            name="vehicle_number"
            value={
              vehicle.vehicle_number
            }
            onChange={handleChange}
            placeholder="e.g. DL01AB1234"
          />

        </div>

        <div className="form-group">

          <label>
            Vehicle Model
          </label>

          <input
            type="text"
            name="vehicle_model"
            value={
              vehicle.vehicle_model
            }
            onChange={handleChange}
            placeholder="e.g. Hyundai Creta"
          />

        </div>

        <div className="form-group">

          <label>
            Customer / Driver
          </label>

          <input
            type="text"
            name="customer_name"
            value={
              vehicle.customer_name
            }
            onChange={handleChange}
            placeholder="Customer name"
          />

        </div>

        <div className="form-group">

          <label>
            Inspector
          </label>

          <input
            type="text"
            name="inspector_name"
            value={
              vehicle.inspector_name
            }
            onChange={handleChange}
            placeholder="Inspector name"
          />

        </div>

      </div>

    </div>
  );
}

export default VehicleDetails;