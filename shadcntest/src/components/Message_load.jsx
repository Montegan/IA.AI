import React, { useEffect } from "react";

const Message_load = ({ items }) => {
  return (
    <>
      {items.human_message && (
        <p
          key={items.human_message}
          className=" self-end p-3 w-fit max-w-[550px] bg-[#323232] rounded-xl text-white text-wrap"
        >
          {items.human_message}
        </p>
      )}
      {items.ai_message && (
        <p
          key={items.ai_message}
          className=" text-white bg-[#3b3b3b23] rounded-xl self-start p-3 w-fit max-w-[500px] text-wrap"
        >
          {items.ai_message}
        </p>
      )}
    </>
  );
};

export default Message_load;
