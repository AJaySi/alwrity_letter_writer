import time #Iwish
import os
import json
import requests
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import google.generativeai as genai


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity - AI Business Letter Writer (Beta)",
        layout="wide",
    )
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"""
      <style>
      /* Custom button styling */
		div.stButton > button:first-child {
		    background: #1565C0;
		    color: white;
		    border: none;
		    padding: 12px 24px;
		    border-radius: 8px;
		    text-align: center;
		    text-decoration: none;
		    display: inline-block;
		    font-size: 16px;
		    margin: 10px 2px;
		    cursor: pointer;
		    transition: background-color 0.3s ease;
		    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
		    font-weight: bold;
		}
		
		div.stButton > button:hover:first-child {
		    background-color: #1976A2;
		    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
		}
      </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    # Title and description
    st.title("✍️ Alwrity - AI Business Letter Writer (Beta)")


    with st.expander("**PRO-TIP** - Read the instructions below.", expanded=True):
        col1, col2, space = st.columns([5, 5, 0.5])
        with col1:
            # Letter Type Selection
            letter_types = ["Proposal", "Complaint", "Thank You", "Reference Letter", "Resignation Letter"]
            letter_type = st.selectbox("**Select Letter Type**", letter_types)
            key_points = st.text_area("**Key Points to Include in the letter**")
        with col2:
            # Recipient Information
            recipient_name = st.text_input("**Enter Recipient's Name**")
            # Sender Information
            #sender_name = st.text_input("**Enter Sender Name**")

    if st.button('**Write Business Letter**'):
        with st.status("Assigning AI professional to write your letter..", expanded=True) as status:
            if not key_points or not recipient_name:
                st.error("🚫 Error: Enter all the details, least you can do..")
            else:
                response = business_letter_writer(letter_type, key_points, recipient_name, status)
                if response:
                    st.subheader(f'**🧕🔬👩 Alwrity can make mistakes. Your Final Business Letter!**')
                    st.write(response)
                else:
                    st.error("💥**Failed to write Letter. Please try again!**")


def business_letter_writer(letter_type, key_points, recipient_name, status):
    """ Email project_update_writer """

    prompt = f"""
        Letter Type: {letter_type}
        Recipient Name: {recipient_name}

        Letter Content/Purpose:  {key_points} 

        Instructions for AI:

        * Generate a professional business letter based on the specified letter type and content/purpose.
        * Infer the tone and desired outcome based on the letter type and content.
        * Include relevant details and information commonly found in such letters. 
        * Maintain a clear and concise writing style.
    """
    status.update(label="Writing Business Letter...")
    try:
        response = generate_text_with_exception_handling(prompt)
        return response
    except Exception as err:
        st.error(f"Exit: Failed to get response from LLM: {err}")
        exit(1)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt):
    """
    Generates text using the Gemini model with exception handling.

    Args:
        api_key (str): Your Google Generative AI API key.
        prompt (str): The prompt for text generation.

    Returns:
        str: The generated text.
    """

    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text

    except Exception as e:
        st.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
