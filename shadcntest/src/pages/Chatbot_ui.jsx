import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { signOut } from "firebase/auth";
import { auth, db } from "../firebase_config.js";
import { useFetcher, useNavigate } from "react-router-dom";
import Message_load from "@/components/Message_load.jsx";
import { CgAttachment } from "react-icons/cg";
import { BsFillSendFill } from "react-icons/bs";
import { IoMdAddCircle } from "react-icons/io";

import { CiLogout } from "react-icons/ci";

import {
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
  addDoc,
  serverTimestamp,
} from "firebase/firestore";
import ChatInput from "@/components/ChatInput.jsx";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Media_selector from "@/components/Media_selector.jsx";

const Chatbot_ui = ({ user, loading, error }) => {
  const [messages, setMessages] = useState([]);
  const [tabs, setTabs] = useState([]);
  const [currentTab, setCurrentTab] = useState("");
  const [mediaSelector, setMediaSelector] = useState(false);

  const navigate = useNavigate();
  const handdle_logout = async () => {
    const signed_out = await signOut(auth);
    console.log(user.proactiveRefresh.isRunning);
    console.log(signed_out);
    navigate("/");
  };

  // Navigate to /ChatBot if the user is logged in
  useEffect(() => {
    if (user == null) {
      navigate("/");
    }
    console.log(user);
  }, [user, navigate]);

  useEffect(() => {
    if (user) {
      const current_user = auth.currentUser?.uid;
      // const collection_ref = collection(db, "users", current_user, "messages");
      // const q = query(collection_ref, orderBy("created_at"), limit(50));
      // const unsubscribeMessages = onSnapshot(q, (snapshot) => {
      //   setMessages(snapshot.docs.map((doc) => doc.data()));
      //   console.log(snapshot.docs.map((doc) => doc.data()));
      // });

      const collection_tab = collection(db, "owner", current_user, "tabs");
      const tabs_query = query(
        collection_tab,
        orderBy("created_at", "desc"),
        limit(50)
      );
      const unsubscribeTabs = onSnapshot(tabs_query, (snapshot) => {
        setTabs(snapshot.docs.map((doc) => doc.id));
        console.log(snapshot.docs.map((doc) => doc.id));
      });

      console.log(currentTab);
      console.log(user);
      return () => {
        unsubscribeTabs();
      };
    }
  }, []);

  const handleTabCreate = async (e) => {
    const current_user = auth.currentUser?.uid;
    const collection_ref = collection(db, "owner", current_user, "tabs");
    const q = await addDoc(collection_ref, {
      user_id: current_user,
      created_at: serverTimestamp(),
    });
    setCurrentTab(q.id);
    const tabs_query = query(collection_ref, orderBy("created_at"), limit(50));
    onSnapshot(tabs_query, (snapshot) => {
      setTabs(snapshot.docs.map((doc) => doc.id));
      console.log(snapshot.docs.map((doc) => doc.id));
    });

    // const unsubscribe = onSnapshot(q, (snapshot) => {
    //   setMessages(snapshot.docs.map((doc) => doc.data()));
    //   console.log(snapshot.docs.map((doc) => doc.data()));
    // });
    handeActiveTab(q.id);
    console.log(q.id);
  };

  const handeActiveTab = (active_id) => {
    const current_user = auth.currentUser?.uid;
    const active_tab = active_id;
    const send_ref = collection(
      db,
      "users",
      current_user,
      "tab_id",
      active_tab,
      "messages"
    );
    // //const collection_ref = collection(db, "owner", current_user, "tabs");
    // const q = await addDoc(send_ref, {
    //   user_id: current_user,
    //   created_at: serverTimestamp(),
    // });
    const tabs_query = query(send_ref, orderBy("created_at"), limit(50));
    onSnapshot(tabs_query, (snapshot) => {
      setMessages(snapshot.docs.map((doc) => doc.data()));
      console.log(snapshot.docs.map((doc) => doc.id));
    });
    // const unsubscribe = onSnapshot(q, (snapshot) => {
    //   setMessages(snapshot.docs.map((doc) => doc.data()));
    //   console.log(snapshot.docs.map((doc) => doc.data()));
    // });
    // console.log(q.id);
  };

  const handleAttach = () => {
    console.log("attach button clicked");
  };

  return (
    <div className="flex p-0 m-0 ">
      {loading ? (
        <h1>Please wait page loading</h1>
      ) : (
        <>
          {error ? (
            <h1>Ecountered error while loging in </h1>
          ) : (
            <>
              <Card className=" h-[100vh] relative w-[20vw] max-w-[20vw] bg-[#171717] rounded-none items-center border-none overflow-y-scroll [scrollbar-width:none] [-ms-overflow-style:none] flex flex-col gap-2">
                <div className="flex w-[20vw] max-w-[20vw] items-center p-2  border-b-[1px] mb-2 gap-3">
                  <Avatar>
                    <AvatarImage src={user.photoURL} alt="profile" />
                    <AvatarFallback>Profile</AvatarFallback>
                  </Avatar>
                  <h1 className="text-white p-3">{user && user.displayName}</h1>
                </div>
                <Button
                  id="button1"
                  className=" w-[260px] mb-2 max-w-[260px] bg-[#87878747]"
                  onClick={(e) => handleTabCreate(e)}
                >
                  <IoMdAddCircle /> New
                </Button>
                <div className=" h-[80vh] rounded-full w-[260px] max-w-[260px] flex flex-col gap-2">
                  {tabs.map((tab) => (
                    <Button
                      id={tab}
                      className="max-w-[260px] bg-[#00416B]"
                      onClick={(e) => {
                        setCurrentTab(e.target.id);
                        handeActiveTab(e.target.id);
                        console.log("current tab is" + e.target.id);
                      }}
                    >
                      {tab}
                    </Button>
                  ))}
                </div>

                <Button
                  onClick={handdle_logout}
                  className="fixed bottom-0 bg-[tomato] text-black font-extrabold text-9xl w-[20vw] max-w-full"
                >
                  <CiLogout />
                </Button>
              </Card>
              <Card className=" h-[100vh] w-[80vw] bg-[#212121] flex gap-3 flex-col items-center rounded-none border-none pt-2 ">
                <Card className="relative h-[90vh] w-[73vw] overflow-y-scroll overflow-x-hidden [scrollbar-width:none] [-ms-overflow-style:none] rounded-none flex flex-col   gap-10 bg-[#212121] border-none">
                  {tabs.length > 0 && currentTab != "" ? (
                    messages.map((items) => <Message_load items={items} />)
                  ) : (
                    <Button
                      id="button1"
                      className="absolute top-[40vh] bg-[#00416B] left-[28vw]"
                      onClick={(e) => handleTabCreate(e)}
                    >
                      Create New Tab
                    </Button>
                  )}

                  <Media_selector
                    setMediaSelector={setMediaSelector}
                    mediaSelector={mediaSelector}
                  />
                </Card>

                {currentTab != "" && (
                  <div className="flex gap-2">
                    <Button
                      className="bg-[#00416B] w-[80px]"
                      onClick={() => {
                        setMediaSelector(!mediaSelector);
                      }}
                    >
                      <CgAttachment />
                    </Button>
                    <ChatInput currentTab={currentTab} />
                  </div>
                )}
              </Card>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Chatbot_ui;
