import app
from app import OCR , init_agent, main
from langchain_core.prompts import PromptTemplate 
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Welcome to Flavor Archives! ", layout="wide",initial_sidebar_state="expanded", page_icon="🍔")
st.title("Explore the legends behind your menu and tell cool tales about your food.")


upload_prompt = "I want to see what items are on the menu. I just sent you the picture of the menu. Answer with like Thanks for sharing your menu I m here to impress you with my super inteligent food knowledge. Start by listing the items on the menu."
app.image_text = ""
 

def show_ui(agent_executor, prompt_to_user=" I'm thrilled to be your culinary guide today. If you have a menu or a specific dish you're curious about, please share it with me, and I'll weave some fascinating tales about the origins and cultural significance of the foods you're exploring. Let's turn every meal into a delightful journey of discovery! 🍽️✨"):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": prompt_to_user}]
        st.session_state['chat_history'] = []  


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.sidebar.file_uploader("Upload your menu image here", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        try:
            app.image_text = str(OCR(uploaded_file))
            response = agent_executor.invoke({"items_available" : app.image_text ,"input": upload_prompt, "chat_history": st.session_state.chat_history})
            st.chat_message("assistant").markdown(response["output"])
        except Exception as e:
            st.error(f"Failed to process the image: {str(e)}")

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "human", "content": prompt})
        st.session_state.chat_history.append(HumanMessage(content=prompt))  
        
        with st.chat_message("human"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                print("agent_executor.invoke:",{"items_available" : app.image_text ,"input": prompt, "chat_history": st.session_state.chat_history },"\n")
                response = agent_executor.invoke({"items_available" : app.image_text ,"input": prompt, "chat_history": st.session_state.chat_history})
                print("st.session_state:",st.session_state,"\n")
                st.markdown(response["output"])

            st.session_state.messages.append({"role": "assistant", "content": response["output"]})
            st.session_state.chat_history.append(AIMessage(content=response["output"]))  



@st.cache_resource
def get_agent_executor(openai_api_key = None):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature = 0.8)
    agent_executor = init_agent(llm)
    return agent_executor

def get_secret_or_input(secret_key, secret_name, info_link = None):
    if secret_key in st.secrets:
        st.write("Found %s secret" % secret_key)
        secret_value = st.secrets[secret_key]
    else:
        st.write(f"Please provide your {secret_name}")
        secret_value = st.text_input(secret_name, key=f"input_{secret_key}", type="password")
        if secret_value:
            st.session_state[secret_key] = secret_value
        if info_link:
            st.markdown(f"[Get an {secret_name}]({info_link})")
    return secret_value

def run():
    ready = True
    openai_api_key = st.session_state.get("OPENAI_API_KEY")
    with st.sidebar:
        if not openai_api_key:
            openai_api_key = get_secret_or_input('OPENAI_API_KEY', "OpenAI API key",
                                                 info_link="https://platform.openai.com/account/api-keys")
    if not openai_api_key:
        st.warning("Missing OPENAI_API_KEY")
        ready = False

    if ready:
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.9, api_key=openai_api_key)
        agent_executor = init_agent(llm)
        st.subheader("Chat with your Menu")
        show_ui(agent_executor)
    else:
        st.warning("Please provide the necessary information to get started")
        st.stop()

run()
