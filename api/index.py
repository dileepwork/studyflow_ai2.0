from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename

# Ensure the 'api' directory is in the path for serverless imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

app = Flask(__name__)
CORS(app)

# Lazy imports - only import when needed to avoid cold start issues
def get_dependencies():
    try:
        # Try importing as package first (works on Vercel)
        try:
            from api import utils, processor
            print("✅ Imported via 'from api import ...'")
        except ImportError:
            # Fallback to direct import (works locally)
            import utils
            import processor
            print("✅ Imported via 'import ...' fallback")
            
        return {
            'extract_text_from_pdf': utils.extract_text_from_pdf,
            'clean_text': utils.clean_text,
            'identify_topics': utils.identify_topics,
            'analyze_dependencies': processor.analyze_dependencies,
            'get_study_order': processor.get_study_order,
            'classify_topics_fully': processor.classify_topics_fully,
            'generate_schedule': processor.generate_schedule,
            'chat_with_mentor': processor.chat_with_mentor,
        }
    except Exception as e:
        print(f"❌ Failed to import dependencies: {str(e)}")
        import traceback
        traceback.print_exc()
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


@app.route('/api/debug', methods=['GET'])
def debug():
    import os
    import sys
    return jsonify({
        "cwd": os.getcwd(),
        "sys_path": sys.path,
        "files_in_cwd": os.listdir(os.getcwd()),
        "files_in_api": os.listdir(os.path.join(os.getcwd(), 'api')) if os.path.exists(os.path.join(os.getcwd(), 'api')) else "api folder missing",
        "file_location": __file__,
        "dirname_file": os.path.dirname(__file__),
        "files_in_dirname": os.listdir(os.path.dirname(__file__))
    })

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
        # G is now a dict {topic: [neighbors]}
        graph_nodes = []
        graph_links = []
        for node in G:
            graph_nodes.append({
                "id": node, 
                "group": topic_details.get(node, {}).get("difficulty", 2)
            })
            for neighbor in G.get(node, []):
                graph_links.append({"source": node, "target": neighbor})
        
        graph_data = {
            "nodes": graph_nodes,
            "links": graph_links
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
