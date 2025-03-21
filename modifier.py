import streamlit as st
from prompts import meta_prompt
import openai 
import dotenv 
import os 

dotenv.load_dotenv(override=True)

st.set_page_config(layout="wide") 
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

model: str = "gpt-4o-mini"
OPENAI_API_KEY : str = os.getenv("OPENAI_API_KEY") 

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def rag_page():
    st.markdown("<hr>", unsafe_allow_html=True)
    model_option = st.selectbox("Select a model Fari (I'll get more options for you dw)", ("gpt-4o-mini", "o1-mini"))
    if model_option: 
        st.session_state.model = model_option
    st.markdown("""
                <hr>
                <h3 
                    style='text-align: center; 
                    font-size: 25px; 
                    margin-top: 10px; 
                    margin-bottom: 2px;'
                >Meta Prompting
                </h3>""", 
                unsafe_allow_html=True)
    st.markdown("""<p 
                    style='
                    text-align: center; 
                    color: green; 
                    background-color: #21252d; 
                    border-radius: 20px; 
                    '>Note: The model selected above is also reused here below
                </p>""", 
                    unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='text-align: center;'>User prompt</h5>", unsafe_allow_html=True)
        st.markdown("Enter any prompt you need into the `user prompt box` box to interact and extract information from the pdf. The output of your prompt will be provided below. This prompt will also be used by the system as a reference to generate a more refined version of itself.")
        normal_prompt = st.text_area("user prompt box", height=800, placeholder="Enter your prompt here...")

        output_btn_col, clear_btn_col, _ = st.columns([1, 1, 3]) 
        with output_btn_col: 
            outputBtn = st.button("Generate")
        with clear_btn_col: 
            clearBtn = st.button("Clear")

            if clearBtn: 
                st.session_state.engineered_prompt = "Cleared prompt. Enter a new one fari..."
    
    if normal_prompt and outputBtn:
        engineered_prompt = meta_prompt.format(normal_prompt)  
        response = client.chat.completions.create(
            model=st.session_state.model, 
            messages=[{
                "role": "user", 
                "content": engineered_prompt, 
            }], 
        ) 
        content = response.choices[0].message.content  
        if content.startswith("```"): 
            content = content[3:]
        
        if content.endswith('```'): 
            content = content[:-3]

        st.session_state.engineered_prompt = content  

    with col2:
        st.markdown("<h5 style='text-align: center;'>Engineered prompt</h5>", unsafe_allow_html=True)
        st.markdown("This textbox displays an Engineered prompt in the `engineered prompt box` generated using your input as reference. The Engineered prompt is a special type of prompt which ensures structure and better quality of outputs.")
        st.markdown("<p style='margin-bottom: 5px;'>engineered prompt box</p>", unsafe_allow_html=True)
        engineered_prompt = st.code(st.session_state.engineered_prompt, 
                                         height=800, 
                                         language="markdown", 
                                         wrap_lines=True)

    st.markdown("<h3 style='text-align: center; font-size: 25px;'> Generate & Compare!</h3>", unsafe_allow_html=True) 
    out_col1, out_col2 = st.columns(2)
    with out_col1:
        st.markdown("<h5 style='text-align: center;'>Output for User Prompt:</h5>", unsafe_allow_html=True)
        if normal_prompt and outputBtn:
            st.write(f"Processed output for: {normal_prompt}")
            with st.spinner("Normal text output..."): 
                response = client.chat.completions.create(
                    model=st.session_state.model, 
                    temperature=0.1, 
                    messages=[{
                        "role": "user", 
                        "content": normal_prompt, 
                    }], 
                ) 

                st.markdown(response.choices[0].message.content) 

        else:
            st.write("No user prompt provided.")

    with out_col2:
        st.markdown("<h5 style='text-align: center;'>Output for Engineered Prompt:</h5>", unsafe_allow_html=True)
        if st.session_state.engineered_prompt != "Engineered prompt will appear here...": 
            with st.spinner("Output for Engineered prompt..."):
                actual_prompt_to_send = st.session_state.engineered_prompt
                
                response = client.chat.completions.create(
                    model=st.session_state.model, 
                    temperature=0.1, 
                    messages=[{
                        "role": "user", 
                        "content": actual_prompt_to_send, 
                    }], 
                )
                response_content = response.choices[0].message.content
                if response_content.startswith("```markdown"): 
                    response_content = response_content.split("```markdown")[1] 
                elif response_content.startswith("```"): 
                    response_content = response_content.split("```")[1]
                if response_content.endswith("```"): 
                    response_content = response_content.split("```")[0]
                
                st.markdown(response_content) 

def main():
    
    if ("engineered_prompt" not in st.session_state) : 
        st.session_state.engineered_prompt = "Engineered prompt will appear here..."
    
    if ("model" not in st.session_state): 
        st.session_state.model = "gpt-4o-mini"
    
    oess, title, atp = st.columns([1, 8, 1])
    
    with title:  
        st.markdown(
            "<h1 style='text-align: center; font-size: 35px; "
            "margin-top: -20px; '>"
            "Automated Meta Prompting for Farheena Faridi</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<h2 style='text-align: center; font-size: 25px; "
            "margin-top: -20px; margin-bottom: 30px;'>"
            "A tool for reducing my own value to you lol</h2>",
            unsafe_allow_html=True
        )


    with oess: 
        st.image(
            "./.assets/eren.jpg", 
            width=100, 
        )
    
    with atp: 
        st.image(
            "./.assets/historia.jpg", 
            width=195, 
        )

    rag_page()

if __name__ == "__main__":
    main()
