import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import { ProjectProvider } from "./context/ProjectContext";
import Home from "./pages/Home";
import CreateProject from "./pages/CreateProject";
import CreateParticipant from "./pages/CreateParticipant";
import EditParticipant from "./pages/EditParticipant";
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
            <Route path="/projects/:projectId/edit-participant/:participantId" element={<EditParticipant />} />
            <Route path="/" element={<Home />} />
          </Routes>
        </div>
      </ProjectProvider>
    </Router>

  );
}

export default App;