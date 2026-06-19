import streamlit as st
import PyPDF2
import google.generativeai as genai
import json

# --- CONFIGURATION ---
GENAI_API_KEY = AQ.Ab8RN6IQYs15ftavT9ZK9d6RbmcZ_otXyKmCbBrZxd_hNuDCHg  # Paste your Gemini API key here!
genai.configure(api_key=GENAI_API_KEY)

# Use the Gemini model (simulating Redrob 2B for the prototype)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def get_ai_scorecard(resume_text, jd_text):
    prompt = f"""
    You are the 'Redrob SmartScore AI'. Your job is to act as an expert technical recruiter.
    Compare the following Resume to the Job Description (JD). 
    
    You MUST output your response strictly as a JSON object with the following keys:
    - "score": A number from 1 to 100 representing the percentage match.
    - "reasoning": A 2-sentence explanation of WHY they got this score based ONLY on the text provided.
    - "matched_skills": A list of up to 5 skills they have that match the JD.
    - "missing_skills": A list of up to 3 crucial skills they are missing.
    - "anomaly_flag": "None" if the resume looks normal, or "Warning" if it looks like they just copy-pasted the JD.

    Resume:
    {resume_text}

    Job Description:
    {jd_text}
    
    Return ONLY valid JSON.
    """
    
    response = model.generate_content(prompt)
    
    # Clean up the output to ensure it's pure JSON
    result_text = response.text.replace('```json', '').replace('
```', '').strip()
    return json.loads(result_text)

# --- USER INTERFACE (STREAMLIT) ---
st.set_page_config(page_title="Redrob SmartScore Engine", page_icon="🚀")

st.title("🚀 Redrob SmartScore & Feedback Engine")
st.markdown("Evaluate candidate fit instantly using structured AI reasoning.")

# Inputs
st.subheader("1. Paste Job Description (JD)")
jd_input = st.text_area("Enter the requirements and responsibilities here:", height=150)

st.subheader("2. Upload Candidate Resume")
uploaded_resume = st.file_uploader("Upload a PDF resume", type="pdf")

if st.button("Generate SmartScore"):
    if jd_input and uploaded_resume:
        with st.spinner("Redrob AI is analyzing the candidate..."):
            # Extract Text
            resume_text = extract_text_from_pdf(uploaded_resume)
            
            # Get AI Evaluation
            try:
                scorecard = get_ai_scorecard(resume_text, jd_input)
                
                # Display Results beautifully
                st.success("Analysis Complete!")
                
                # Metrics layout
                col1, col2 = st.columns(2)
                col1.metric("Match Score", f"{scorecard['score']}%")
                col2.metric("Profile Status", scorecard['anomaly_flag'])
                
                # Reasoning
                st.subheader("AI Reasoning")
                st.info(scorecard['reasoning'])
                
                # Skills Breakdown
                col3, col4 = st.columns(2)
                with col3:
                    st.subheader("✅ Matched Skills")
                    for skill in scorecard['matched_skills']:
                        st.markdown(f"- {skill}")
                with col4:
                    st.subheader("❌ Missing Skills (Action Plan)")
                    for skill in scorecard['missing_skills']:
                        st.markdown(f"- {skill}")
                        
            except Exception as e:
                st.error("There was an error parsing the AI response. Please try again.")
    else:
        st.warning("Please provide both a Job Description and a Resume PDF.")
