import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Inspect from "./pages/Inspect";
import Compare from "./pages/Compare";
import History from "./pages/History";
import ReportDetails from "./pages/ReportDetails";

import "./App.css";


function App() {

  return (
    <BrowserRouter>

      <Navbar />

      <main>

        <Routes>

          <Route
            path="/"
            element={<Home />}
          />


          <Route
            path="/inspect"
            element={<Inspect />}
          />


          <Route
            path="/compare"
            element={<Compare />}
          />


          <Route
            path="/history"
            element={<History />}
          />


          <Route
            path="/reports/:inspectionId"
            element={<ReportDetails />}
          />

        </Routes>

      </main>

    </BrowserRouter>
  );
}


export default App;