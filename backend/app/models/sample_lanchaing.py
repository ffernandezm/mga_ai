from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


#llm = OpenAI(temperature=0)
llmmodel = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key='AIzaSyD27Kp4hi3B0M_Qhf-B6nsK7fR2tRq51bE',
            convert_system_message_to_human=True
        )
template = """You are a nice chatbot having a conversation with a human.

Previous conversation:
{chat_history}

New human question: {question}
Response:"""
prompt = PromptTemplate.from_template(template)
memory = ConversationBufferMemory(memory_key="chat_history")
conversation = LLMChain(
    llm=llmmodel,
    prompt=prompt,
    verbose=True,
    memory=memory
)

conversation({"question": "hi"})