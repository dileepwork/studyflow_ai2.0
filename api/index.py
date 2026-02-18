from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import re
import json
import pypdf
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.before_request
def log_request():
    print(f"📡 Request: [{request.method}] {request.path}")

# ==========================================
# 🤖 GEMINI CONFIGURATION
# ==========================================
def get_gemini():
    try:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"❌ Gemini load failed: {str(e)}")
        return None

# ==========================================
# 📄 UTILS (Self-contained)
# ==========================================

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
    return text

def clean_text(text):
    # Keep alphanumeric and basic punctuation
    text = re.sub(r'[^\w\s\.,;:\-\(\)]', ' ', text)
    # Collapse multiple spaces/tabs to single space (but NOT newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse multiple newlines to single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def identify_topics(text):
    """Uses Gemini API with fallback to regex"""
    model = get_gemini()
    if model:
        try:
            prompt = f"""
            Identify and extract the main learning topics or key concepts from the following text.
            The text might be a formal syllabus, a chapter summary, or a list of learning objectives.
            
            Strict Rules:
            1. Extract distinct, high-level topics (max 15).
            2. Each topic should be a SHORT, clear conceptual title (3-5 words max).
            3. CRITICAL: Remove all labels like "UNIT I", "MODULE 1", "CHAPTER 1", "TOPIC 1.1", etc.
            4. Remove metadata like "Page 1", "Session 2", dates, university names, or "Notes/Syllabus".
            5. Remove course codes like "CS3491", "AI3001", etc.
            6. NEVER include phrases like "You said", "Here are the topics", or any introductory text.
            7. Return ONLY a JSON array of strings.
            
            Text:
            {text[:5000]}
            """
            response = model.generate_content(prompt)
            raw_response = response.text.replace('```json', '').replace('```', '').strip()
            start = raw_response.find('[')
            end = raw_response.rfind(']') + 1
            if start != -1 and end != 0:
                topics = json.loads(raw_response[start:end])
                if isinstance(topics, list) and len(topics) > 0:
                    cleaned = []
                    for t in topics:
                        t = str(t).strip()
                        # Deep Cleaning
                        t = re.sub(r'^(UNIT|MODULE|CHAPTER|TOPIC|SECTION|PART|LESSON)\s*[\d\.\-\:]*\s*', '', t, flags=re.IGNORECASE)
                        t = re.sub(r'[A-Z]{2,}\d{3,}[A-Z]*', '', t) # Course codes like CS3491
                        t = re.sub(r'(Syllabus|Notes|Course|University|Credit|Instructor|Hours)$', '', t, flags=re.IGNORECASE)
                        t = re.sub(r'^[A-Z\d\.\-\s]+(?=[A-Z])', '', t) # Leading numbers/junk
                        t = re.sub(r'\s+', ' ', t).strip()
                        
                        if t and len(t) > 3 and not any(phrase in t.lower() for phrase in ["you said", "here are", "identified", "topics"]):
                            cleaned.append(t.capitalize())
                    return cleaned[:20]
        except Exception as e:
            print(f"Gemini topic extraction failed: {str(e)}")
            
    # Enhanced Fallback
    lines = text.split('\n')
    topics = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5: continue
        
        # Capture lines that look like topics
        if (re.match(r'^(UNIT|MODULE|CHAPTER|TOPIC|SECTION)\s', line, re.IGNORECASE) or 
            re.match(r'^[\d\.\-\*\•]+\s+[A-Z]', line) or 
            (line[0].isupper() and len(line) < 80)):
            
            t = re.sub(r'^[\d\.\-\*\•\s]+', '', line).strip()
            t = re.sub(r'^(UNIT|MODULE|CHAPTER|TOPIC|SECTION)\s*[\d\.\-\:]*\s*', '', t, flags=re.IGNORECASE)
            t = re.sub(r'[A-Z]{2,}\d{3,}[A-Z]*', '', t).strip()
            
            cleaned = t.capitalize()
            if cleaned and cleaned not in seen and len(cleaned) > 2:
                topics.append(cleaned)
                seen.add(cleaned)
    
    return topics[:20]

