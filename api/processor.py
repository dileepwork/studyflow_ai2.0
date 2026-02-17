import re
import json
import os

def get_gemini():
    """Lazy load Gemini"""
    try:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"❌ Gemini load failed: {str(e)}")
        raise

def analyze_dependencies(topics):
    """
    Lightweight dependency analysis using string similarity.
    Replaces networkx with simple dict-based graph.
    """
    graph = {topic: [] for topic in topics}
    
    # Pre-tokenize topics for similarity
    def get_tokens(text):
        return set(re.findall(r'\w+', text.lower()))

    topic_tokens = [get_tokens(t) for t in topics]

    if len(topics) > 1:
        for i in range(len(topics)):
            for j in range(i + 1, len(topics)):
                # Jaccard Similarity
                set_i = topic_tokens[i]
                set_j = topic_tokens[j]
                
                if not set_i or not set_j:
                    continue
                
                intersection = len(set_i.intersection(set_j))
                union = len(set_i.union(set_j))
                similarity = intersection / union if union > 0 else 0
                
                # If topics are similar, assume earlier one is prerequisite
                if similarity > 0.2:
                    graph[topics[i]].append(topics[j])

    # Unit-based dependency
    current_unit = None
    for topic in topics:
        if re.match(r'^(UNIT|MODULE|CHAPTER)\s+[IVX\d]+', topic, re.IGNORECASE):
            current_unit = topic
        elif current_unit and current_unit in graph:
            graph[current_unit].append(topic)

    return graph

def get_study_order(graph):
    """
    Simple topological sort without networkx.
    """
    # Calculate in-degrees
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            if neighbor in in_degree:
                in_degree[neighbor] += 1
    
    # Queue of nodes with no dependencies
    queue = [node for node in graph if in_degree[node] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor in in_degree:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
    
    # If not all nodes processed (cycle detected), add remaining
    if len(result) < len(graph):
        for node in graph:
            if node not in result:
                result.append(node)
    
    return result

# Teacher's Insights & Resources Mapping
MENTOR_TIPS = {
    "introduction": "Don't just memorize definitions. Try to understand the 'Why' behind this field.",
    "basic": "Strong foundations make complex topics easier. Spend extra time here if you're a beginner.",
    "neural": "Think of this as biological inspiration. Visualize the layers and connections.",
    "search": "Algorithms are like recipes. Trace them on paper before coding.",
    "algorithm": "Practice with small examples first. Complexity matters more than syntax.",
    "math": "Focus on the logic, not just the formulas. Use online calculators to verify.",
    "code": "Don't just copy. Type every line and see it fail, then fix it.",
    "hard": "Break this into 3 smaller chunks. Don't try to finish it in one sitting.",
    "exam": "Focus on the core concepts. Past papers are your best friend here."
}

def get_mentor_advice(topic):
    topic_lower = topic.lower()
    for key, tip in MENTOR_TIPS.items():
        if key in topic_lower:
            return tip
    return "Study this topic with a focus on its real-world applications."

def get_resource_links(topic):
    # Generates helpful search links for the student
    query = topic.replace(' ', '+')
    return [
        {"name": "YouTube Tutorial", "url": f"https://www.youtube.com/results?search_query={query}+tutorial"},
        {"name": "GeeksforGeeks", "url": f"https://www.google.com/search?q={query}+geeksforgeeks"},
        {"name": "University Notes", "url": f"https://www.google.com/search?q={query}+lecture+notes+pdf"},
        {"name": "Interview Prep", "url": f"https://www.google.com/search?q={query}+interview+questions+answers"},
        {"name": "Documentation/Wiki", "url": f"https://en.wikipedia.org/wiki/{query}"}
    ]

def classify_topics_fully(ordered_topics):
    easy_keywords = ['introduction', 'basics', 'overview', 'concept', 'history', 'units']
    hard_keywords = ['advanced', 'neural', 'optimization', 'complex', 'inference', 'backpropagation', 'bayesian', 'deep', 'logic']
    
    topic_details = {}
    for topic in ordered_topics:
        score = 2  # Default Medium
        t_lower = topic.lower()
        
        if any(kw in t_lower for kw in easy_keywords):
            score = 1
        elif any(kw in t_lower for kw in hard_keywords):
            score = 3
        
        topic_details[topic] = {
            "difficulty": score,
            "advice": get_mentor_advice(topic),
            "resources": get_resource_links(topic)
        }
    return topic_details

def generate_schedule(ordered_topics, topic_details, total_weeks, hours_per_week, student_level="Beginner"):
    """
    Adaptive Scheduling:
    - Beginner: Spends 50% more time on foundations (Difficulty 1).
    - Advanced: Spends 30% less time on basics and jumps to Hard topics faster.
    """
    # Adjust weights based on student level
    if student_level == "Beginner":
        weights = {1: 2.5, 2: 3, 3: 4}  # Extra time for foundations
    elif student_level == "Advanced":
        weights = {1: 0.5, 2: 1.5, 3: 3}  # Skip basics, focus on hard
    else:  # Intermediate
        weights = {1: 1, 2: 2, 3: 3}
    
    topic_weights = [(t, weights[topic_details[t]["difficulty"]]) for t in ordered_topics]
    total_weight = sum(w for _, w in topic_weights)
    
    if total_weight == 0:
        total_weight = 1
    
    weight_per_week = total_weight / total_weeks
    
    schedule = []
    current_week_topics = []
    current_week_weight = 0
    week_num = 1
    
    for topic, weight in topic_weights:
        current_week_topics.append(topic)
        current_week_weight += weight
        
        # Determine if we should close the week
        if current_week_weight >= weight_per_week and week_num < total_weeks:
            schedule.append({
                "week": week_num,
                "topics": current_week_topics
            })
            current_week_topics = []
            current_week_weight = 0
            week_num += 1
            
    # Add remaining topics to last week
    if current_week_topics:
        if week_num > total_weeks:
            schedule[-1]["topics"].extend(current_week_topics)
        else:
            schedule.append({
                "week": week_num,
                "topics": current_week_topics
            })
            
    return schedule

def chat_with_mentor(topic, user_message):
    """
    AI-powered mentor chat using Gemini API.
    """
    try:
        model = get_gemini()
        
        prompt = f"""
You are a friendly AI study mentor helping a student understand "{topic}".

Student's question: {user_message}

Provide a helpful, concise response (2-3 sentences max) that:
1. Answers their question directly
2. Relates to the topic "{topic}"
3. Encourages them with practical advice
4. Uses simple, clear language

Response:
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"⚠️ Gemini chat failed: {str(e)}, using fallback")
        return fallback_chat_response(topic, user_message)

def fallback_chat_response(topic, user_message):
    """Fallback chat responses without API"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["hello", "hi", "hey"]):
        return f"Hi there! I'm ready to help you master {topic}. What's on your mind?"
    
    if any(word in message_lower for word in ["what is", "define", "explain", "understand"]):
        return f"To understand {topic}, think of it as a way to solve problems systematically. It's often broken down into smaller, simpler steps. Check the resource links for detailed explanations!"
        
    if "example" in message_lower:
        return f"A great example of {topic} is how modern systems solve real-world problems efficiently. The resources I've provided have excellent examples with visuals."

    if any(word in message_lower for word in ["hard", "difficult", "confused", "stuck"]):
        return f"Don't worry, {topic} can be challenging. I recommend starting with the YouTube tutorial I provided. Focus on understanding the basic concept first, then dive into details."

    return f"That's a great question about {topic}! Check the GeeksforGeeks link in your resources for detailed examples and explanations. Practice problems really help solidify understanding."
