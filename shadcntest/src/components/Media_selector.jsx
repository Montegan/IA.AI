import React, { useState } from "react";
import { Button } from "./ui/button";
import axios from "axios";
import { CgWebsite } from "react-icons/cg";
import { FaYoutube } from "react-icons/fa";

const Media_selector = ({ mediaSelector, setMediaSelector }) => {
  const [file, setfile] = useState("");
  const [UploadStatus, setUploadStatus] = useState("");
  const [webUrl, setWebUrl] = useState("");
  const [youtubeUrl, setyoutubeUrl] = useState("");

  // Handle file upload
  const handleFileUpload = async () => {
    if (!file) {
      alert("Please select a file!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/load_db",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setUploadStatus(`${response.data.message}`);
    } catch (error) {
      setUploadStatus(
        `Error:${error.response ? error.response.data.error : error.message}`
      );
    }
  };

  const handleUrlUpload = async () => {
    if (webUrl != "") {
      const webResponse = await axios.post(
        "http://127.0.0.1:5000/load_web",
        {
          webUrl: webUrl,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setUploadStatus(webResponse.data.message);
      webResponse && setWebUrl("");
    }
  };

  const handleYoutubeUpload = async () => {
    if (youtubeUrl != "") {
      const webResponse = await axios.post(
        "http://127.0.0.1:5000//load_youtube",
        {
          webUrl: youtubeUrl,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setUploadStatus(webResponse.data.message);
      webResponse && setyoutubeUrl("");
    }
  };

  return (
    <>
      <div
        className={
          mediaSelector
            ? "bg-[#2d2d2d] fixed bottom-[5vh] left-[10vw] rounded-md shadow-[0px_0px_500px_150px_#000000] p-5  h-[90vh] w-[80vw] flex flex-col justify-center gap-8"
            : "hidden"
        }
      >
        {/* <div> */}
        <Button
          onClick={() => {
            setMediaSelector(!mediaSelector);
          }}
          className=" absolute h-8 w-3 rounded-full bg-[tomato] hover:bg-[#ee553b] text-black   top-[5px] right-[5px]"
        >
          X
        </Button>
        <div className=" w-[80%] min-h-11 ">
          <p
            className={
              UploadStatus
                ? "text-white w-fit transition-transform bg-green-600 p-2"
                : "hidden"
            }
          >
            {UploadStatus}
            {/* {setTimeout(() => {
            setUploadStatus("");
          }, 2000)} */}
          </p>
        </div>

        <div className=" bg-[#4b4b4b96] p-4 flex gap-2 rounded-md items-center justify-start w-full">
          <label
            htmlFor="file_upload"
            className="flex flex-col items-center justify-center w-[92%] max-w-[92%] h-40 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 border-gray-300 hover:bg-gray-100"
          >
            <div className="flex flex-col  items-center justify-center pt-5 pb-6">
              {file ? (
                file.name
              ) : (
                <>
                  <p className="text-xl text-gray-500">
                    pdf, xlsx, docs, ppts, csv, txt
                  </p>
                  <br />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or
                    drag and drop
                  </p>
                </>
              )}
            </div>

            <input
              id="file_upload"
              type="file"
              className="hidden"
              onChange={(e) => {
                setfile(e.target.files[0]);
                console.log(e.target.files[0]);
              }}
            />
          </label>
          {file && (
            <Button
              className="self-end w-fit bg-[#00416B]"
              onClick={handleFileUpload}
            >
              Upload
            </Button>
          )}
        </div>

        <div className=" bg-[#4b4b4b96] text-white flex flex-col gap-2 rounded-md p-2">
          <label htmlFor="Youtube">
            <FaYoutube color="red" size={25} />
          </label>
          <div className="w-full flex gap-2 ">
            <input
              id="Youtube"
              type="text"
              className="w-full p-1 pl-2 text-black rounded-md"
              placeholder="Youtube link here"
              value={youtubeUrl}
              onChange={(e) => setyoutubeUrl(e.target.value)}
            />
            <Button
              className="w-fit bg-[#00416B]"
              onClick={handleYoutubeUpload}
            >
              Upload
            </Button>
          </div>
        </div>

        <div className=" bg-[#4b4b4b96] flex text-white gap-2 flex-col rounded-md p-2">
          <label htmlFor="WebLink">
            <CgWebsite size={25} />
          </label>
          <div className="w-full flex gap-2 ">
            <input
              id="WebLink"
              className="w-full text-black p-1 pl-2 rounded-md"
              type="text"
              placeholder="website link here"
              value={webUrl}
              onChange={(e) => setWebUrl(e.target.value)}
            />
            <Button className="w-fit bg-[#00416B]" onClick={handleUrlUpload}>
              Upload
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Media_selector;
