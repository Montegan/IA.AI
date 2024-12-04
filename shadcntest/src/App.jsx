import { useEffect, useState } from "react";
import "./App.css";
import { Routes, Route } from "react-router-dom";
import Homepage from "./components/Homepage";
import Chatbot_ui from "./pages/Chatbot_ui";
import { auth } from "./firebase_config";
import { useAuthState } from "react-firebase-hooks/auth";
import VoiceChat from "./pages/VoiceChat";

function App() {
  const [user, loading, error] = useAuthState(auth);
  return (
    <Routes>
      <Route
        path="/"
        element={<Homepage user={user} loading={loading} error={error} />}
      />
      <Route
        path="/ChatBot"
        element={<Chatbot_ui user={user} loading={loading} error={error} />}
      />

      <Route
        path="/voiceBot"
        element={<VoiceChat user={user} loading={loading} error={error} />}
      />
    </Routes>
  );
}

export default App;
