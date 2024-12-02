import React, { useState } from "react";
import { Button } from "./ui/button";
import axios from "axios";
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

  return (
    <>
      <div
        className={
          mediaSelector
            ? "bg-[#2d2d2d] fixed bottom-[10vh] left-[10vw] rounded-md shadow-[0px_0px_500px_150px_#000000] p-10  h-[80vh] w-[80vw] flex flex-col justify-center gap-8"
            : "hidden"
        }
      >
        {/* <div> */}
        <Button
          onClick={() => {
            setMediaSelector(!mediaSelector);
          }}
          className=" absolute h-8 w-6 rounded-full bg-[#00416B]  top-[0] right-[0]"
        >
          X
        </Button>
        <div className="flex items-center justify-center w-full">
          <label
            htmlFor="file_upload"
            className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 border-gray-300 hover:bg-gray-100"
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {file ? (
                file.name
              ) : (
                <>
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or
                    drag and drop
                  </p>
                  <p className="text-lg text-gray-500">PDF (MAX. 5MB)</p>
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
          <h1 className="text-white">{UploadStatus && UploadStatus}</h1>
          {file && <Button onClick={handleFileUpload}>Upload</Button>}
        </div>

        <div className=" bg-[#4b4b4b96] text-white flex flex-col gap-2 rounded-md p-2">
          <label htmlFor="Youtube">Youtube:</label>
          <input id="Youtube" type="text" className="w-full p-1 rounded-md" />
          <Button className="w-fit bg-[#00416B]">Upload</Button>
        </div>

        <div className=" bg-[#4b4b4b96] flex text-white gap-2 flex-col rounded-md p-2">
          <label htmlFor="WebLink">Website:</label>
          <input id="WebLink" className="w-full p-1 rounded-md" type="text" />
          <Button className="w-fit bg-[#00416B]">Upload</Button>
        </div>
      </div>
    </>
  );
};

export default Media_selector;
