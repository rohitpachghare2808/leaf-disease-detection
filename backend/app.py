from flask import Flask, request, jsonify, send_from_directory, session
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from model import LeafCNN
import os
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from db import connect, get_db_path, init_db, ensure_default_user, utc_now_iso

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "leafcare-dev-secret-change-me")

import tempfile
UPLOADS_DIR = os.path.join(tempfile.gettempdir(), "leafcare_uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

DB_PATH = get_db_path(BASE_DIR)
DB = connect(DB_PATH)
init_db(DB)

# Create a default demo user if not present
DEMO_EMAIL = "leafcare@example.com"
DEMO_PASSWORD = "leaf123"
ensure_default_user(DB, DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD))

# IMPORTANT: class order MUST match the folder names order used by ImageFolder.
# Fallback list is used if trained checkpoint doesn't contain class names.
classes = [
    "Bacterial Spot",
    "Early Blight",
    "Healthy",
    "Late Blight",
    "Leaf Curl",
    "Leaf Spot",
    "Mosaic Virus",
    "Powdery Mildew",
    "Rust",
    "Septoria Leaf Spot"
]
feature_prototypes = {}
feature_distance_thresholds = {}

# Instantiate model and, if available, load trained weights.
weights_path = os.path.join(BASE_DIR, "leaf_model.pth")
loaded_state_dict = None
if os.path.exists(weights_path):
    try:
        state = torch.load(weights_path, map_location="cpu")
        # Support both plain state_dict and checkpoint dict.
        if isinstance(state, dict) and "state_dict" in state:
            loaded_state_dict = state["state_dict"]
            if isinstance(state.get("classes"), list) and state["classes"]:
                classes = state["classes"]
            if isinstance(state.get("feature_prototypes"), dict):
                feature_prototypes = state["feature_prototypes"]
            if isinstance(state.get("feature_distance_thresholds"), dict):
                feature_distance_thresholds = state["feature_distance_thresholds"]
        else:
            loaded_state_dict = state
        print("Successfully loaded leaf_model.pth")
    except Exception as e:
        print(f"WARNING: Could not read weights from leaf_model.pth. Using untrained model. Error: {e}")
else:
    print("WARNING: leaf_model.pth not found. Using untrained model, predictions will be unreliable.")

if loaded_state_dict is not None:
    fc2_weight = loaded_state_dict.get("fc2.weight")
    if fc2_weight is not None:
        output_classes = int(fc2_weight.shape[0])
        if output_classes != len(classes):
            if output_classes < len(classes):
                classes = classes[:output_classes]
            else:
                classes = classes + [f"Class {i+1}" for i in range(len(classes), output_classes)]
else:
    output_classes = len(classes)

model = LeafCNN(num_classes=output_classes)
if loaded_state_dict is not None:
    try:
        model.load_state_dict(loaded_state_dict)
    except Exception as e:
        print(f"WARNING: Could not load checkpoint in model. Using untrained model. Error: {e}")

model.eval()

# Human-readable information for each class (same keys as in `classes`)
DISEASE_INFO = {
    "Healthy": {
        "remedy": "No treatment required",
        "prevention": "Regular monitoring"
    },
    "Early Blight": {
        "remedy": "Apply fungicide",
        "prevention": "Crop rotation"
    },
    "Late Blight": {
        "remedy": "Use copper fungicide",
        "prevention": "Avoid excess moisture"
    },
    "Leaf Spot": {
        "remedy": "Remove infected leaves",
        "prevention": "Proper spacing"
    },
    "Powdery Mildew": {
        "remedy": "Sulfur spray",
        "prevention": "Increase airflow"
    },
    "Rust": {
        "remedy": "Apply fungicide",
        "prevention": "Avoid wet foliage"
    },
    "Bacterial Spot": {
        "remedy": "Copper-based bactericide",
        "prevention": "Use disease-free seeds"
    },
    "Leaf Curl": {
        "remedy": "Control insects",
        "prevention": "Use resistant varieties"
    },
    "Mosaic Virus": {
        "remedy": "Remove infected plants",
        "prevention": "Control aphids"
    },
    "Septoria Leaf Spot": {
        "remedy": "Apply fungicide",
        "prevention": "Avoid overhead watering"
    },
    "Unknown": {
        "remedy": "Ensure you are uploading a clear image of a single leaf.",
        "prevention": "If it is a leaf, the disease may not be supported yet."
    },
    "Nitrogen Deficiency": {
        "remedy": "Apply a balanced nitrogen‑rich fertilizer, add well‑decomposed compost.",
        "prevention": "Ensure regular but not excessive watering, monitor soil health."
    }
}

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        # Keep inference preprocessing aligned with training.
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

