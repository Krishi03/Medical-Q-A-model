import streamlit as st
import requests
from dotenv import load_dotenv
import os


load_dotenv()

def main():
    st.title("Medical Q&A Assistant")
    
    
    with st.sidebar:
        st.markdown("### Privacy & Data Protection")
        st.info("""
        🔒 **HIPAA Compliance Notice**
        - No personal health information (PHI) is stored
        - All queries are processed securely
        - Data is encrypted in transit
        - No user session data is retained
        """)
    
    st.write("Ask questions about medical topics and get evidence-based answers")
    
    
    st.markdown("""
    > **Important**: This system provides general medical information for educational purposes only. 
    It does not store or process personal health information. For personalized medical advice, 
    always consult with qualified healthcare professionals.
    """)

    
    query = st.text_input("Enter your medical question")

    if st.button("Get Answer"):
        if query:
            with st.spinner("Processing your question..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/query",
                        json={"text": query}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success':
                            # Display Answer
                            st.markdown("### Answer:")
                            st.write(data['answer'])
                            
                            # Display Follow-up Questions
                            if data.get('follow_up_questions'):
                                st.markdown("### Follow-up Questions")
                                for q in data['follow_up_questions']:
                                    st.markdown(f"- {q}")
                        else:
                            st.error(f"Error: {data.get('answer', 'Unknown error')}")
                    else:
                        st.error("Failed to get response from server")
                
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend server. Please make sure it's running.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question")

if __name__ == "__main__":
    main()
