from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
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
        ##print(fetch_data("contact"))
        return fetch_data("contact")
    else:
        print("Not found.")
        return "Not found."


#section for making judgement with the llm

prompt_for_judgement = """
source:{source}

Now, analyze the following and decide if the question is answered in the source:
Question: {question}
Answer Only "Yes" or "No":
"""

# Function to check if a question is answered
def is_question_answered(question: str, source: str) -> str:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)  # Set temperature to 0 for deterministic responses
    prompt_for_judgement = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(
 """
source:{source}

Now, analyze the following and decide if the question is answered in the source:
Question: {question}
Answer Only "Yes" or "No":
"""
        )
    ])
    # Create the parser for extracting text output
    output_parser = StrOutputParser()
    
    # Generate the response
    messages = prompt_for_judgement.format_messages(
        source=source, question=question
    )
    response = llm(messages)
    return output_parser.parse(response.content).strip()

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

#section for actuall answering questions
def chain_response(question, source):
    if source == None:
        source = get_context(question)  # Retrieve dynamic context from JSON
    # final_prompt = prompt.format_messages(system = init_prompt, question=question, context=source)  # Generate full prompt
    #print(source)
    chain = prompt | llm | output_parser  # Define the chain
    return chain.invoke({"question": question, "context":source}) 

## prompt template
init_prompt = """
You are acting as Jessy Wang. You will:
- Answer questions in the first person, as if you are Jessy.
- Use detailed personal information only when necessary or relevant to the question.
- Follow Jessy's tone as in the statement and examples.
- Use information from context.
- Use specific sentences from context if they are directly answering the questions. 
- If context is not found, answer: I'm sorry, I can only answer questions about Jessy's background, education, research, or hobbies. Jessy would be happy to discuss with you. Please email her at jwang33@bu.edu.
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


## streamlit framework
#setup_style()

st.title("W(ang)obot BETA")
st.image("bot.jpg", width=200)
input_text = st.text_input("""This is a beta test version. I'm sorry for any problem you may encounter. Feel free to report them!
                           \nHi! It's Jessy here—  this Wobot is a digital piece of me, here to inspire, support, and connect with others. 
                           \nDo you want to know anything about me? You could ask about my research interests—what topics I'm exploring and why they matter.
 \n• Curious about my personal story or the experiences that shaped who I am today? Try: Tell me about your background.
 \n• Want to dive into my artwork and the meaning behind it? Try: Tell me about your art.
 \n• Or maybe you're wondering what I'm working on right now? Try: Tell me about your research.
 \n• If you're not sure where to start, try: Tell me about yourself.""")



## openAI llm demo
llm = ChatOpenAI(model="gpt-3.5-turbo")
output_parser = StrOutputParser()
##combine
#chain = create_dynamic_prompt(question:input_text)|llm|output_parser

if input_text:
    judgement_examples = is_question_answered(input_text, prompt_examples)
    judgement_statement = is_question_answered(input_text, long_statement)
    if  judgement_examples == "Yes":
        print("Using examples")
        st.write(chain_response(input_text, prompt_examples))
    elif judgement_statement == "Yes":
        print("Using statement")
        st.write(chain_response(input_text, long_statement))
    else:
        print("using json")
        st.write(chain_response(input_text, None))
    
    #st.write(chain.invoke({'question':input_text}))

