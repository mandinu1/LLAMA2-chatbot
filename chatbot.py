import streamlit as st
import os
import replicate
import tempfile
import speech_recognition as sr
from gtts import gTTS


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error making a request to Google API: {e}")


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    return tts


# function to play the speech
def play_speech(tts):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        st.audio(temp_audio.name, format='audio/mp3')


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def generate_response(input_user):
    temperature = 0.1
    top_p = 0.9
    max_length = 500
    dialog = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.message:
        if dict_message["role"] == "user":
            dialog += "user :" + dict_message["content"] + "\n\n"
        else:
            dialog += "assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm, input={"prompt": f"{dialog}{input_user} assistant: ",
                                       "temperature": temperature, "top_p": top_p, "max_length": max_length,
                                       "repetition_penalty": 1
                                       })


st.set_page_config(page_title="💬 MY Llama 2 Chatbot")

with st.sidebar:
    st.title('My first LLAMA 2 chatbot')
    st.write('This chat bot is created is using the open-source Llama 2 LLM model from Meta train with 7 '
             'billion parameters (LLAMA2-7B)')
    replicate_api = 'r8_IgKwaAEgZNqs7l6oNz5xFlFteTAffDX26ClLs'
    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    st.subheader('Models and parameters')
    llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'  # 7B LLAMA model link
    st.button('Clear Chat History', on_click=clear_chat_history)
recognized_text = st.chat_input("Say something")
speaker = False
col1, col2 = st.columns(2)
# Check if "🎙️ Speak" button is clicked
if col1.button("🎙️ voice "):
    transcription = recognize_speech()
    recognized_text = transcription
# Check if "Press Me" button is pressed
if col2.button(":loud_sound: speaker"):
    speaker = True

if "messages" not in st.session_state.keys():
    st.session_state.message = [{"role": "assistant", "content": "How may I help you ?"}]

for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.write(message["content"])
