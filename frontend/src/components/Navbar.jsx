import {
  Link,
  useLocation,
} from "react-router-dom";


function Navbar() {

  const location =
    useLocation();


  return (
    <nav className="navbar">

      <div className="nav-container">

        <Link
          to="/"
          className="logo"
        >
          AutoInspect{" "}
          <span>
            India
          </span>
        </Link>


        <div className="nav-links">

          <Link
            to="/"
            className={
              location.pathname ===
              "/"
                ? "active-link"
                : ""
            }
          >
            Home
          </Link>


          <Link
            to="/inspect"
            className={
              location.pathname ===
              "/inspect"
                ? "active-link"
                : ""
            }
          >
            Inspect
          </Link>


          <Link
            to="/compare"
            className={
              location.pathname ===
              "/compare"
                ? "active-link"
                : ""
            }
          >
            Compare
          </Link>


          <Link
            to="/history"
            className={
              location.pathname.startsWith(
                "/history"
              ) ||
              location.pathname.startsWith(
                "/reports"
              )
                ? "active-link"
                : ""
            }
          >
            History
          </Link>

        </div>

      </div>

    </nav>
  );
}


export default Navbar;