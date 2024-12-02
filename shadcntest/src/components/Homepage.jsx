import React, { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { auth, provider } from "@/firebase_config";
import { signInWithPopup, signOut } from "firebase/auth";
import { Button } from "./ui/button";
import bg_image from "../assets/ai_head.webp";
import { FcGoogle } from "react-icons/fc";

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
        <div className="h-[100vh] w-[100vw] display flex items-center   justify-center bg-gradient-to-r from-[#2b272f] to-[#161d15]">
          <div className="h-[85vh] w-[42vw] object-contain bg-slate-400 rounded-tl-2xl rounded-bl-2xl">
            <img
              src={bg_image}
              className=" h-full w-full rounded-tl-2xl rounded-bl-2xl"
              alt="ai"
            />
          </div>
          <div className="h-[85vh] w-[42vw] bg-slate-500 flex flex-col items-center justify-center gap-[50px] rounded-tr-2xl rounded-br-2xl bg-clip-padding backdrop-filter backdrop-blur-3xl bg-opacity-20 ">
            <h1 className="text-[4rem] font-merriweather font-extrabold text-green-600">
              Welcome to IA.AI
            </h1>
            <button
              onClick={signinUser}
              className="bg-white p-1 text-lg flex items-center justify-center gap-2 text-nowrap rounded-xl w-[340px]"
            >
              <span>SIGN IN WITH</span>
              <FcGoogle size="40px" />
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Homepage;
