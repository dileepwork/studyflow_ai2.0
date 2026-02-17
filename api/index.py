from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import re
import json
import pypdf
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
CORS(app)

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
            prompt = f"Extract distinct topics from this syllabus text as a JSON array of strings. Return ONLY JSON. Syllabus:\n{text[:3000]}"
            response = model.generate_content(prompt)
            topics = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            if isinstance(topics, list) and len(topics) > 0:
                return topics
        except Exception as e:
            print(f"Gemini topic extraction failed: {str(e)}")
            
    # Fallback
    print("⚠️ Using Fallback Regex for Topic Extraction")
    lines = text.split('\n')
    topics = []
    seen = set()
    for line in lines:
        line = line.strip()
        # Allow shorter lines (e.g. "BFS", "DFS", "Math") - heavily relaxed constraint
        if not line or len(line) < 3: 
            continue
            
        # Skip likely non-topics (dates, page numbers, etc)
        if re.match(r'^\d+$', line) or re.match(r'^page\s+\d+', line, re.IGNORECASE):
            continue
            
        if re.match(r'^(UNIT|MODULE|CHAPTER)\s', line, re.IGNORECASE) or len(line) < 100:
            cleaned = re.sub(r'^[\d\.\)\-\*]+', '', line).strip()
            if cleaned and cleaned not in seen and len(cleaned) > 2:
                topics.append(cleaned)
                seen.add(cleaned)
                
    print(f"Fallback extracted {len(topics)} topics: {topics[:5]}...")
    return topics[:20]

# ==========================================
# ⚙️ PROCESSOR (Self-contained)
# ==========================================

def analyze_dependencies(topics):
    graph = {topic: [] for topic in topics}
    tokens = [set(re.findall(r'\w+', t.lower())) for t in topics]
    
    for i in range(len(topics)):
        for j in range(i + 1, len(topics)):
            if not tokens[i] or not tokens[j]: continue
            similarity = len(tokens[i].intersection(tokens[j])) / len(tokens[i].union(tokens[j]))
            if similarity > 0.2:
                graph[topics[i]].append(topics[j])
                
    current_unit = None
    for topic in topics:
        if re.match(r'^(UNIT|MODULE|CHAPTER)', topic, re.IGNORECASE):
            current_unit = topic
        elif current_unit:
            graph[current_unit].append(topic)
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

MENTOR_TIPS = {
    "introduction": "Understand the basics first.",
    "neural": "Visualize the layers.",
    "algorithm": "Practice small examples.",
    "math": "Focus on the logic."
}

def get_mentor_advice(topic):
    t_lower = topic.lower()
    for key, tip in MENTOR_TIPS.items():
        if key in t_lower: return tip
    return "Focus on real-world applications."

def classify_topics_fully(ordered_topics):
    topic_details = {}
    for topic in ordered_topics:
        topic_details[topic] = {
            "difficulty": 2, 
            "advice": get_mentor_advice(topic),
            "resources": [
                {"name": "YouTube", "url": f"https://www.youtube.com/results?search_query={topic.replace(' ','+')}"},
                {"name": "Tutorial", "url": f"https://www.google.com/search?q={topic.replace(' ','+')}+tutorial"}
            ]
        }
    return topic_details

def generate_schedule(ordered_topics, topic_details, weeks, hours, level):
    weights = {1: 1, 2: 2, 3: 3}
    if level == "Beginner": weights = {1: 2, 2: 3, 3: 4}
    
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
    if curr_topics: schedule.append({"week": w_num, "topics": curr_topics})
    return schedule

def chat_with_mentor(topic, message):
    model = get_gemini()
    if model:
        try:
            prompt = f"As a mentor for {topic}, answer briefly: {message}"
            return model.generate_content(prompt).text.strip()
        except: pass
    return f"Focus on understanding the core concepts of {topic} through practice."

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

UPLOAD_FOLDER = '/tmp'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/analyze', methods=['POST'])
def analyze_syllabus():
    try:
        if 'file' not in request.files: return jsonify({"error": "No file"}), 400
        file = request.files['file']
        if not file.filename: return jsonify({"error": "No filename"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        raw_text = extract_text_from_pdf(filepath) if filename.endswith('.pdf') else open(filepath, 'r', errors='ignore').read()
        cleaned_text = clean_text(raw_text)
        topics = identify_topics(cleaned_text)
        G = analyze_dependencies(topics)
        ordered_topics = get_study_order(G)
        topic_details = classify_topics_fully(ordered_topics)
        schedule = generate_schedule(ordered_topics, topic_details, 
                                     int(request.form.get('weeks', 4)), 
                                     int(request.form.get('hours', 10)), 
                                     request.form.get('level', 'Beginner'))
        
        nodes = [{"id": n, "group": topic_details[n]["difficulty"]} for n in G]
        links = [{"source": u, "target": v} for u in G for v in G[u]]
        
        return jsonify({
            "topics": ordered_topics,
            "topic_details": topic_details,
            "schedule": schedule,
            "graph": {"nodes": nodes, "links": links},
            "mentor_summary": "Path generated successfully!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