# SERVE YOUR WEBSITE
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOADS_DIR, filename)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"ok": False, "error": "Email and password are required."}), 400

    cur = DB.cursor()
    cur.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"ok": False, "error": "Invalid email or password."}), 401

    session["user_id"] = int(user["id"])
    session["email"] = user["email"]
    return jsonify({"ok": True, "email": user["email"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/me", methods=["GET"])
def me():
    if not session.get("user_id"):
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "email": session.get("email")})


@app.route("/history", methods=["GET"])
def history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in."}), 401

    cur = DB.cursor()
    cur.execute(
        """
        SELECT id, filename, result, description, treatment, confidences_json, created_at
        FROM scans
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (int(user_id),),
    )
    rows = cur.fetchall()
    items = []
    for r in rows:
        items.append(
            {
                "id": r["id"],
                "file": r["filename"],
                "result": r["result"],
                "description": r["description"],
                "treatment": r["treatment"],
                "prevention": r["description"],
                "remedy": r["treatment"],
                "confidences": json.loads(r["confidences_json"]),
                "time": r["created_at"],
                "imageUrl": f"/uploads/{r['filename']}",
            }
        )
    return jsonify({"ok": True, "items": items})

@app.route("/predict", methods=["POST"])
def predict():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in."}), 401

    file = request.files["image"]

    # Save uploaded image file
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
        ext = ".jpg"
    saved_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOADS_DIR, saved_name)
    file.save(saved_path)

    image = Image.open(saved_path).convert("RGB")
    img = transform(image).unsqueeze(0)  # shape: [1, 3, 224, 224]

    with torch.no_grad():
        features = model.extract_features(img)[0]
        outputs = model.fc2(features.unsqueeze(0))
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        predicted_index = int(torch.argmax(probabilities).item())
        confidence_val = float(probabilities[predicted_index].item())

    predicted_class = classes[predicted_index]
    distance_reject = False
    if predicted_class in feature_prototypes and predicted_class in feature_distance_thresholds:
        prototype = torch.tensor(feature_prototypes[predicted_class], dtype=features.dtype)
        feature_distance = float(torch.norm(features.cpu() - prototype, p=2).item())
        allowed_distance = float(feature_distance_thresholds[predicted_class])
        distance_reject = feature_distance > allowed_distance

    # Lower threshold to reduce false "Unknown" on small datasets.
    # Still treat direct "Unknown" class predictions as unknown.
    if confidence_val < 0.60 or predicted_class == "Unknown" or distance_reject:
        prediction = "Unknown"
    else:
        prediction = predicted_class

    result = prediction
    # Normalize legacy class name lookup
    lookup_key = result
    if lookup_key == "Healthy Leaf":
        lookup_key = "Healthy"

    info = DISEASE_INFO.get(lookup_key, {})

    confidences = {
        cls: float(probabilities[i].item())
        for i, cls in enumerate(classes)
    }

    remedy = info.get("remedy", "")
    prevention = info.get("prevention", "")

    cur = DB.cursor()
    cur.execute(
        """
        INSERT INTO scans (user_id, filename, result, description, treatment, confidences_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(user_id),
            saved_name,
            result,
            prevention,
            remedy,
            json.dumps(confidences),
            utc_now_iso(),
        ),
    )
    DB.commit()
    scan_id = cur.lastrowid

    return jsonify(
        {
            "ok": True,
            "id": scan_id,
            "result": result,
            "prediction": prediction,
            "confidence": round(confidence_val * 100, 2),
            "confidences": confidences,
            "description": prevention,
            "treatment": remedy,
            "prevention": prevention,
            "remedy": remedy,
            "imageUrl": f"/uploads/{saved_name}",
            "uploadedAs": saved_name,
        }
    )

if __name__ == "__main__":
    app.run(debug=True)