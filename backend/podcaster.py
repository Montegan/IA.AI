import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from google.cloud import texttospeech_v1beta1 as texttospeech
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI


load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\H00422003\\Desktop\\SFBU\\2ndsem\\GenAI\\fullstack_rag_sfbu\\complete_rag_app\\google_credentials.json"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI()


class question_format(BaseModel):
    question1: str
    question2: str


@app.get("/")
def main():
    return ("hello bot from fast")
# sample_prompt = "answer should be presented by creating two personas in a podcast studio that are talking answering the users questions as if they"
# @app.post("/question")
# def user_question(user_question: question_format):
#     print(user_question.question1)
#     # return web_loaders(user_question.question1)
#     response = llm.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "system", "content": " You are a helpful assistant and an expert in podcast content creation. Your task is to answer user questions in a conversational manner by creating a script featuring two personas, Lisa and James, who discuss the topic in a podcast setting. Ensure the dialogue is natural, engaging, and informative, suitable for text-to-speech agents to read aloud. do not include greeting and do not mention podcast in the script"},
#                   {"role": "user", "content": "we're diving into a fundamental topic for podcasters: RSS feeds. James, can you explain what an RSS feed is and why it's crucial for podcasters?"},
#                   {"role": "assistant", "content": "Absolutely, Lisa. An RSS feed, which stands for Really Simple Syndication, is essentially a web feed that allows users and applications to access updates to websites in a standardized, computer-readable format. For podcasters, it's the backbone of distributing episodes to various platforms."},
#                   {"role": "user", "content": "So, without an RSS feed, our podcast wouldn't appear on platforms like Apple Podcasts or Spotify?"},
#                   {"role": "assistant", "content": "Exactly. The RSS feed contains all the metadata about your podcast—episode titles, descriptions, audio file locations—and platforms use this information to display and update your content."},
#                   {"role": "user", "content": "Got it. So, ensuring our RSS feed is correctly set up and maintained is essential for reaching our audience."},
#                   {"role": "assistant",
#                       "content": "Precisely. It's the bridge between your content and your listeners."},
#                   {"role": "user", "content": f"what is the difference between {user_question.question1} and {user_question.question2}"}],
#     )

#     result = response.choices[0].message.content
#     speech_file_path = Path(__file__).parent / "speech.mp3"
#     response = llm.audio.speech.create(
#         model="tts-1",
#         voice="alloy",
#         input=f"{result}"
#     )

#     response.stream_to_file(speech_file_path)
#     return (result)


# [speaker="R",content"="we're diving into a fundamental topic for podcasters: RSS feeds. James, can you explain what an RSS feed is and why it's crucial for podcasters?",
#                   {"role": "assistant", "content": "Absolutely, Lisa. An RSS feed, which stands for Really Simple Syndication, is essentially a web feed that allows users and applications to access updates to websites in a standardized, computer-readable format. For podcasters, it's the backbone of distributing episodes to various platforms."},
#                   {"role": "user", "content": "So, without an RSS feed, our podcast wouldn't appear on platforms like Apple Podcasts or Spotify?"},
#                   {"role": "assistant", "content": "Exactly. The RSS feed contains all the metadata about your podcast—episode titles, descriptions, audio file locations—and platforms use this information to display and update your content."},
#                   {"role": "user", "content": "Got it. So, ensuring our RSS feed is correctly set up and maintained is essential for reaching our audience."},
#                   {"role": "assistant",
#                       "content": "Precisely. It's the bridge between your content and your listeners."},]


#  [
#     {
#         "content": "Hey, Sara, did you know the difference between cats and dogs?",
#         "speaker": "R"
#     },
#     {
#         "content": "Yes, Robert. Cats and dogs are both popular pets, but they have many differences.",
#         "speaker": "S"
#     },
#     {
#         "content": "For starters, cats are known for being more independent compared to dogs. They often prefer solitude and require less attention.",
#         "speaker": "S"
#     },
#     {
#         "content": "On the other hand, dogs are social animals that thrive on companionship and human interaction. They are often referred to as 'man's best friend.'",
#         "speaker": "S"
#     },
#     {
#         "content": "Cats are usually quieter and more reserved, while dogs tend to be more vocal and expressive through barking, whining, or howling.",
#         "speaker": "S"
#     },
#     {
#         "content": "Also, in terms of grooming, cats are generally more self-sufficient and spend a lot of time grooming themselves, whereas dogs may need regular baths and grooming sessions.",
#         "speaker": "S"
#     },
#     {
#         "content": "These are just a few of the many differences between cats and dogs, showcasing their unique characteristics and behaviors.",
#         "speaker": "S"
#     }
# ]


# Define a nested model for the content
class Content(BaseModel):
    content: str = Field(
        ...,
        description="The line a persona speaks in the conversation."
    )
    speaker: str = Field(
        ...,
        description="A single letter label, either 'R' for Rachel or 'S' for Simon, to distinguish each persona."
    )


class google_parser(BaseModel):
    result: List[Content] = Field(
        description=" list of conversations between personas")


@app.post("/question")
def google_adui(user_question: question_format, ):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()
    print(user_question)
    print(user_question.question1)
    llm_parser = PydanticOutputParser(pydantic_object=google_parser)
    format_instruction = llm_parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages([("system", " You are a helpful assistant and an expert in podcast content creation. Your task is to answer user questions in a conversational manner by creating a script featuring two personas, Rachel and Simon, who discuss the topic in a podcast setting. Ensure the dialogue is natural, engaging,goes back and forth, informative and suitable for text-to-speech agents to read aloud. do not mention podcast in the script.\n{format_instruction}"),
                                              ("user", "what is the difference between {question1} and {question2}")])

    # return web_loaders(user_question.question1)
    response = prompt | llm | llm_parser

    resutls = response.invoke(
        {"format_instruction": format_instruction, "question1": user_question.question1, "question2": {user_question.question2}})

    # print(resutls)
    # for item in resutls:
    #     multi_speaker_markup = texttospeech.MultiSpeakerMarkup(
    #         turns=[
    #             texttospeech.MultiSpeakerMarkup.Turn(
    #                 text=item.content,
    #                 speaker=item.speaker,
    #             ),]
    #     )
    print(resutls)
    speech_turns = []

    for i in resutls.result:
        script = texttospeech.MultiSpeakerMarkup.Turn(
            text=i.content,
            speaker=i.speaker
        )
        speech_turns.append(script)
        # result = [Content(content='Hey Robert, do you know the difference between being rich and poor?', speaker='S'), Content(content='Hey Sara, well, being rich generally means having an abundance of financial resources and assets, while being poor means lacking those resources.', speaker='R'), Content(
        #     content="That's true. Being rich often provides access to better education, healthcare, and living conditions, while those who are poor may struggle to meet their basic needs.", speaker='S'), Content(content='Absolutely, Sara. The difference in wealth can also affect opportunities, social status, and overall quality of life.', speaker='R')]

    # result = response.choices[0].message.content
    multi_speaker_markup = texttospeech.MultiSpeakerMarkup(
        turns=speech_turns
    )

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(
        multi_speaker_markup=multi_speaker_markup
    )

    # Build the voice request, select the language code ('en-US') and the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Studio-MultiSpeaker"
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        return ('Audio content written to file "output.mp3"')
