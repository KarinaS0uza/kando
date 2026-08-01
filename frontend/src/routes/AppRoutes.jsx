import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "../components/layout/ProtectedRoute";

import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Dashboard from "../pages/Dashboard";
import UploadProfile from "../pages/UploadProfile";
import Score from "../pages/Score";
import SimulationInstructions from "../pages/SimulationInstructions";
import SimulationQuestions from "../pages/SimulationQuestions";
import Report from "../pages/Report";
import TalentPassport from "../pages/TalentPassport";
import StudyPath from "../pages/StudyPath";
import Reliability from "../pages/Reliability";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <ProtectedRoute>
            <UploadProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload/reliability"
        element={
          <ProtectedRoute>
            <Reliability />
          </ProtectedRoute>
        }
      />
      <Route
        path="/score"
        element={
          <ProtectedRoute>
            <Score />
          </ProtectedRoute>
        }
      />
      <Route
        path="/simulation/instructions"
        element={
          <ProtectedRoute>
            <SimulationInstructions />
          </ProtectedRoute>
        }
      />
      <Route
        path="/simulation/questions"
        element={
          <ProtectedRoute>
            <SimulationQuestions />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report"
        element={
          <ProtectedRoute>
            <Report />
          </ProtectedRoute>
        }
      />
      <Route
        path="/talent-passport"
        element={
          <ProtectedRoute>
            <TalentPassport />
          </ProtectedRoute>
        }
      />
      <Route
        path="/study-path"
        element={
          <ProtectedRoute>
            <StudyPath />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
