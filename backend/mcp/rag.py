import os
import json
import joblib
import numpy as np

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rag')
FAISS_DIR = os.path.join(RAG_DIR, 'faiss')

# Curated clinical knowledge base used to build and query the FAISS index
CLINICAL_KB = [
    {
        "title": "WHO Physical Activity Guidelines",
        "content": "The World Health Organization (WHO) recommends that adults aged 18-64 should perform at least 150-300 minutes of moderate-intensity aerobic physical activity, or 75-150 minutes of vigorous-intensity aerobic physical activity per week. They also recommend muscle-strengthening activities involving major muscle groups on 2 or more days a week. Regular exercise helps prevent and manage noncommunicable diseases such as heart disease, type-2 diabetes, and cancer.",
        "category": "WHO standards"
    },
    {
        "title": "Diabetic Fitness and Nutrition Guide",
        "content": "For diabetic users, diet and exercise are key pillars of glycemic management. Focus on complex, low-glycemic index carbohydrates (like oats, brown rice, quinoa, and non-starchy vegetables) that cause gradual blood glucose elevations. High-protein foods (chicken, paneer, tofu, lentils) help stabilize satiety. Incorporating regular strength training (2-3 days a week) improves insulin sensitivity and increases GLUT4 muscle glucose uptake.",
        "category": "Diabetes"
    },
    {
        "title": "Hypertension Cardio Safety Standards",
        "content": "Hypertensive individuals must practice safety-first physical training. Avoid maximal weightlifting movements that induce the Valsalva maneuver (extreme breath-holding during heavy deadlifts or overhead presses), as this spikes arterial blood pressure. Focus instead on steady-state cardiovascular conditioning (cycling, brisk walking, swimming) and controlled-tempo resistance training. Keep sodium intake under 2,000mg per day.",
        "category": "Hypertension"
    },
    {
        "title": "Muscle Hypertrophy and Progressive Overload",
        "content": "To build muscle tissue, training must incorporate progressive overload (gradually increasing load, reps, or sets over time). Ensure daily protein intake is in the range of 1.6 to 2.2 grams per kilogram of bodyweight, partitioned across 3 to 5 meals. Sleep is critical: during deep sleep phases, growth hormone releases, enabling muscle fiber repair and myofibrillar protein synthesis.",
        "category": "Hypertrophy"
    },
    {
        "title": "Hydration and Electrolyte Balance",
        "content": "Hydration needs scale dynamically with environment and sweat rates. Standard bodies require 35ml of water per kg of weight. In ambient temperatures exceeding 30C, scale water intake by an extra 0.5 to 1.5 Liters. Ensure moderate sodium, potassium, and magnesium intake during high-sweat sessions to avoid hyponatremia and neuromuscular cramping.",
        "category": "Hydration"
    },
    {
        "title": "Joint-Friendly Modifications for Knee, Back & Shoulder Injuries",
        "content": "When managing knee osteoarthritis or ligament strain, replace high-axial-load squats and impact running with swimming, stationary cycling, and glute bridges. For lumbar spine pain, eliminate conventional deadlifts in favor of chest-supported rows and bird-dogs. For rotator cuff or shoulder impingement, avoid overhead pressing and substitute core stabilization planks and neutral-grip pulling.",
        "category": "Injury Rehabilitation"
    },
    {
        "title": "Sustainable Fat Loss and Caloric Deficit Physiology",
        "content": "Healthy, sustainable fat loss requires a moderate caloric deficit of 350 to 500 kcal below Total Daily Energy Expenditure (TDEE), yielding roughly 0.4 to 0.7 kg of fat loss per week. Deficits exceeding 1,000 kcal/day risk lean muscle catabolism, metabolic adaptation, and hormonal disruption. Pairing high protein intake (30-35% of calories) with resistance training preserves lean mass during weight loss.",
        "category": "Weight Loss"
    },
    {
        "title": "Indian Vegetarian, Vegan, and Jain Protein Optimization",
        "content": "Plant-based and Indian vegetarian diets can achieve complete amino acid profiles by combining complementary protein sources: lentils (moong/chana dal) with whole grains (brown rice/roti), soy products (firm tofu, tempeh), dairy (low-fat paneer, Greek yogurt, whey isolate), and seeds/nuts (almonds, walnuts, chia seeds). Jain diets exclude root vegetables (onion, garlic, potato) while utilizing paneer, lentils, quinoa, and leafy greens.",
        "category": "Nutrition"
    }
]

FALLBACK_KB = CLINICAL_KB


def ensure_faiss_index() -> bool:
    """Builds the local FAISS index and TF-IDF vectorizer if not already present on disk."""
    index_path = os.path.join(FAISS_DIR, 'index.bin')
    chunks_path = os.path.join(FAISS_DIR, 'chunks.json')
    vectorizer_path = os.path.join(FAISS_DIR, 'vectorizer.pkl')

    if os.path.exists(index_path) and os.path.exists(chunks_path) and os.path.exists(vectorizer_path):
        return True

    try:
        import faiss
        from sklearn.feature_extraction.text import TfidfVectorizer

        os.makedirs(FAISS_DIR, exist_ok=True)
        corpus = [f"{doc['title']} {doc['category']} {doc['content']}".lower() for doc in CLINICAL_KB]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus).toarray().astype('float32')

        # Normalize for cosine similarity via L2 distance
        faiss.normalize_L2(tfidf_matrix)
        dim = tfidf_matrix.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(tfidf_matrix)

        faiss.write_index(index, index_path)
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(CLINICAL_KB, f, indent=2)
        joblib.dump(vectorizer, vectorizer_path)
        return True
    except Exception as e:
        print(f"Could not auto-build FAISS index: {e}")
        return False


def query_rag_knowledge_base(query: str, top_k: int = 3) -> dict:
    """
    RAG MCP: Query the local FAISS index for relevant health and fitness research.
    Automatically builds the FAISS index on first run if needed.
    """
    query_clean = str(query).strip().lower()
    
    index_path = os.path.join(FAISS_DIR, 'index.bin')
    chunks_path = os.path.join(FAISS_DIR, 'chunks.json')
    vectorizer_path = os.path.join(FAISS_DIR, 'vectorizer.pkl')
    
    ensure_faiss_index()

    # Check if FAISS files exist
    if os.path.exists(index_path) and os.path.exists(chunks_path) and os.path.exists(vectorizer_path):
        try:
            import faiss
            
            # Load FAISS structures
            index = faiss.read_index(index_path)
            with open(chunks_path, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            vectorizer = joblib.load(vectorizer_path)
            
            # Vectorize query
            query_vec = vectorizer.transform([query_clean]).toarray().astype('float32')
            if np.linalg.norm(query_vec) > 0:
                faiss.normalize_L2(query_vec)
            
            # Query index
            distances, indices = index.search(query_vec, top_k)
            
            results = []
            for idx, rank_idx in enumerate(indices[0]):
                if 0 <= rank_idx < len(chunks):
                    results.append({
                        "title": chunks[rank_idx]["title"],
                        "content": chunks[rank_idx]["content"],
                        "category": chunks[rank_idx].get("category", "General"),
                        "score": round(float(distances[0][idx]), 4)
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
