from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Lazy imports - only import when needed to avoid cold start issues
def get_dependencies():
    try:
        from utils import extract_text_from_pdf, clean_text, identify_topics
        from processor import analyze_dependencies, get_study_order, classify_topics_fully, generate_schedule, chat_with_mentor
        import networkx as nx
        return {
            'extract_text_from_pdf': extract_text_from_pdf,
            'clean_text': clean_text,
            'identify_topics': identify_topics,
            'analyze_dependencies': analyze_dependencies,
            'get_study_order': get_study_order,
            'classify_topics_fully': classify_topics_fully,
            'generate_schedule': generate_schedule,
            'chat_with_mentor': chat_with_mentor,
            'nx': nx
        }
    except Exception as e:
        print(f"❌ Failed to import dependencies: {str(e)}")
        raise

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "API is running!",
        "timestamp": "2026-02-17"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        deps = get_dependencies()
        data = request.json
        topic = data.get('topic')
        message = data.get('message')
        response = deps['chat_with_mentor'](topic, message)
        return jsonify({"response": response})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

UPLOAD_FOLDER = '/tmp'
# Ensure the upload folder exists
try:
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"✅ Upload folder created: {UPLOAD_FOLDER}")
except Exception as e:
    print(f"⚠️  Upload folder issue (may already exist): {str(e)}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/api/analyze', methods=['POST'])
def analyze_syllabus():
    try:
        # Import dependencies here to avoid cold start issues
        deps = get_dependencies()
        
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        config = {
            "weeks": int(request.form.get('weeks', 4)),
            "hours": int(request.form.get('hours', 10)),
            "level": request.form.get('level', 'Beginner')
        }
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Extraction
        if filename.endswith('.pdf'):
            raw_text = deps['extract_text_from_pdf'](filepath)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
                
        # 2. Cleaning
        cleaned_text = deps['clean_text'](raw_text)
        
        # 3. Topic Identification
        topics = deps['identify_topics'](cleaned_text)
        
        # 4. Dependency Analysis
        G = deps['analyze_dependencies'](topics)
        
        # 5. Sorting
        ordered_topics = deps['get_study_order'](G)
        
        # 6. Full Topic Analysis (Difficulty, Advice, Resources)
        topic_details = deps['classify_topics_fully'](ordered_topics)
        
        # 7. Adaptive Schedule Generation
        schedule = deps['generate_schedule'](ordered_topics, topic_details, config['weeks'], config['hours'], config['level'])
        
        # Prepare graph data for visualization
        graph_data = {
            "nodes": [{"id": node, "group": topic_details.get(node, {}).get("difficulty", 2)} for node in G.nodes()],
            "links": [{"source": u, "target": v} for u, v in G.edges()]
        }
        
        return jsonify({
            "topics": ordered_topics,
            "topic_details": topic_details,
            "schedule": schedule,
            "graph": graph_data,
            "mentor_summary": f"Based on your {config['level']} level, I've created a path that focuses more on { 'foundations' if config['level'] == 'Beginner' else 'advanced optimization' if config['level'] == 'Advanced' else 'balanced learning' }."
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()
        print("❌ ERROR in analyze_syllabus:")
        print(error_msg)
        print(trace)
        return jsonify({
            "error": error_msg, 
            "traceback": trace
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
