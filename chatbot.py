import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🫀💬 Heart Health Chatbot")

# Set Replicate API Key directly in the code
REPLICATE_API_TOKEN = "r8_NxcEZua2zw5Sx8UYPJhhbx5PjUu8ceg1T2Cn7"  # Add your API key here
os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN

# Sidebar for model selection and parameters
with st.sidebar:
    st.title('🫀💬 Heart Health Chatbot')
    st.success('API key successfully loaded!', icon='✅')

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm here to help you with heart health questions. Feel free to ask about heart symptoms, conditions, treatments, or preventive measures."}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm here to help you with heart health questions. Feel free to ask about heart symptoms, conditions, treatments, or preventive measures."}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating heart-specific response
def generate_llama2_response(prompt_input):
    string_dialogue = """
    You are a specialized heart health assistant. You should focus on answering questions related to heart health, symptoms, types of heart diseases, treatments, and preventive care.
    """
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(
        llm,
        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
               "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1}
    )
    return output

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)