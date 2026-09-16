const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


/* =========================================================
   ERROR HANDLER
========================================================= */

const getErrorMessage = async (response) => {
  try {
    const data =
      await response.json();

    if (
      Array.isArray(
        data.detail
      )
    ) {
      return data.detail
        .map((error) => {

          if (
            typeof error ===
            "string"
          ) {
            return error;
          }

          const location =
            Array.isArray(
              error.loc
            )
              ? error.loc.join(
                  " → "
                )
              : "";

          return (
            error.msg ||
            location ||
            "Invalid request"
          );
        })
        .join(" | ");
    }

    if (
      typeof data.detail ===
      "string"
    ) {
      return data.detail;
    }

    return JSON.stringify(data);

  } catch {

    return (
      `Request failed with status ` +
      `${response.status}`
    );
  }
};


/* =========================================================
   INSPECT IMAGE
========================================================= */

export const inspectImage = async (
  file,
  vehicle = {}
) => {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  formData.append(
    "vehicle_number",
    vehicle.vehicle_number || ""
  );

  formData.append(
    "vehicle_model",
    vehicle.vehicle_model || ""
  );

  formData.append(
    "customer_name",
    vehicle.customer_name || ""
  );

  formData.append(
    "inspector_name",
    vehicle.inspector_name || ""
  );

  const response =
    await fetch(
      `${API_BASE_URL}/inspect`,
      {
        method: "POST",
        body: formData,
      }
    );

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  return response.json();
};


/* =========================================================
   COMPARE IMAGES
========================================================= */

export const compareImages = async (
  beforeFile,
  afterFile,
  vehicle = {}
) => {

  const formData =
    new FormData();

  formData.append(
    "before_image",
    beforeFile
  );

  formData.append(
    "after_image",
    afterFile
  );

  formData.append(
    "vehicle_number",
    vehicle.vehicle_number || ""
  );

  formData.append(
    "vehicle_model",
    vehicle.vehicle_model || ""
  );

  formData.append(
    "customer_name",
    vehicle.customer_name || ""
  );

  formData.append(
    "inspector_name",
    vehicle.inspector_name || ""
  );

  const response =
    await fetch(
      `${API_BASE_URL}/compare`,
      {
        method: "POST",
        body: formData,
      }
    );

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  return response.json();
};


/* =========================================================
   DOWNLOAD FILE
========================================================= */

const downloadFile = async (
  url,
  filename
) => {

  const response =
    await fetch(url);

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  const blob =
    await response.blob();

  const blobUrl =
    window.URL.createObjectURL(
      blob
    );

  const link =
    document.createElement(
      "a"
    );

  link.href = blobUrl;
  link.download = filename;

  document.body.appendChild(
    link
  );

  link.click();

  link.remove();

  window.URL.revokeObjectURL(
    blobUrl
  );
};


/* =========================================================
   DOWNLOAD PDF
========================================================= */

export const downloadPDF = async (
  inspectionId
) => {

  await downloadFile(
    `${API_BASE_URL}/reports/` +
      `${inspectionId}/pdf`,

    `AutoInspect-${inspectionId}.pdf`
  );
};


/* =========================================================
   DOWNLOAD JSON
========================================================= */

export const downloadJSON = async (
  inspectionId
) => {

  await downloadFile(
    `${API_BASE_URL}/reports/` +
      `${inspectionId}/json`,

    `AutoInspect-${inspectionId}.json`
  );
};


/* =========================================================
   GET ALL REPORTS
========================================================= */

export const getReports = async (
  search = ""
) => {

  const query =
    search.trim()
      ? `?search=${encodeURIComponent(
          search.trim()
        )}`
      : "";

  const response =
    await fetch(
      `${API_BASE_URL}/reports${query}`
    );

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  return response.json();
};


/* =========================================================
   GET SINGLE REPORT
========================================================= */

export const getReport = async (
  inspectionId
) => {

  const response =
    await fetch(
      `${API_BASE_URL}/reports/` +
        encodeURIComponent(
          inspectionId
        )
    );

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  return response.json();
};

/* =========================================================
   DELETE REPORT
========================================================= */

export const deleteReport = async (
  inspectionId
) => {

  const response =
    await fetch(
      `${API_BASE_URL}/reports/` +
        encodeURIComponent(
          inspectionId
        ),
      {
        method: "DELETE",
      }
    );

  if (!response.ok) {

    const message =
      await getErrorMessage(
        response
      );

    throw new Error(
      message
    );
  }

  return response.json();
};