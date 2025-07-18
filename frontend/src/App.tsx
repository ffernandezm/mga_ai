import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useState } from "react";
import Navbar from "./components/Navbar";
import { ProjectProvider } from "./context/ProjectContext";
import Home from "./pages/Home";
import CreateProject from "./pages/CreateProject";
import CreateParticipant from "./pages/CreateParticipant";
import Projects from "./pages/Projects";
import ProjectForm from "./components/ProjectForm";
import "bootstrap/dist/css/bootstrap.min.css";
import ProjectList from "./components/ProjectList";
import Formulation from "./pages/Formulation";

function App() {
  return (
    <Router>
      <ProjectProvider>
        <Navbar />
        <div className="container mt-4">
          <Routes>
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/create-project" element={<CreateProject />} />
            <Route path="/edit-project/:id" element={<Formulation />} />
            <Route path="/projects/:projectId/create-participant" element={<CreateParticipant />} />
            <Route path="/" element={<Home />} />
          </Routes>
        </div>
      </ProjectProvider>
    </Router>

  );
}

export default App;