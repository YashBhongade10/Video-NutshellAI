import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PROMPT = """You are a YouTube video summarizer. Analyze the transcript text and:
1. Identify the main topics discussed
2. Extract key points for each topic
3. Provide concise bullet points
4. Keep summary under 250 words
5. Maintain original context and meaning

Transcript:
"""

def extract_transcript(video_url):
    try:
        if "youtube.com" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        else:
            raise ValueError("Invalid YouTube URL format")

        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)

        transcript = fetched_transcript.to_raw_data()
        
        if not transcript:
            raise ValueError("No transcript available for this video")

        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text

    except IndexError:
        st.error("⚠️ Could not extract video ID from URL")
        return None
    except Exception as e:
        st.error(f"⚠️ Error extracting transcript: {str(e)}")
        return None

def generate_summary(transcript):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(PROMPT + transcript)
        return response.text
    except Exception as e:
        st.error(f"⚠️ Error generating summary: {str(e)}")
        return None

st.set_page_config(page_title="YouTube NutshellAI", page_icon="📝")

st.title("🎥 YouTube Video NutshellAI")
st.markdown("Get AI-powered summaries of any YouTube video with transcripts")

with st.expander("ℹ️ How to use"):
    st.write("""
    1. Paste a YouTube video URL
    2. Click 'Generate Summary'
    3. Get key points in seconds
    """)

# Input section
video_url = st.text_input(
    "Enter YouTube Video URL:",
    placeholder="https://www.youtube.com/watch?v=..."
    
)

if st.button("✨ Generate Summary", type="primary"):
    if not video_url:
        st.warning("Please enter a YouTube URL")
    else:
        with st.spinner("🔍 Extracting transcript..."):
            transcript = extract_transcript(video_url)
        
        if transcript:
            with st.spinner("🧠 Generating summary..."):
                summary = generate_summary(transcript)
            
            if summary:
                st.success("✅ Summary generated successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Video Preview")
                    if "youtube.com" in video_url:
                        video_id = video_url.split("v=")[1].split("&")[0]
                    else:
                        video_id = video_url.split("/")[-1]
                    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg")
                
                with col2:
                    st.subheader("Key Points")
                    st.markdown(summary)
                
                with st.expander("📜 View Full Transcript"):
                    st.text(transcript)
            else:
                st.error("Failed to generate summary")
        else:
            st.error("Could not extract transcript from this video")

st.markdown("---")
st.caption("Note: Works best with videos that have English captions available")