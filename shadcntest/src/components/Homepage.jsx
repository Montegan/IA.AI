import React, { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { auth, provider } from "@/firebase_config";
import { signInWithPopup, signOut } from "firebase/auth";
import { Button } from "./ui/button";

const Homepage = ({ user, loading, error }) => {
  const navigate = useNavigate();
  const signinUser = () => {
    signInWithPopup(auth, provider).then((data) => {
      console.log(data);
      navigate("/ChatBot");
    });
  };

  // Navigate to /ChatBot if the user is logged in
  useEffect(() => {
    if (user) {
      navigate("/ChatBot");
    }
  }, [user, navigate]);

  return (
    <>
      {loading ? (
        <h1>Loading</h1>
      ) : (
        <div className="h-[100vh] w-[100vw] display flex flex-col gap-4 items-center justify-center bg-green-200">
          <div>Welcome to you IA.AI</div>
          <Button variant="outline" onClick={signinUser}>
            SIGN IN with goole
          </Button>
        </div>
      )}
    </>
  );
};

export default Homepage;
