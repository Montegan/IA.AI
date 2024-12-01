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
    console.log("message sent");
    setUserInput("");
  };
  return (
    <>
      <form action="" onSubmit={handleSubmit} className="flex w-ful gap-2">
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
