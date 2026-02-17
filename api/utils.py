import pypdf
import re
import os
import json

# Lazy import to avoid cold start issues
gemini_model = None

def get_gemini():
    global gemini_model
    if gemini_model is None:
        try:
            import google.generativeai as genai
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Gemini: {str(e)}")
            raise
    return gemini_model

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def clean_text(text):
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s\.,;:\-\(\)]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def identify_topics(text):
    """
    Uses Gemini API to extract topics from syllabus text.
    This replaces the heavyweight spaCy model.
    """
    try:
        model = get_gemini()
        
        prompt = f"""
You are an educational AI assistant. Extract all distinct topics from this syllabus text.

Rules:
1. Return ONLY a JSON array of topic strings
2. Each topic should be a clear, concise learning objective
3. Preserve UNIT/MODULE/CHAPTER markers if present
4. Remove duplicates
5. Keep topics under 120 characters
6. Extract 5-20 topics depending on content length

Syllabus:
{text[:3000]}

Return format (JSON only, no markdown):
["Topic 1", "Topic 2", "Topic 3"]
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean markdown artifacts if present
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        topics = json.loads(response_text)
        
        # Validate and clean
        if isinstance(topics, list) and len(topics) > 0:
            return [str(t).strip() for t in topics if t and len(str(t).strip()) > 0]
        else:
            # Fallback to simple extraction
            return fallback_topic_extraction(text)
            
    except Exception as e:
        print(f"⚠️ Gemini extraction failed: {str(e)}, using fallback")
        return fallback_topic_extraction(text)

def fallback_topic_extraction(text):
    """
    Simple regex-based topic extraction as fallback.
    """
    lines = text.split('\n')
    topics = []
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
            
        # Check for Unit/Module markers
        if re.match(r'^(UNIT|MODULE|CHAPTER)\s+[IVX\d\w]+', line, re.IGNORECASE):
            topics.append(line)
        # Extract numbered topics
        elif re.match(r'^\d+[\.\)]\s+', line):
            clean_line = re.sub(r'^\d+[\.\)]\s+', '', line)
            if len(clean_line) < 120 and len(clean_line) > 10:
                topics.append(clean_line)
        # Extract bullet points
        elif re.match(r'^[\-\*•]\s+', line):
            clean_line = re.sub(r'^[\-\*•]\s+', '', line)
            if len(clean_line) < 120 and len(clean_line) > 10:
                topics.append(clean_line)
    
    # De-duplicate
    seen = set()
    unique_topics = []
    for t in topics:
        key = t.lower()
        if key not in seen:
            unique_topics.append(t)
            seen.add(key)
    
    return unique_topics[:20]  # Limit to 20 topics
