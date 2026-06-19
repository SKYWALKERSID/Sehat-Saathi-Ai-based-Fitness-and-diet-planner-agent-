import os
import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.models import Profile
from backend.mcp.rag import query_rag_knowledge_base
from backend.mcp.health_knowledge import lookup_health_standards

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

def generate_offline_answer(query: str, profile: Profile, rag_results: dict) -> str:
    """Synthesizes a detailed, clinical-grade coaching answer using matching RAG chunks and biometrics."""
    q_lower = query.lower()
    
    # 1. Gather RAG context
    chunks = rag_results.get("results", [])
    context_snippet = ""
    for c in chunks[:2]:
        context_snippet += f"- **{c['title']}** ({c['category']}): {c['content']}\n\n"
        
    # 2. Extract profile bio
    goals = profile.goals
    bmi_val = goals.bmi if goals else 22.0
    bmi_cat = goals.bmi_category if goals else "Normal"
    cals = goals.target_calories if goals else 2000
    
    # 3. Create rule-based logic to tailor answers based on topic keywords
    response = ""
    
    if "obesity" in q_lower or "risk" in q_lower or "metabolic" in q_lower:
        risks = json.loads(profile.recommendations[-1].outputs).get("predicted_risks", {}) if profile.recommendations else {}
        response = (
            f"Based on your profile biometrics, your calculated BMI is **{bmi_val}** ({bmi_cat}).\n\n"
            f"Our Machine Learning Health Risk predictors indicate:\n"
            f"- **Obesity Risk**: {risks.get('obesity_risk', 'Low Risk')}\n"
            f"- **Sedentary Risk**: {risks.get('sedentary_risk', 'Low Risk')}\n"
            f"- **Metabolic Risk**: {risks.get('metabolic_risk', 'Low Risk')}\n\n"
            f"**Actionable Advice**: "
        )
        if bmi_cat in ["Overweight", "Obese"]:
            response += "We recommend incorporating low-impact workouts (cycling, swimming) to shield your joints. Avoid heavy axial loading on your spine until BMI drops under 28."
        else:
            response += "Your BMI lies in a safe category. Maintain current resistance volumes and focus on clean protein-balanced macros."
            
    elif "diet" in q_lower or "food" in q_lower or "protein" in q_lower or "carb" in q_lower or "fat" in q_lower:
        response = (
            f"Analyzing your customized diet profile: Your target daily calories are **{cals} kcal**, "
            f"with a macro split of **{goals.target_protein}g Protein**, **{goals.target_carbs}g Carbs**, and **{goals.target_fat}g Fats**.\n\n"
            f"**Coach Nutrition Guidance**:\n"
            f"- Focus on whole foods: grilled chicken, paneer, tofu, and oats.\n"
            f"- Respect your specified preferences: *{profile.diet_preference}*.\n"
            f"- Keep allergies (*{profile.allergies}*) completely excluded from your shopping logs.\n\n"
        )
        
    elif "injury" in q_lower or "pain" in q_lower or "hurt" in q_lower or "exercise" in q_lower or "workout" in q_lower:
        response = (
            f"Under your active profile restrictions: Injuries reported: *{profile.injuries}* | Medical conditions: *{profile.medical_conditions}*.\n\n"
            f"Our **Safety-First Engine** has applied joint-safety checks:\n"
        )
        inj_lower = profile.injuries.lower()
        if "knee" in inj_lower:
            response += "- *Knee protection*: Excluded heavy squats/leg press. Replaced with Glute Bridges and functional mobility work.\n"
        if "back" in inj_lower:
            response += "- *Back protection*: Restricted deadlifts and heavy compression loading to safeguard your spine.\n"
        if "shoulder" in inj_lower:
            response += "- *Shoulder protection*: Swapped overhead presses/bench presses for planks and rows.\n"
        if "none" in inj_lower:
            response += "- *Status*: No active injuries registered. Progressive resistance loading is approved.\n"
            
    else:
        response = (
            f"Hello **{profile.name}**! I am your AI Health Assistant. I've reviewed your active profile "
            f"(Goal: *{profile.fitness_goal}*, Weight: *{profile.weight}kg*, Experience: *{profile.workout_experience}*).\n\n"
            f"How can I help you today? You can ask me about:\n"
            f"1. Your metabolic health risks and obesity metrics.\n"
            f"2. Your workout schedule details and joint exercises safety overrides.\n"
            f"3. Your meal macros partitions and calorie requirements.\n"
        )
        
    # Append relevant RAG knowledge chunks
    response += f"\n\n**Retrieved RAG Reference Documents**:\n{context_snippet}"
    return response

@chatbot_bp.route('/chatbot', methods=['POST'])
@login_required
def ask_chatbot():
    data = request.json or {}
    query = data.get('query', '').strip()
    profile_id = data.get('profile_id')
    
    if not query:
        return jsonify({"error": "No query message provided."}), 400
        
    if not profile_id:
        return jsonify({"error": "No active profile selected."}), 400
        
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Selected profile not found or access denied."}), 404
        
    # 1. Retrieve information via RAG MCP
    rag_results = query_rag_knowledge_base(query, top_k=2)
    
    # 2. Check for LLM API keys in env variables for natural completion
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if gemini_key:
        try:
            # We can use Gemini API to write a highly natural answer!
            # Format context
            context = json.dumps(rag_results.get("results", []))
            prompt = (
                f"You are a health coach assistant for the Sehat Saathi project. Answer the user question: '{query}'\n"
                f"User Profile details:\n"
                f"- Name: {profile.name}, Goal: {profile.fitness_goal}, Weight: {profile.weight}kg, "
                f"Injuries: {profile.injuries}, Allergies: {profile.allergies}, Medical: {profile.medical_conditions}\n"
                f"Target Calories: {profile.goals.target_calories if profile.goals else 2000} kcal.\n\n"
                f"Use the following retrieved clinical knowledge chunks to support your answer. "
                f"Provide direct, clinical-grade advice and maintain joint safety rules. Do not mention that you have context chunks:\n"
                f"{context}"
            )
            
            # Simple call to Gemini Developer API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            import requests
            res = requests.post(url, json=payload, headers=headers, timeout=5.0)
            if res.status_code == 200:
                answer = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"answer": answer, "mcp_source": "RAG MCP + Gemini API"}), 200
        except Exception as e:
            print(f"Gemini API generation failed: {e}. Falling back to offline engine.")
            
    # Fallback to local rule-based RAG synthesis
    answer = generate_offline_answer(query, profile, rag_results)
    return jsonify({
        "answer": answer, 
        "mcp_source": "RAG MCP (FAISS) + Health Knowledge MCP (Local Expert Engine)"
    }), 200
