import React, { useEffect, useRef, useState } from "react";
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
import { FaMicrophone } from "react-icons/fa";
import { MdGTranslate } from "react-icons/md";
import { RiUserVoiceFill } from "react-icons/ri";

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
import axios from "axios";
import Loading from "@/components/Loading.jsx";

const Chatbot_ui = ({ user, loading, error }) => {
  const [messages, setMessages] = useState([]);
  const [tabs, setTabs] = useState([]);
  const [currentTab, setCurrentTab] = useState("");
  const [mediaSelector, setMediaSelector] = useState(false);
  const [Micon, setMicon] = useState(false);
  const [language, setLanguage] = useState("English");

  const navigate = useNavigate();
  const chatEndRef = useRef(null);
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
    const tabs_query = query(
      collection_ref,
      orderBy("created_at", "desc"),
      limit(50)
    );
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

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Trigger when messages update

  const handleAudio = async () => {
    console.log(Micon);
    const currentuser = auth.currentUser.uid;
    const backendMessage = await axios.post(
      "http://127.0.0.1:5000/process_audio",
      { currentuser: currentuser, currentTab: currentTab },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    backendMessage && setMicon(false);

    console.log(backendMessage.data.data);
    const recorded_text = backendMessage.data.data;
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
      human_message: recorded_text,
      created_at: serverTimestamp(),
    });
  };

  return (
    <div className="flex p-0 m-0 ">
      {loading ? (
        <Loading />
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
                <div className=" h-[80vh]  w-[260px] overflow-y-scroll [scrollbar-width:none] [-ms-overflow-style:none] max-w-[260px] flex flex-col gap-2">
                  {tabs.map((tab) => (
                    <Button
                      id={tab}
                      className="max-w-[260px] bg-[#41525e2e] focus:bg-[#26516e] "
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
                {currentTab != "" && (
                  <div className="flex h-[60px] border-b-2 border-opacity-10 border-gray-300 w-[73vw] items-center justify-between  px-2 pb-2 gap-2">
                    <div
                      className="cursor-pointer"
                      onClick={() => {
                        navigate("/voiceBot");
                      }}
                    >
                      <RiUserVoiceFill size="30" className="text-[#afafaf]" />
                    </div>
                    <div className=" p-1  w-[250px] flex items-center ">
                      <label htmlFor="language">
                        <MdGTranslate className="text-gray-100 text-[2rem] opacity-40" />
                      </label>
                      <select
                        name="language"
                        id="language"
                        className="rounded-lg focus:outline-none ml-3 bg-slate-300   text-black p-1 w-[10vw]"
                        value={language}
                        onChange={(e) => {
                          setLanguage(e.target.value);
                          console.log(e.target.value);
                        }}
                      >
                        <option value="English">English</option>
                        <option value="Spanish">Spanish</option>
                        <option value="Chinese">Chinese</option>
                        <option value="Tagalog">Tagalog</option>
                        <option value="Vietnamese">Vietnamese</option>
                        <option value="Arabic">Arabic</option>
                        <option value="French">French</option>
                        <option value="Albanian">Albanian</option>
                        <option value="Armenian">Armenian</option>
                        <option value="Azerbaijani">Azerbaijani</option>
                        <option value="Belarusian">Belarusian</option>
                        <option value="Bengali">Bengali</option>
                        <option value="Bosnian">Bosnian</option>
                        <option value="Brazilian Portuguese">
                          Brazilian Portuguese
                        </option>
                        <option value="Bulgarian">Bulgarian</option>
                        <option value="Catalan">Catalan</option>
                        <option value="Croatian">Croatian</option>
                        <option value="Czech">Czech</option>
                        <option value="Danish">Danish</option>
                        <option value="Dutch">Dutch</option>
                        <option value="Estonian">Estonian</option>
                        <option value="Finnish">Finnish</option>
                        <option value="Galician">Galician</option>
                        <option value="Georgian">Georgian</option>
                        <option value="German">German</option>
                        <option value="Greek">Greek</option>
                        <option value="Gujarati">Gujarati</option>
                        <option value="Hindi">Hindi</option>
                        <option value="Hungarian">Hungarian</option>
                        <option value="Indonesian">Indonesian</option>
                        <option value="Irish">Irish</option>
                        <option value="Italian">Italian</option>
                        <option value="Japanese">Japanese</option>
                        <option value="Korean">Korean</option>
                        <option value="Latvian">Latvian</option>
                        <option value="Lithuanian">Lithuanian</option>
                        <option value="Macedonian">Macedonian</option>
                        <option value="Malay">Malay</option>
                        <option value="Maltese">Maltese</option>
                        <option value="Mandarin Chinese">
                          Mandarin Chinese
                        </option>
                        <option value="Marathi">Marathi</option>
                        <option value="Moldovan">Moldovan</option>
                        <option value="Mongolian">Mongolian</option>
                        <option value="Montenegrin">Montenegrin</option>
                        <option value="Nepali">Nepali</option>
                        <option value="Norwegian">Norwegian</option>
                        <option value="Pashto">Pashto</option>
                        <option value="Persian (Farsi)">Persian (Farsi)</option>
                        <option value="Polish">Polish</option>
                        <option value="Portuguese">Portuguese</option>
                        <option value="Punjabi">Punjabi</option>
                        <option value="Romanian">Romanian</option>
                        <option value="Russian">Russian</option>
                        <option value="Serbian">Serbian</option>
                        <option value="Sinhala">Sinhala</option>
                        <option value="Slovak">Slovak</option>
                        <option value="Slovene">Slovene</option>
                        <option value="Ukrainian">Ukrainian</option>
                        <option value="Urdu">Urdu</option>
                        <option value="Uzbek">Uzbek</option>
                        <option value="Vietnamese">Vietnamese</option>
                        <option value="Welsh">Welsh</option>
                      </select>
                    </div>
                  </div>
                )}
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
                  <div ref={chatEndRef}></div>
                </Card>

                {currentTab != "" && (
                  <div className="flex w-[73vw] items-center justify-center gap-2">
                    <button
                      className=" bg-[#00406b98] hover:bg-[#00416B] h-10 w-[100px] text-white rounded-lg flex items-center justify-center"
                      onClick={() => {
                        setMediaSelector(!mediaSelector);
                      }}
                    >
                      <CgAttachment />
                    </button>
                    <Button
                      onClick={() => {
                        setMicon(!Micon);
                        console.log(Micon);
                        handleAudio();
                      }}
                      className={
                        Micon
                          ? "text-red-500 w-[100px] "
                          : "bg-[#00406b98] hover:bg-[#00416B] w-[100px] text-white"
                      }
                    >
                      <FaMicrophone />
                    </Button>
                    <ChatInput currentTab={currentTab} language={language} />
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
