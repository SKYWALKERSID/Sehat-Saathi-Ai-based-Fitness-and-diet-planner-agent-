import os
import json
import joblib

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rag')
FAISS_DIR = os.path.join(RAG_DIR, 'faiss')

# Hardcoded knowledge base as fallback if FAISS index is not built
FALLBACK_KB = [
    {
        "title": "WHO Physical Activity Guidelines",
        "content": "The World Health Organization (WHO) recommends that adults aged 18-64 should perform at least 150-300 minutes of moderate-intensity aerobic physical activity, or 75-150 minutes of vigorous-intensity aerobic physical activity per week. They also recommend muscle-strengthening activities involving major muscle groups on 2 or more days a week. Regular exercise helps prevent and manage noncommunicable diseases such as heart disease, type-2 diabetes, and cancer.",
        "category": "WHO standards"
    },
    {
        "title": "Diabetic Fitness and Nutrition Guide",
        "content": "For diabetic users, diet and exercise are key pillars of glycemic management. Focus on complex, low-glycemic index carbohydrates (like oats, brown rice, and vegetables) that cause gradual blood glucose elevations. High-protein foods (chicken, paneer, tofu) help stabilize satiety. Incorporating regular strength training (2-3 days a week) improves insulin sensitivity and increases muscle glucose uptake.",
        "category": "Diabetes"
    },
    {
        "title": "Hypertension Cardio Safety Standards",
        "content": "Hypertensive individuals must practice safety-first physical training. Avoid maximal weightlifting movements that induce the Valsalva maneuver (extreme breath-holding), as this spikes blood pressure. Focus instead on steady-state cardiovascular conditioning (cycling, brisk walking, swimming) and high-repetition, lower-resistance circuit routines. Keep sodium intake under 2,000mg per day.",
        "category": "Hypertension"
    },
    {
        "title": "Muscle Hypertrophy and Progressive Overload",
        "content": "To build muscle tissue, training must incorporate progressive overload (gradually increasing weight, reps, or sets). Ensure daily protein intake is in the range of 1.6 to 2.2 grams per kilogram of bodyweight, partitioned across 3 to 5 meals. Sleep is critical: during deep sleep phases, growth hormone releases, enabling muscle fiber repair and recovery.",
        "category": "Hypertrophy"
    },
    {
        "title": "Hydration and Electrolyte Balance",
        "content": "Hydration needs scale dynamically with environment and sweat rates. Standard bodies require 35ml of water per kg of weight. In ambient temperatures exceeding 30C, scale water intake by an extra 0.5 to 1.5 Liters. Ensure moderate sodium, potassium, and magnesium intake during high-sweat sessions to avoid hyponatremia and cramping.",
        "category": "Hydration"
    }
]

def query_rag_knowledge_base(query: str, top_k: int = 3) -> dict:
    """
    RAG MCP: Query the local FAISS index for relevant health and fitness research.
    Falls back to a clean python-based TF-IDF search if FAISS files are not yet built.
    """
    query_clean = str(query).strip().lower()
    
    index_path = os.path.join(FAISS_DIR, 'index.bin')
    chunks_path = os.path.join(FAISS_DIR, 'chunks.json')
    vectorizer_path = os.path.join(FAISS_DIR, 'vectorizer.pkl')
    
    # Check if FAISS files exist
    if os.path.exists(index_path) and os.path.exists(chunks_path) and os.path.exists(vectorizer_path):
        try:
            import faiss
            
            # Load FAISS structures
            index = faiss.read_index(index_path)
            with open(chunks_path, 'r') as f:
                chunks = json.load(f)
            vectorizer = joblib.load(vectorizer_path)
            
            # Vectorize query
            query_vec = vectorizer.transform([query_clean]).toarray().astype('float32')
            
            # Query index
            distances, indices = index.search(query_vec, top_k)
            
            results = []
            for idx, rank_idx in enumerate(indices[0]):
                if rank_idx < len(chunks) and rank_idx >= 0:
                    results.append({
                        "title": chunks[rank_idx]["title"],
                        "content": chunks[rank_idx]["content"],
                        "category": chunks[rank_idx].get("category", "General"),
                        "score": float(distances[0][idx])
                    })
                    
            if results:
                return {
                    "query": query,
                    "search_type": "FAISS Index",
                    "results": results
                }
        except Exception as e:
            print(f"FAISS search failed: {e}. Falling back to clean python matcher.")
            
    # Substring / Bag-of-words keyword matcher fallback
    results = []
    query_words = set(query_clean.split())
    
    for doc in FALLBACK_KB:
        score = 0
        doc_content = doc["content"].lower()
        doc_title = doc["title"].lower()
        
        # Simple scoring
        for word in query_words:
            if word in doc_content:
                score += 1
            if word in doc_title:
                score += 3
                
        if score > 0:
            results.append({
                "title": doc["title"],
                "content": doc["content"],
                "category": doc["category"],
                "score": float(score)
            })
            
    # Sort results
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
    
    # If no keywords matched, return top fallback items
    if not results:
        results = [{
            "title": doc["title"],
            "content": doc["content"],
            "category": doc["category"],
            "score": 0.0
        } for doc in FALLBACK_KB[:top_k]]
        
    return {
        "query": query,
        "search_type": "Sub-string Fallback Engine",
        "results": results
    }
