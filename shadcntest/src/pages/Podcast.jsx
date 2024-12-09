import React from "react";
import { BsChatLeftTextFill } from "react-icons/bs";
import { MdEmail } from "react-icons/md";
import { RiUserVoiceFill } from "react-icons/ri";
import { useNavigate } from "react-router-dom";

const Podcast = () => {
  const navigate = useNavigate();
  return (
    <div>
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
    </div>
  );
};

export default Podcast;
