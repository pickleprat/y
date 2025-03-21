import streamlit as st
from prompts import meta_prompt
import openai 
import dotenv 
import os 
import re 
import json 
import pymupdf4llm

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

def extract_markdown_per_page(pdf_path):
    page_chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    markdown_list = [page_chunk['text'] for page_chunk in page_chunks]
    return markdown_list

def rag_page():
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

        outputBtn = st.button("Generate Outputs")
    
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
                if "markdown_pages" in st.session_state: 
                    normal_prompt = (normal_prompt + "### TEXT CONTENT ###\n" +  
                        ".".join(st.session_state.markdown_pages) ) 

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
                
                if "markdown_pages" in st.session_state:
                    actual_prompt_to_send += "### PDF CONTENT###\n" + ".".join(st.session_state.markdown_pages)
                
                response = client.chat.completions.create(
                    model=st.session_state.model, 
                    temperature=0.1, 
                    messages=[{
                        "role": "user", 
                        "content": actual_prompt_to_send, 
                    }], 
                )
                
                try:
                    response_content = response.choices[0].message.content
                    if re.findall(r"<output>(.*?)</output>", response_content, re.DOTALL):
                        json_content = re.findall(r"<output>(.*?)</output>", response_content, re.DOTALL)[0]
                        if json_content.startswith("```json"):
                            json_content = json_content.split("```json")[1].split("```")[0]
                        js_dict = json.loads(json_content)
                        st.json(js_dict)
                    else:
                        st.code(response_content)
                except Exception as e:
                    st.markdown(response.choices[0].message.content)
                    print(f"Error processing response: {e}")

def main():
    
    if ("engineered_prompt" not in st.session_state) : 
        st.session_state.engineered_prompt = "Engineered prompt will appear here..."

    # if ("markdown_pages" not in st.session_state) : 
    #     pdf_path: str = "./assets/acceptable-policies.pdf" 
    #     st.session_state.markdown_pages = extract_markdown_per_page(pdf_path)
    
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

    # url = "https://atp2025.theopeneyes.com/sample/ATP2025-GenAIAcceptableUSPolicySample.pdf"

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

    # st.markdown(
    #     """
    #     <hr>
    #     <div style="text-align: center; margin-top: 10px; ">
    #         <h3 style="font-size: 25px;">About Policy Information used in this demo</h3>
    #         <p style="margin-left: 180px; margin-right: 180px; font-size: 15px; margin-bottom: 2px; ">The Policy provided below is a sample policy outlining guidelines for the safe and responsible use of AI technology in the workplace. </p>
    #         <p style="margin-left: 180px; margin-right: 180px; font-size: 15px; margin-bottom: 2px; ">It defines key terms, details security best practices, and explains staff responsibilities for using AI tools ethically and securely.</p>
    #     </div>
    #     """, 
    #     unsafe_allow_html=True
    # ) 

    # st.markdown(
    #     f"""
    #     <div style="text-align: center; margin-top: 20px;">
    #         <a href="{url}" target="_blank">
    #             <button style="font-size:16px; margin-top: -70px; margin-bottom: 30px; padding:10px 20px; cursor:pointer; border: solid black 3px; background-color: rgb(14, 205, 142); border-radius: 20px; ">
    #                 View Policy 
    #             </button>
    #         </a>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # ) 
    rag_page()

if __name__ == "__main__":
    main()