# ==========================================
# ⚙️ PROCESSOR (Self-contained)
# ==========================================

def analyze_dependencies(topics):
    """
    Builds a dependency graph. 
    1. Implicitly assumes sequential topics in the text are related.
    2. Uses Jaccard Similarity to find keywords overlaps.
    """
    graph = {topic: [] for topic in topics}
    tokens = [set(re.findall(r'\w+', t.lower())) for t in topics]
    
    # Keyword-based dependencies
    for i in range(len(topics)):
        for j in range(i + 1, len(topics)):
            if not tokens[i] or not tokens[j]: continue
            # If topics share significant words, assume dependency
            intersection = tokens[i].intersection(tokens[j])
            if len(intersection) >= 1:
                similarity = len(intersection) / len(tokens[i].union(tokens[j]))
                if similarity > 0.15:
                    graph[topics[i]].append(topics[j])
                    
    # Sequential context dependency (Topic N is often a prerequisite for N+1)
    for i in range(len(topics) - 1):
        if topics[i+1] not in graph[topics[i]]:
            graph[topics[i]].append(topics[i+1])
            
    return graph

def get_study_order(graph):
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            if neighbor in in_degree: in_degree[neighbor] += 1
    
    queue = [node for node in graph if in_degree[node] == 0]
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            if neighbor in in_degree:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0: queue.append(neighbor)
    
    if len(result) < len(graph):
        for node in graph:
            if node not in result: result.append(node)
    return result

# Teacher's Insights & Resources Mapping
MENTOR_TIPS = {
    "introduction": "Don't just memorize definitions. Try to understand the 'Why' behind this field.",
    "basic": "Strong foundations make complex topics easier. Spend extra time here if you're a beginner.",
    "neural": "Think of this as biological inspiration. Visualize the layers and connections.",
    "search": "Search algorithms are the heart of problem solving. Draw the search trees to visualize state space.",
    "heuristic": "Heuristics are 'rules of thumb'. Think about how they estimate cost to goals.",
    "logic": "Follow the flow step-by-step. Logical inference is about derivation from facts.",
    "algorithm": "Practice with small examples first. Complexity matters more than syntax.",
    "math": "Focus on the logic, not just the formulas. Use online calculators to verify.",
    "probabilistic": "Probability handles uncertainty. Focus on Bayes' rule and conditional independence.",
    "inference": "This is about drawing conclusions from data. It's the 'reasoning' part of AI.",
    "hard": "Break this into 3 smaller chunks. Don't try to finish it in one sitting.",
    "application": "Think about where you see this in your daily life like Google Maps or Siri."
}

def get_mentor_advice(topic):
    t_lower = topic.lower()
    for key, tip in MENTOR_TIPS.items():
        if key in t_lower: return tip
    return "Focus on understanding the core concepts through real-world examples and practice."

