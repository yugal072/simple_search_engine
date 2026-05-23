import streamlit as st 
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchResults
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.callbacks import StreamlitCallbackHandler

## Arxiv and Wikipedia tools
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=250)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper = WikipediaAPIWrapper(
    top_k_results=2, 
    doc_content_chars_max=300,
    # This is the most important part:
    wiki_client_kwargs={
        "user_agent": "LangchainStreamlitChat/1.0 (contact: yugalupadhyay588@gmail.com)"
    }
)

wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)

search = DuckDuckGoSearchResults(name="search", output_format="list", num_results=3)


st.title("Langchain---Chat with search")



# Sidebar for settings

api_key = st.secrets["GROQ_API_KEY"]



if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role":"assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])
    
if prompt:= st.chat_input(placeholder="what is machine learning"):
    st.session_state.messages.append({"role":"user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    llm = ChatGroq(api_key = api_key, model = "llama-3.3-70b-versatile", streaming=True)
    
    tools = [search, arxiv, wiki]
    
    search_agent = initialize_agent(
        tools,
        llm,
        agent= =AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors = True,
        max_iteration = 8,
        early_stopping_method="generate",
        verbose = True,
        return_intermediate_steps=False
    )
    
    with st.chat_message("assistant"):
        st.cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        try:
            response = search_agent.run(prompt,callbacks=[st.cb])
            st.session_state.messages.append({'role':'assistant', 'content': response})
            st.write(response)
        except:
            response = f"Sorry, I encountered an error: {str(e)[:200]}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
