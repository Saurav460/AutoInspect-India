import { useState } from "react";

function DetectionViewer({
  image,
  detections = [],
}) {
  const [imageSize, setImageSize] =
    useState({
      width: 1,
      height: 1,
    });

  const handleImageLoad = (
    event
  ) => {
    setImageSize({
      width:
        event.target.naturalWidth,

      height:
        event.target.naturalHeight,
    });
  };

  return (
    <div className="viewer-container">

      <img
        src={image}
        alt="Vehicle inspection"
        className="inspection-image"
        onLoad={
          handleImageLoad
        }
      />

      {detections.map(
        (damage, index) => {

          if (
            !damage.bounding_box ||
            damage.bounding_box
              .length !== 4
          ) {
            return null;
          }

          const [
            x1,
            y1,
            x2,
            y2,
          ] = damage.bounding_box;

          const left =
            (x1 /
              imageSize.width) *
            100;

          const top =
            (y1 /
              imageSize.height) *
            100;

          const width =
            ((x2 - x1) /
              imageSize.width) *
            100;

          const height =
            ((y2 - y1) /
              imageSize.height) *
            100;

          const confidence =
            (
              Number(
                damage.confidence ||
                  0
              ) * 100
            ).toFixed(0);

          return (
            <div
              key={index}
              className="bounding-box"
              style={{
                left:
                  `${left}%`,

                top:
                  `${top}%`,

                width:
                  `${width}%`,

                height:
                  `${height}%`,
              }}
            >

              <div className="box-label">

                {damage.type}

                {" · "}

                {confidence}%

              </div>

            </div>
          );
        }
      )}

    </div>
  );
}

export default DetectionViewer;