def get_resource_links(topic):
    query = topic.replace(' ', '+')
    return [
        {"name": "YouTube Tutorial", "url": f"https://www.youtube.com/results?search_query={query}+tutorial"},
        {"name": "GeeksforGeeks", "url": f"https://www.google.com/search?q={query}+geeksforgeeks"},
        {"name": "Lecture Notes", "url": f"https://www.google.com/search?q={query}+lecture+notes+pdf"},
        {"name": "Interview Prep", "url": f"https://www.google.com/search?q={query}+interview+questions"},
        {"name": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/{query}"}
    ]

def classify_topics_fully(ordered_topics):
    easy_keywords = ['introduction', 'basics', 'overview', 'concept', 'history', 'units', 'defintion', 'scope', 'applications']
    hard_keywords = ['advanced', 'neural', 'optimization', 'complex', 'inference', 'backpropagation', 'bayesian', 'deep', 'logic', 'calculus', 'integration', 'heuristics', 'probabilistic', 'adversarial', 'learning']
    
    topic_details = {}
    for topic in ordered_topics:
        score = 2  # Default Medium
        t_lower = topic.lower()
        if any(kw in t_lower for kw in easy_keywords): score = 1
        if any(kw in t_lower for kw in hard_keywords): score = 3
        
        topic_details[topic] = {
            "difficulty": score, 
            "advice": get_mentor_advice(topic),
            "resources": get_resource_links(topic)
        }
    return topic_details

def generate_schedule(ordered_topics, topic_details, weeks, hours, level):
    if level == "Beginner":
        weights = {1: 2.5, 2: 3, 3: 4}
    elif level == "Advanced":
        weights = {1: 0.5, 2: 1.5, 3: 3}
    else:  # Intermediate
        weights = {1: 1, 2: 2, 3: 3}
    
    topic_weights = [(t, weights.get(topic_details[t]["difficulty"], 2)) for t in ordered_topics]
    total_weight = sum(w for _, w in topic_weights) or 1
    weight_per_week = total_weight / weeks
    
    schedule = []
    curr_topics, curr_weight, w_num = [], 0, 1
    for topic, weight in topic_weights:
        curr_topics.append(topic)
        curr_weight += weight
        if curr_weight >= weight_per_week and w_num < weeks:
            schedule.append({"week": w_num, "topics": curr_topics})
            curr_topics, curr_weight, w_num = [], 0, w_num + 1
    
    if curr_topics:
        if w_num > weeks:
            schedule[-1]["topics"].extend(curr_topics)
        else:
            schedule.append({"week": w_num, "topics": curr_topics})
    return schedule

def chat_with_mentor(topic, message):
    model = get_gemini()
    if model:
        try:
            prompt = f"""
            You are a friendly and expert academic mentor. 
            The student is studying "{topic}" and has a doubt.
            
            Student Question: "{message}"
            
            Provide a helpful, encouraging, and technically accurate response in 2-3 sentences.
            If the question is unrelated to the topic, gently guide them back to studying.
            """
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            print(f"Chat error: {str(e)}")
    return f"Focus on understanding the core concepts of {topic} through practice. Try checking the resources provided!"

# ==========================================
# 🌐 ROUTES
# ==========================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "API is running!", "timestamp": "2026-02-17"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    return jsonify({"response": chat_with_mentor(data.get('topic', 'General'), data.get('message', ''))})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Path not found", "path": request.path}), 404

# Determine the absolute path for uploads folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/analyze', methods=['POST'])
def analyze_syllabus():
    try:
        print("📥 Received analyze request")
        if 'file' not in request.files: 
            print("❌ No file in request")
            return jsonify({"error": "No file"}), 400
        file = request.files['file']
        if not file.filename: 
            print("❌ No filename")
            return jsonify({"error": "No filename"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"💾 Saving file to {filepath}")
        file.save(filepath)
        
        print("📄 Extracting text...")
        raw_text = extract_text_from_pdf(filepath) if filename.endswith('.pdf') else open(filepath, 'r', errors='ignore').read()
        cleaned_text = clean_text(raw_text)
        
        print("🤖 Identifying topics via Gemini...")
        topics = identify_topics(cleaned_text)
        if not topics:
            print("⚠️ No topics extracted, using fallback...")
            topics = ["Introduction", "Core Concepts", "Advanced Modules", "Conclusion"]
            
        print(f"📊 Analyzing dependencies for {len(topics)} topics...")
        G = analyze_dependencies(topics)
        ordered_topics = get_study_order(G)
        
        print("🏷️ Classifying topics...")
        topic_details = classify_topics_fully(ordered_topics)
        
        print("📅 Generating schedule...")
        schedule = generate_schedule(ordered_topics, topic_details, 
                                     int(request.form.get('weeks', 4)), 
                                     int(request.form.get('hours', 10)), 
                                     request.form.get('level', 'Beginner'))
        
        nodes = [{"id": n, "group": topic_details[n]["difficulty"]} for n in G]
        links = [{"source": u, "target": v} for u in G for v in G[u]]
        
        print("✅ Analysis complete!")
        return jsonify({
            "topics": ordered_topics,
            "topic_details": topic_details,
            "schedule": schedule,
            "graph": {"nodes": nodes, "links": links},
            "mentor_summary": f"I've analyzed your content and created a {len(schedule)}-week strategic roadmap!"
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"🔥 Server Error: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"error": error_msg, "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
