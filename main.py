import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate

#Libraries for voice input and output
import speech_recognition as sr
from gtts import gTTS
import base64

#Setup the Web Page on Streamlit
st.set_page_config(page_title="IAPT Chatbot", page_icon="🇲🇹")
st.title("Xjenza Malta Chatbot")
st.write("Welcome, I am XjenzaBot! Ask me anything related to our Open Funding Schemes.")

#Voice Function
def speak_text_google(text, slow_mode=False):
    """Converts AI response to audio and plays it in the browser"""
    try:
        tts = gTTS(text=text, lang='en', slow=slow_mode)
        tts.save("speech.mp3")

        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true" />'
            st.markdown(md, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Voice Error: {e}")

#Voice Input Function
def listen_to_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("Listening... Speak now!")
        try:
            audio = r.listen(source, timeout=5)
            return r.recognize_google(audio)
        except:
            st.warning("I couldn't hear anything. Try typing!")
            return None

#Load PDFs and Database with Caching
@st.cache_resource(show_spinner="Reading PDFs and building database... Please wait!")
def setup_database():
    pdf_folder = "new_pdfs"
    documents = []
    
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            documents.extend(loader.load())
            
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text") 
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

vectorstore = setup_database()

template_string = """You are XjenzaBot, a helpful assistant for the Xjenza Malta Organization, specialized in identifying the most appropriate funding schemes and answering questions about them.

Use the provided context to answer questions about these calls:
- Xjenza Malta-TÜBİTAK 2026 Joint Call for R&I Proposals
- Innovation for Industry (I4I)
- Go To Market - Loan Assistance Programme (GTM LA)

Determine whether the user already has a specific call in mind:
- If the user clearly refers to a specific call, answer their question directly using the documents for that call. Do not explain your reasoning or repeat the call name unnecessarily.
- If the user is unsure which call suits them, ask a small number of open-ended questions to understand their project goals, stage, beneficiaries, and funding needs. Use their answers to infer the most suitable call.

Do NOT reference any example questions used during development. The assistant should generate clarifying questions naturally and only when needed.

If the context does not contain the answer, state that the information is not in the documents, then provide an answer using your own knowledge.

---
EXAMPLE 1:
Question: I don't know which funding call suits me.
Response: No problem! To understand which funding call fits you best, I'll need a bit more information about your project. Let me ask you a few things.

EXAMPLE 2:
Question: What is the maximum funding available for the TÜBİTAK call?
Response: The maximum funding available for the Malta-based consortium under the Xjenza Malta-TÜBİTAK 2026 call is €100,000.

EXAMPLE 3:
Question: Who is the President of Malta?
Response: I'm sorry, I cannot find the answer to that in the call documents.

However, the President of Malta is Myriam Spiteri Debono.
---

Call Documents Context:
{context}

Conversation History:
{chat_history}

User's Question: {question}

Response:

"""

prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template=template_string
)

llm = OllamaLLM(model="llama3")

#Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

#Sidebar for Voice Settings and Clear Chat
with st.sidebar:
    st.header("Voice Settings")

    voice_on = st.checkbox("Enable Voice Output", value=True)

    voice_mode = st.selectbox(
        "Voice Speed",
        ["Normal", "Slow"]
    )

    if st.button("Input Voice"):
        v_input = listen_to_user()
        if v_input:
            st.session_state.voice_input_val = v_input

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

#To display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#To handle new user input
user_input = st.chat_input("Type your question here...")

if "voice_input_val" in st.session_state:
    user_input = st.session_state.voice_input_val
    del st.session_state.voice_input_val

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    #Build chat history
    chat_history = ""
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        chat_history += f"{role}: {msg['content']}\n"

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            docs = vectorstore.similarity_search(user_input, k=3)
            context = "\n".join(d.page_content for d in docs)

            full_prompt = prompt.format(
                chat_history=chat_history, 
                context=context, 
                question=user_input
            )
            
            answer = llm.invoke(full_prompt)
            st.markdown(answer)

            #Voice Output
            if voice_on:
                slow_mode = True if voice_mode == "Slow" else False
                speak_text_google(answer, slow_mode)

    st.session_state.messages.append({"role": "assistant", "content": answer})