import { useEffect, useRef, useState } from "react";
import axios from "axios";
import logo_image from "../assets/SFBU_Logo.png";
import { Avatar } from "../components/ui/avatar";
import { AvatarFallback, AvatarImage } from "@radix-ui/react-avatar";
import { useNavigate } from "react-router-dom";
import { BsChatLeftTextFill } from "react-icons/bs";
import { MdEmail } from "react-icons/md";
import { FaPodcast } from "react-icons/fa6";

function VoiceChat() {
  const [status, setStatus] = useState("");
  const [clicked, setClicked] = useState(false);
  const send_mess = async () => {
    setClicked(!clicked);
    console.log(clicked);
    const item = await axios.post("http://127.0.0.1:5000/vtv", {
      clicked: clicked,
    });
    console.log(item);
    setStatus(item.data);
  };
  const audio_ref = useRef(null);
  const navigate = useNavigate();
  return (
    <div className="bg-[#00416B] relative h-[100vh] flex flex-col p-3 justify-start items-center  ">
      <div className="relative min-h-[35px] flex gap-16 items-center w-full">
        <BsChatLeftTextFill
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/ChatBot")}
        />

        <MdEmail
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/emailBot")}
        />
        <FaPodcast
          className="text-[#b0b0b0] hover:text-[#d4d4d4]"
          size={23}
          onClick={() => navigate("/podcast")}
        />
      </div>

      <h1 className="text-[3rem] font-bold text-[#BC955c] mt-[50px]">
        SFBU VOICE
      </h1>
      <Avatar
        className={
          clicked
            ? "h-[200px] w-[200px] animate-pulse mt-[100px]"
            : "mt-[100px] h-[200px] w-[200px]"
        }
        htmlFor="player_icon"
      >
        <AvatarImage
          className="h-[200px] w-[200px]"
          src={logo_image}
          onClick={send_mess}
        />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
      <span className="mt-[10px] opacity-45 text-slate-300">
        CLick Logo to speak
      </span>
      {/* <audio
        id="player_icon"
        className="hidden"
        src={sound}
        controls
        autoPlay
        ref={audio_ref}
      ></audio> */}
    </div>
  );
}

export default VoiceChat;

// useEffect(() => {
//   // console.log(audio_ref.ended);
//   // if (audio_ref.ended) {
//   //   console.log("audio finished playing ");
//   // }
//   setStatus(audio_ref.current.currentTime);
//   console.log(audio_ref);
// }, [status]);

// const send_mess = () => {
//   console.log("clicked talk button");
// };
