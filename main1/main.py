from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
from fuzzywuzzy import process

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not set.")

# Configure GenAI API
genai.configure(api_key=api_key)

# Initialize FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class InputModel(BaseModel):
    input: str

class OutputModel(BaseModel):
    output: str

# Predefined responses for each question
predefined_responses = {
    "what services do you offer?": (
        "We offer Longevity Tests, Genetic Tests, and an Immunity Store. "
        "Let me know what you'd like to explore!"
    ),
    "what are the available longevity tests.": (
        "Here are the Longevity Tests we currently offer:\n\n"
        "✅ AI Cancer Test: Available\nBook here: https://longevity.dnaiworld.com/HybridChat\n\n"
        "🧪 Diabetic Testing: Coming Soon\n"
        "❤️ Cardiovascular Testing: Coming Soon\n"
        "🥗 Personalized Food Test: Coming Soon\n"
        "💊 Healthy Supplement Test: Coming Soon"
    ),
    "what are the available genetic tests?": (
        "Here are the Genetic Tests we offer:\n\n"
        "- NIPT (Noninvasive Prenatal Screening)\n"
        "- Clinical Exome Sequencing\n"
        "- Microbiome Analysis\n"
        "- Genetic Disorder Testing\n"
        "- Whole Exome Sequencing\n"
        "- RNA Sequencing\n\n"
        "Book here: https://longevity.dnaiworld.com/GetGeneSeq"
    ),
    "go to immunity store?": (
        "Sure! Here's what we have in the Immunity Store:\n\n"
        "🍎 Apple: ₹100 / 250 gm\n"
        "🍌 Banana: ₹20 / 250 gm\n"
        "🍊 Orange: ₹30 / 250 gm\n\n"
        "Shop now: https://longevity.dnaiworld.com/immunity-store"
    ),
    "how do i book a ai cancer test?": (
        "AI Cancer Test: Available\n\n"
        "Book AI Cancer Test here: https://longevity.dnaiworld.com/HybridChat.\n\n"
    ),
    "what are the symptoms of lung cancer?": (
        "Common symptoms of lung cancer include:\n"
        "- Persistent cough\n"
        "- Chest pain\n"
        "- Shortness of breath\n"
        "- Coughing up blood"
    ),
    "can you suggest some health tips?": (
        "Here are some general health tips:\n"
        "- 🥗 Eat a balanced diet\n"
        "- 🏃 Stay physically active\n"
        "- 😴 Get 7–8 hours of sleep\n"
        "- 🚰 Stay hydrated\n"
        "- 🧘 Manage stress\n"
        "- 🚭 Avoid smoking"
    ),
    "how can i order from the immunity store?": (
        "You can explore and order items from the Immunity Store at:\n"
        "https://longevity.dnaiworld.com/immunity-store\n\n"
        "Let me know if you’d like to add anything to your cart!"
    ),
    "where can i book a genetic test?": (
        "You can book genetic tests here:\n"
        "https://longevity.dnaiworld.com/GetGeneSeq\n\n"
        "Let me know which test you're interested in!"
    ),
    "what tests are coming soon?": (
        "Coming soon:\n"
        "- Diabetic Testing\n"
        "- Cardiovascular Testing\n"
        "- Personalized Food Test\n"
        "- Healthy Supplement Test"
    ),
}

# Only these are considered for direct answer
def predefined_questions():
    return list(predefined_responses.keys())

# Health-related keywords
health_keywords = [
    "cancer", "test", "doctor", "symptoms", "disease", "medicine", "treatment",
    "immunity", "genetic", "health", "medical", "wellness", "infection", "therapy",
    "diagnosis", "risk", "nutrition", "exercise", "screening"
]

# Cancer symptom mapping
cancer_symptoms = {
    "lung cancer": ["cough", "chest pain", "shortness of breath", "coughing up blood"],
    "breast cancer": ["lump in breast", "nipple discharge", "breast pain", "skin changes"],
    "colon cancer": ["blood in stool", "abdominal pain", "weight loss", "diarrhea"],
    "leukemia": ["fatigue", "frequent infections", "easy bruising", "pale skin"],
    "skin cancer": ["mole changes", "new skin growth", "itchy lesion", "bleeding spot"]
}

@app.post("/generate-sample-queries", response_model=dict)
async def generate_sample_queries():
    return {"sample_queries": predefined_questions()}

@app.post("/generate-response", response_model=OutputModel)
async def generate_response(input_data: InputModel):
    user_input = input_data.input.strip().lower()

    # Match against predefined
    best_match, score = process.extractOne(user_input, predefined_responses.keys())
    if score > 85:
        return OutputModel(output=predefined_responses[best_match])

    # Symptom detection
    user_symptoms = set(user_input.split())
    possible_cancers = [
        cancer for cancer, symptoms in cancer_symptoms.items()
        if any(symptom in user_symptoms for symptom in symptoms)
    ]
    if possible_cancers:
        return OutputModel(output=f"Possible risk: {', '.join(possible_cancers)}. Consult a doctor.")

    # Check for health-related
    if any(keyword in user_input for keyword in health_keywords):
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(user_input)
        return OutputModel(output=response.text.strip())

    # Fallback for unrelated
    return OutputModel(output="I specialize in health-related queries. We currently offer Longevity Tests, Genetic Tests, and an Immunity Store!")

@app.get("/")
async def root():
    return {"message": "Welcome to DNAi Chatbot. Use available endpoints for assistance."}
