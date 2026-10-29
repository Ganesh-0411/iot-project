# analyze.py
import easyocr
import json
import os

# Initialize the reader globally so it doesn't reload on every request
# 'en' for English. Add other codes like ['en', 'hi'] for multi-language
try:
    print("⏳ Loading OCR Engine (this happens once)...")
    reader = easyocr.Reader(['en'], gpu=False) # gpu=False for better compatibility
    print("✅ OCR Engine Ready!")
except Exception as e:
    print(f"⚠️ Warning during OCR init: {e}")
    reader = None

# Load Massive Subject Data Set from JSON
dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
try:
    with open(dataset_path, "r") as f:
        SUBJECT_DATASET = json.load(f)
    print(f"📚 Loaded {sum(len(v) for v in SUBJECT_DATASET.values())} keywords from dataset.json")
except Exception as e:
    print(f"⚠️ Error loading dataset.json: {e}")
    SUBJECT_DATASET = {}

def classify_subject(text: str) -> str:
    """Determine which subject the text belongs to with high sensitivity."""
    text = "".join(text.lower().split())
    
    if not SUBJECT_DATASET:
        return "General"
    
    # Initialize scores for each subject
    scores = {}
    for s in SUBJECT_DATASET.keys():
        scores[s] = 0
    
    # Check for keywords from the JSON dataset
    for subject, keywords in SUBJECT_DATASET.items():
        # Direct subject name match (High weight)
        if subject.lower() in text:
            scores[subject] += 5
            
        for kw in keywords:
            clean_kw = "".join(kw.lower().split())
            if clean_kw in text:
                scores[subject] += 1
                
    if not scores:
        return "General"
        
    print(f"📊 Match Scores: {scores}")
    
    # Explicitly find the subject with the highest score
    best_subject = max(scores.keys(), key=lambda k: scores[k])
    return best_subject if scores[best_subject] > 0 else "General"

def analyze_handwriting(image_path: str) -> dict:
    """Use EasyOCR to extract text locally and classify it into subjects."""
    if reader is None:
        return {"summary": "OCR Engine failed.", "error": "Init Error"}

    try:
        results = reader.readtext(image_path, detail=0)
        raw_text = "\n".join(results)
        
        # Determine the Subject
        category = classify_subject(raw_text)
        
        title = results[0][:50] if results else f"Digitized {category} Note"
        
        return {
            "title": title,
            "subject": category,  # New field!
            "type": "handwritten note",
            "language": "english",
            "raw_text": raw_text,
            "structured": {
                "headings": [category] + results[:1],
                "paragraphs": [raw_text],
                "lists": [],
                "math": [],
                "tables": []
            },
            "summary": f"Detected Subject: {category}. Extracted {len(results)} text blocks.",
            "confidence": "Local OCR"
        }

    except Exception as e:
        print(f"OCR error: {e}")
        return {
            "summary": f"Failed to read image locally: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    if os.path.exists("handwriting.png"):
        print(analyze_handwriting("handwriting.png"))
