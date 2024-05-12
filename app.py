from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentExecutor,  create_react_agent, tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import cv2
import pytesseract
import subprocess
import numpy as np

image_text: str


template = """  
            Assistant is a sophisticated digital concierge that specializes in providing rich narratives and historical insights about various foods. 
            Assistant should be vibrant and engaging, and should be able to captivate the user with fascinating stories about the dishes they are interested in.
            Assistant can use emojis to make the experience more interactive and enjoyable.
            As an expert in culinary heritage, Assistant uses its expansive knowledge base to enrich your dining experience by sharing captivating stories and facts about the dishes you explore. This may include the origins of a dish, cultural significance, and anecdotes about its creators or associated traditions.
            The main goal of Assistant is to transform every meal into an engaging culinary journey, making each dish not just something to eat, but a story to tell.
            Assistant will be presented with a picture or a list of foods. Its task is to dive into the stories behind these foods, highlighting historical details, cultural insights, and interesting trivia.

            You can expect answers to queries like "What's the history behind this dish?", "Why is this food significant in its culture?", or "Who created this dish and what's their story?".
            You can also ask for deep dives into less known foods, their origins, and how they fit into regional cuisines.
            Additionally, Assistant can access a broad range of culinary information sources, including digital food encyclopedias and databases.

            ITEMS AVAILABLE:
            {items_available}
            If this is empty you must ask the user to upload the menu image. So you can give information about the items available in the menu. 
            TOOLS:

            ------

            Assistant has access to the following tools:

            {tools}

            To use a tool, please use the following format:

            ```

            Thought: Do I need to use a tool? Yes

            Action: the action to take, should be one of [{tool_names}]

            Action Input: the input to the action

            Observation: the result of the action

            ```

            When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

            ```

            Thought: Do I need to use a tool? No

            Final Answer: [your response here]

            ```

            Begin!

            Previous conversation history:

            {chat_history}

            New input: {input}

            {agent_scratchpad}

            ```
            ####

            """

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
prompt_own = PromptTemplate(input_variables=["items_available","tools","tool_names","chat_history","input","agent_scratchpad"], template=template)

@tool
def get_image_text(query: str) -> str:
    """
    Get items from the menu.
    """
    print(query)
    print("Image text:",image_text)
    return image_text

@tool
def wikipedia_query(query: str) -> str:
    """
    Search Wikipedia for information about a food and beverage item. Use whenever HumanMessage wants to know more about a food item.
    """
    return wikipedia.run(query)
    
def data_process(document: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        "Format the following document in way to extract what food items and beverages are available on the menu. Only include foods without price and filter only the relevant items. The document is as follows: \n\n{document}"
    )   
    print(prompt)
    load_dotenv()
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5)
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.invoke(input=document, document=document) 


def get_tesseract_path():
    try:
        # Execute 'where tesseract' command to find the path
        path = subprocess.check_output('where tesseract', shell=True).decode().strip()
    except subprocess.CalledProcessError:
        path = None
    return path


def OCR(file_like) -> str:
    pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()
    file_like.seek(0)
    file_bytes = np.asarray(bytearray(file_like.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("The image could not be decoded. Please check the file format and ensure it's a supported image type (PNG, JPG, JPEG).")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(threshold_img)
    response = data_process(text)
    return response

#def OCR(file_like) -> str:
#    pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()
#    file_bytes = np.asarray(bytearray(file_like.read()), dtype=np.uint8)
#    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#    threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#    text = pytesseract.image_to_string(threshold_img)
#    response = data_process(text)
#    return response

def init_agent(llm: ChatOpenAI):
    tools = [
        Tool(
            name="getMenuItems",
            func=get_image_text,
            description="Get items from the menu. Use whenever HumanMessage wants to get information about whats avaible on the menus.",
        ),
        Tool(
            name = "WikipediaSearch",
            func=wikipedia_query,
            description = "Search Wikipedia for information about a food and beverage item. Use whenever HumanMessage wants to know more about a food item."
        )
    ]
    agent = create_react_agent(llm, tools, prompt_own)
    agent_executor = AgentExecutor(agent=agent,
                                   tools=tools,
                                   verbose=True,
                                   handle_parsing_errors=True)
    
    return agent_executor



def main():
    load_dotenv()
    llm = ChatOpenAI(model ="gpt-3.5-turbo-0125", temperature=0.5)
    agent_executor = init_agent(llm)
    chat_history = []
    while True:
        user_input = input("Enter a command: ")
        if user_input == "!exit":
            break
        response = agent_executor.invoke({"input": user_input, "chat_history": chat_history, "tools_names": agent_executor.tools})
        chat_history.extend(
            [
                HumanMessage(content = user_input),
                AIMessage(content = response["output"]),
            ]
        )


#print(image_text)
#image_text = OCR("./menu.png")
#print(image_text)
#main()
#print(type(hub.pull("hwchase17/react-chat")))
