import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { BsChatLeftTextFill } from "react-icons/bs";
import { MdEmail } from "react-icons/md";
import { RiUserVoiceFill } from "react-icons/ri";
import { useNavigate } from "react-router-dom";
import song from "../../../backend/output.mp3";
import path from "path";
const Podcast = () => {
  const navigate = useNavigate();
  const [user_question, setUserQuestion] = useState("");
  const [audioPath, setAudiopath] = useState("");
  const [status, setStatus] = useState(true);

  const [llm_response, setResponse] = useState();

  const playAudio = async () => {
    const item = await axios.post("http://127.0.0.1:5000/player", {
      status: status,
    });
    setStatus(!status);
    console.log(item.data);
  };

  const post_message = async () => {
    const item = await axios.post("http://127.0.0.1:5000/podcast", {
      question: user_question,
    });
    console.log(item.data.message);
    setResponse(item.data.message);
    setUserQuestion("");
  };

  // const audioRef = useRef(null);

  useEffect(() => {
    const music_path = `${import.meta.env.VITE_BASE_URL}backend\\output.mp3`;
    console.log(music_path);
    setAudiopath(music_path);
    // if (audioRef.current) {

    //   audioRef.current.pause(); // Pause currently playing song
    //   console.log(audioRef.current);
    // }
    // audioRef.current = new Audio(song);
  }, [llm_response]);

  useEffect(() => {
    if (llm_response !== "") {
      const timeout = setTimeout(() => {
        setResponse("");
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [llm_response]);

  return (
    <div className="bg-gradient-to-b from-black to-gray-900 min-h-screen w-full text-white">
      {/* Navigation Icons */}
      <div className="flex  gap-10  px-4 py-4 ">
        {[
          { icon: BsChatLeftTextFill, link: "/ChatBot" },
          { icon: RiUserVoiceFill, link: "/voiceBot" },
          { icon: MdEmail, link: "/emailbot" },
        ].map(({ icon: Icon, link }, idx) => (
          <Icon
            key={idx}
            className="text-gray-400 hover:text-white transition duration-200 cursor-pointer"
            size={25}
            onClick={() => navigate(link)}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center text-white py-10 space-y-6">
        <h1 className="text-3xl font-bold">SFBU Podcast</h1>
        <p className="text-lg italic opacity-75">{llm_response}</p>

        {/* Question Form */}
        <div className="bg-gray-800 p-6 rounded-lg w-[60%]">
          <label htmlFor="question1" className="block text-sm mb-2">
            Ask a Question
          </label>
          <input
            id="question1"
            type="text"
            value={user_question}
            onChange={(e) => setUserQuestion(e.target.value)}
            className="w-full p-3 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Type your question..."
          />
        </div>

        {/* Audio Player */}
        <div className=" flex mt-10 gap-5">
          {/* <audio
            src={audioPath}
            className={audioPath ? " rounded-lg shadow-lg " : "hidden"}
            controls
            ref={audioRef}
          /> */}
          <button
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 w-[100px] h-[45px] rounded-xl font-medium transition duration-200"
            onClick={post_message}
          >
            Submit
          </button>

          <button
            className="bg-[#00406b98] hover:bg-[#00416B] w-[100px] h-[45px] rounded-xl"
            onClick={() => {
              playAudio();
            }}
          >
            {status ? "Play" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Podcast;

{
  /* <div className="bg-black h-full min-h-[100vh] w-full">
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
        <MdEmail
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/emailbot")}
        />
      </div>

      <div className=" flex flex-col items-center justify-center gap-5">
        <h1>Welcome Chat..</h1>
        <p>{llm_response}</p>
        <p>{llm_response}</p>

        <div className=" text-black bg-green-200  flex flex-col gap-3 p-3 w-[50vw]">
          <label htmlFor="question1">Question</label>
          <input
            id="question1"
            type="text"
            value={user_question}
            onChange={(e) => setUserQuestion(e.target.value)}
          />
        </div>
        <button className="bg-green-400 p-3" onClick={post_message}>
          clicked
        </button>
        <br />
        <br />
        <audio src={song} controls />

        <h1>read the content</h1>
      </div>
    </div>
  ); */
}
