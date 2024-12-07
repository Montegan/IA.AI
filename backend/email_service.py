from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

client = OpenAI()

stringparser = StrOutputParser()


def compose_email(draft, language):
    subject = create_subject(draft)
    summary = summarize_summary(draft)
    sentiment = get_sentiment(draft)
    system_prompt = """ You are a helpfull Ai assistant for san francisco bay university employee's. Your job is to compose an email based on the provided draft. the subject is also provided below delimitted by dollar sign and the sentiment of the draft delimitted by hastags.subject:${subject}$ , sentiment: #{sentiment}#. the output should be in the provided language below language :$${language}$$, The generated email should only contain the body of the email. avoid placeholders or lables in the final email."""
    assistant_response = """Hi Simon,
I hope this email finds you well. I wanted to take a moment to thank you for your time during the interview process. Your insights and expertise were greatly appreciated and I thoroughly enjoyed our conversation. Your passion for the role and the company was evident and it left a positive impression on me.
I would also like to commend the professionalism and hospitality of the entire interview panel. It was a pleasure meeting everyone and I was impressed by the warm and welcoming environment of San Francisco Bay University.
Overall, my experience during the interview was very positive and I am excited about the potential opportunity to join your team. I look forward to hearing back from you soon.
Thank you again for your time and consideration.
Best regards,"""
    mail_prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "hi simon how was your interview can you tell me a little about it."), ("assistant", assistant_response), ("user", draft)])
    email_chain = mail_prompt | client | stringparser

    final_email = email_chain.invoke(
        {"draft": draft, "language": language, "sentiment": sentiment, "subject": subject})
    return {"email": final_email, "summary": summary, "sentiment": sentiment, "subject": subject}

# return {"email": final_email, "summary": summary, "sentiment": sentiment, "subject": subject}
# and company information to be in the footer are the following : % name: Jeff Bezos, position: Manager ,contact: +1 925-22122-212, company name: Emax electronics
# {"role": "user", "content": "ask simon how his interview went with facebook and what his thoughts was on the overall interview process .be concise"},
#         {"role": "assistant", "content": """ Hi Simon,
# I hope this message finds you well! I wanted to check in and see how your interview with Facebook went. What were your thoughts on the overall interview process?
# Looking forward to hearing from you!
# Best,  """}


def create_subject(draft):
    subject_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are expert in email subject writing. your job is to create a potential subject for an email based on the draft provided for San Francisco Bay University employees . the output should be only the subject no additional label is needed"),
        ("user", "{draft}")])

    subject_chain = subject_prompt | client | stringparser
    final_subject = subject_chain.invoke(draft)

    return final_subject
# response = client.chat.completions.create(model="gpt-4o-mini", messages=[
#                                               {"role": "system", "content": "You are a helpfull ai Assistant for san francisco bay university emplyee's that creates a potential subject for an email based on the darft provided by the user"}, {"role": "user", "content": f"{draft}"}])
#     email_subject = response.choices[0].message.content


def get_sentiment(draft):
    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant for San Francisco Bay University employees that extracts the sentiment of a draft email. Give a single word response as positive or negative."),
        ("user", "{draft}")
    ])

    sentiment_chain = sentiment_prompt | client | stringparser
    final_sentiment = sentiment_chain.invoke(draft)

    return final_sentiment
    # response = client.chat.completions.create(model="gpt-4o-mini", messages=[
    #                                           {"role": "system", "content": "You are a helpfull ai Assistant for san francisco bay university emplyee's that extracts the sentiment of a user Draft email. give a single word reponse as positive or negative"}, {"role": "user", "content": f"{draft}"}])
    # email_subject = response.choices[0].message.content
    # return email_subject


def summarize_summary(draft):

    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant for San Francisco Bay University employees that summarizes the draft email."),
        ("user", "{draft}")
    ])

    summary_chain = summarize_prompt | client | stringparser
    final_summary = summary_chain.invoke(draft)

    return final_summary

    # summary = client.chat.completions.create(model="gpt-4o-mini", messages=[
    #                                          {"role": "system", "content": "You are a helpfull ai Assistant for san francisco bay university emplyee's that summarizes users draft email"}, {"role": "user", "content": f"{draft}"}])
    # summary_response = summary.choices[0].message.content
    # return summary_response


# answer = compose_email("hello what is happening in eritrea", "english")
# print(answer)
