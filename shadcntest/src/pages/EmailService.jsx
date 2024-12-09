import React, { useEffect, useState } from "react";
import axios from "axios";
import { MdGTranslate } from "react-icons/md";
import { RiUserVoiceFill } from "react-icons/ri";
import { FaPodcast } from "react-icons/fa6";
import { BsChatLeftTextFill } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

const EmailService = () => {
  const [originalComment, setOriginalComment] = useState("");
  const [commentSummary, setCommentSummary] = useState("");
  const [sentiment, setSentiment] = useState("");
  const [language, setLanguage] = useState("");
  const [email, setEmail] = useState("");
  const [sentAlert, setAlert] = useState("");
  const [subject, setSubject] = useState("");
  const [reciverAddress, setreciverAddress] = useState("");
  const [attachement, setAttachment] = useState("");

  const generateComment = async () => {
    const response = await axios.get(" http://127.0.0.1:5000/originalComment");
    setOriginalComment(response.data.messages);
  };

  const navigate = useNavigate();

  const generateEmail = async () => {
    const response = await axios.post(" http://127.0.0.1:5000/composeEmail", {
      language: language,
      comment: originalComment,
    });
    setEmail(response.data.email);
    setSubject(response.data.subject);
  };
  useEffect(() => {
    if (sentAlert !== "") {
      const timeout = setTimeout(() => {
        setAlert("");
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [sentAlert]);

  const sendEmail = async () => {
    console.log(email);
    console.log(subject);
    console.log(reciverAddress);
    const formData = new FormData();
    formData.append("file", attachement);
    formData.append("final_email", email);
    formData.append("subject", subject);
    formData.append("reciver", reciverAddress);

    const response = await axios.post(
      "http://127.0.0.1:5000/sendmail",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    setAlert(response.data);
  };

  const handleAttachement = async () => {};

  return (
    <div className="text-white bg-black flex flex-col items-center h-[100vh] gap-6 w-full pt-6 px-4">
      <div className="relative min-h-[35px] flex gap-16 items-center w-full">
        <BsChatLeftTextFill
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/ChatBot")}
        />
        <RiUserVoiceFill
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/voiceBot")}
        />
        <FaPodcast
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/podcast")}
        />
        <span
          className={
            sentAlert != ""
              ? " fixed top-3 right-[45vw] text-black bg-green-500 p-1 rounded-md "
              : "hidden"
          }
        >
          {sentAlert}
        </span>
      </div>

      <div className="grid max-sm:grid-cols-1  grid-cols-12 w-full gap-2 h-fit">
        <div className="h-fit min-h-[82vh]  pt-2 col-span-5 flex items-center flex-col ">
          <div className=" h-full min-h-[80vh] justify-end  w-full flex gap-2 flex-col">
            <label
              htmlFor="Original_Comment"
              className="font-title font-bold opacity-35 text-left text-[1rem]"
            >
              Playground
            </label>
            <textarea
              name="Original_Comment"
              placeholder="Start here ..."
              id="Original_Comment"
              className=" h-full min-h-[72vh] w-full p-3 text-[1.1rem] focus:outline-none rounded-xl bg-[#191A23]"
              value={originalComment}
              onChange={(e) => {
                setOriginalComment(e.target.value);
                console.log(e.target.value);
              }}
            ></textarea>

            <button
              onClick={generateEmail}
              className="bg-green-50 self-center hover:bg-slate-300 active:bg-slate-400 p-2 text-black text-lg font-bold w-[25vw] rounded-md"
            >
              Generate Email
            </button>
          </div>
        </div>

        <div className="flex flex-col  justify-center h-fit col-span-7 gap-1">
          <div className="flex justify-between items-center w-full">
            <span
              htmlFor="customer_email"
              className="font-title font-bold text-left opacity-35 text-[1rem]"
            >
              Email
            </span>
            <div className="rounded-xl p-1 self-end  flex  w-fit">
              <label htmlFor="language" className="font-title text-[1.3rem] ">
                <MdGTranslate className="text-slate-300 text-[1.6rem] hover:text-[#cacaca] " />
              </label>
              <select
                name="language"
                id="language"
                className=" focus:outline-none ml-3 text-slate-300 border-b-2 bg-transparent border-slate-400 w-[8vw]"
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
              </select>
            </div>
          </div>

          <div className="h-fit flex flex-col  gap-2 min-h-[82vh] w-full">
            <div className="flex  items-center  gap-2 pr-2">
              {/* <label htmlFor="emailSubject" className="w-16 text-right">
                To
              </label> */}
              <input
                id="emailSubject"
                type="text"
                placeholder="To:"
                className=" h-fit w-full p-2 text-[1rem] focus:outline-none rounded-lg bg-[#191A23]"
                value={reciverAddress}
                onChange={(e) => setreciverAddress(e.target.value)}
              />
            </div>
            <div className="flex  items-center gap-2 pr-2">
              {/* <label
                htmlFor="emailSubject"
                className="w-16 text-right bg-black"
              >
                Subject
              </label> */}
              <input
                id="emailSubject"
                placeholder="Subject:"
                type="text"
                className=" h-fit w-full p-2 text-[1rem] focus:outline-none rounded-xl bg-[#191A23]"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
            <div className=" flex flex-col gap-2 ">
              <textarea
                name="customer_email"
                placeholder="Draft:"
                id="customer_email"
                className="h-fit min-h-[58vh] w-full p-3 text-[0.9rem] focus:outline-none rounded-xl bg-[#191A23]"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  console.log(e.target.value);
                }}
              ></textarea>
              <div>
                <input
                  type="file"
                  onChange={(e) => setAttachment(e.target.files[0])}
                />
                <button
                  onClick={sendEmail}
                  className="bg-green-500 self-center hover:bg-green-400 active:bg-green-600 p-[8px] text-black text-lg font-bold w-[25vw] rounded-md"
                >
                  Send Email
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailService;
