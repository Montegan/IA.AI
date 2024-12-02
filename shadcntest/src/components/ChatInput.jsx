import React, { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { db, auth } from "../firebase_config";
import {
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
  addDoc,
  serverTimestamp,
} from "firebase/firestore";
import { BsFillSendFill } from "react-icons/bs";
import axios from "axios";

const ChatInput = ({ currentTab }) => {
  const [userInput, setUserInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const currentuser = auth.currentUser.uid;
    // const send_ref = collection(db, currentuser);
    const send_ref = collection(
      db,
      "users",
      currentuser,
      "tab_id",
      currentTab,
      "messages"
    );
    await addDoc(send_ref, {
      userId: currentuser,
      human_message: userInput,
      created_at: serverTimestamp(),
    });

    const backendMessage = await axios.post(
      "http://127.0.0.1:5000/ragEndpoint",
      { prompt: userInput, currentuser: currentuser, currentTab: currentTab },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    console.log("message sent");
    console.log(backendMessage);
    setUserInput("");
  };
  return (
    <>
      <form onSubmit={handleSubmit} className="flex w-ful gap-2">
        <Input
          className="w-[43vw] "
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
        />
        <Button type="Submit" className="bg-[#00416B] ">
          <BsFillSendFill />
        </Button>
      </form>
    </>
  );
};

export default ChatInput;
