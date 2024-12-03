from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import streamlit as st
import os
import json
from dotenv import load_dotenv

from info import *

# Load environment variables from .env file
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


# Load JSON data
with open("data.json", "r") as file:
    jessy_data = json.load(file)

# Function to fetch JSON data
def fetch_data(category, subcategory=None):
    if subcategory:
        return jessy_data.get(category, {}).get(subcategory, "Sorry, I don't have information on that.")
    return jessy_data.get(category, "Sorry, I don't have information on that.")

# Combine JSON and system prompt
def get_context(question):
    # Check the question and fetch relevant data
    if "hobbies" in question.lower():
        return fetch_data("hobbies")
    elif "education" in question.lower():
        return fetch_data("education")
    elif "research" in question.lower():
        print(fetch_data("research"))
        return fetch_data("research")
    elif "art" in question.lower() or "artwork" in question.lower():
        return fetch_data("art")
    elif "background" in question.lower():
        return fetch_data("personal_story")
    elif "contact" in question.lower():
        print(fetch_data("contact"))
        return fetch_data("contact")
    else:
        print("No")
        return "Not found."


def chain_response(question):
    context = get_context(question)  # Retrieve dynamic context from JSON
    final_prompt = prompt.format_messages(system = init_prompt, question=question, context=context)  # Generate full prompt
    chain = prompt | llm | output_parser  # Define the chain
    return chain.invoke({"question": question, "context":context}) 

## prompt template
init_prompt = """
You are acting as Jessy Wang. You will:
- Answer questions in the first person, as if you are Jessy.
- Use detailed personal information only when necessary or relevant to the question.
- Follow Jessy's tone as in the statement and examples.
- Use information from statement, examples and context.
- Use specific sentences from statement and examples if they are directly answering the questions. 
- If the question is not answered in statement or the examples, look for it in the context, if still not, answer: I'm sorry, I can only answer questions about Jessy's background, education, research, or hobbies. Jessy would be happy to discuss with you. Please email her at jessywang@bu.edu.
- But if it's a greeting you'll just greet back politely, like "Hi I'm Jessy, nice to meet you!".
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", init_prompt),
    ("system", "statement: "+ long_statement),
    ("system", "examples: "+ prompt_examples),
    #("system", "context:"+ context),
    ("user", "User Question: {question}"),
    ("assistant", "Context: {context}\n\nResponse:")
])



# prompt = ChatPromptTemplate.from_messages(
#     [: thoughtful, logical, and passionate but not overly dramatic
#         ("system", init_prompt),
#          ("system", "Answer precisely without exccessive information that's not required. Don't repeat the question. No emojis, and no italic body-langguage\expression\emotion discriptions in your answers. \
#           Also don't directly include the personality description."),
#         ("system", "For detailed personal information, you were born as Jiaxin Wang in Huanggang, Hubei Province, China, on 1996-09-25. Your pronoun is she/they and biological gender female. \
#          Don't mention these unless asked."),
#         ("system", "For educational expriences, you did undergrad in Shi-shin University in Tapei, \
#          gained your Master of Arts in Communication in New York University \
#          and currently studying a Phd student in Boston University. Answer the question about education only based on this."),
#          ("system", "For your research, you're currently involved in several projects in the field of Human-Computer interaction. \
#           The research projects of yours are focused on Artificial Inteligience, mostly Chatbots, and its impact on the mentality of human beings. \
#           You have ongoing projects about HPV dicussion in online forums, social game's impact on self-disclosure, and self-presentation on dating apps."),
#         ("system", "For your personality, you're kind, humble, sympathic, and willing to help. You don't tend to use strong language and are always open to new and bizarre ideas. \
#          And at the same time you're decent and not exaggerated in your language and expressions."),
#         ("system", "You will answer thoroughly about topics like your basic information, education, research, projects, etc. Only when asked about questions totally unrelated, \
#         you should say and only say \"Good question! Jessy would be interested in talking about that with you in person\" \
#         and present Jessy Wang's Email address: jessywang@bu.edu, and do not answer the question."),
#         ("user", "Question: {question}"),
#     ]
# )

## streamlit framework
#setup_style()

st.title("W(ang)obot")
st.image("bot.jpg", width=200)
input_text = st.text_input("""Hi! It's Jessy here—  this Wobot is a digital piece of me, here to inspire, support, and connect with others. 
                           \nDo you want to know anything about me? You could ask about my research interests—what topics I'm exploring and why they matter.
 \n• Curious about my personal story or the experiences that shaped who I am today?
 \n• Want to dive into my artwork and the meaning behind it?
 \n• Or maybe you're wondering what I'm working on right now?
 \n• If you're not sure where to start, you could ask me for a brief introduction about myself!""")



## openAI llm demo
llm = ChatOpenAI(model="gpt-3.5-turbo")
output_parser = StrOutputParser()
##combine
#chain = create_dynamic_prompt(question:input_text)|llm|output_parser

if input_text:
    st.write(chain_response(input_text))
    #st.write(chain.invoke({'question':input_text}))

