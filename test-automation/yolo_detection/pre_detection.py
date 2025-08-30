# # yolo_integration.py
# import re
import os
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv('ROBOFLOW_API_KEY')
)


INTENT_TO_CLASS = {
    "comment": ["comment", "comment_edit"], 
    "reply": ["comment", "comment_edit"],
    "type": ["comment_edit", "send_comment"],
    "submit": ["send_comment"],
    "write": ["comment_edit"],
    "send": ["send_comment", "share"],
    "post": ["send_comment"],
    "like": ["like"],
    "heart": ["like"],
    "share": ["share"],
    "message": ["inbox"],
    "inbox": ["inbox"],
    "chat": ["inbox"],
    "profile": ["profile"],
    "upload": ["upload"],
    "friends": ["friends"],
    "explore": ["explore"],
    "search": ["search"],
    "magnifying": ["search"],
    "home": ["home"],
    "following": ["following"],
    "for you": ["for you"],
    "shop": ["shop"],
    "store": ["shop"]
}

# def get_prediction_from_step(image_path: str, user_query: str, confidence_threshold: float = 0.95):
#     # step → possible YOLO classes
#     query = user_query.lower()
#     target_classes = []
#     for keyword, classes in INTENT_TO_CLASS.items():
#         if re.search(rf"\b{re.escape(keyword)}\b", query):
#             target_classes.extend(classes)
#     target_classes = list(set(target_classes))

#     if not target_classes:
#         #TODO: remove later
#         print(f"[YOLO] No intent keywords matched in query: '{user_query}'")
#         return None
    
#     # run YOLO
#     result = client.run_workflow(
#         workspace_name="tiktok-qz4gk",
#         workflow_id="custom-workflow-2",
#         images={"image": image_path},
#         use_cache=True
#     )

#     for prediction in result[0]['output']['predictions']:
#         if prediction['confidence'] < confidence_threshold:
#             continue
#         if prediction['class'].lower() in target_classes:
#             return (prediction['x'], prediction['y'])
#     #TODO: remove later
#     print(f"[YOLO] No confident match for {target_classes}")
#     return None

from rapidfuzz import process, fuzz
import re

YOLO_CLASSES = [
    'Following', 'For you', 'Friends', 'comment', 'comment_edit',
    'edit_profile', 'home', 'like', 'name_edit', 'profile',
    'save', 'search', 'send_comment', 'share', 'username_edit'
]

def expand_with_fuzzy(query: str, threshold: int = 70) -> list[str]:
    matches = process.extract(query, YOLO_CLASSES, scorer=fuzz.partial_ratio, limit=5)
    return [m[0] for m in matches if m[1] >= threshold]

def get_prediction_from_step(image_path: str, user_query: str, confidence_threshold: float = 0.95):
    query = user_query.lower()
    target_classes = []

    # 1. Exact intent → classes mapping
    for keyword, classes in INTENT_TO_CLASS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", query):
            target_classes.extend(classes)
        
    if any(k in query for k in ["type", "write", "input", "text"]):
        target_classes.extend(["comment_edit", "username_edit", "name_edit"])

    # 2. Fuzzy expansion if no intent matched
    if not target_classes:
        fuzzy_classes = expand_with_fuzzy(query)
        if fuzzy_classes:
            print(f"[YOLO] Fuzzy matched '{query}' → {fuzzy_classes}")
            target_classes.extend(fuzzy_classes)

    target_classes = list(set(target_classes))
    if not target_classes:
        print(f"[YOLO] No intent or fuzzy matches for query: '{user_query}'")
        return None

    # 3. Run YOLO workflow
    result = client.run_workflow(
        workspace_name="tiktok-qz4gk",
        # workflow_id="tiktokflutter",
        workflow_id="tiktoklynx",
        images={"image":image_path},
        use_cache=True
    )

    if isinstance(result, list) and len(result) > 0:
        predictions = result[0].get("predictions", {}).get("predictions", [])
    elif isinstance(result, dict):
        predictions = result.get("predictions", {}).get("predictions", [])
    else:
        predictions = []

    # 4. Filter predictions by target_classes and confidence
    filtered = []
    for p in predictions:
        print(f"[YOLO] Prediction: class={p.get('class')}, confidence={p.get('confidence')}")
        if p["confidence"] >= confidence_threshold and p["class"].lower() in [c.lower() for c in target_classes]:
            filtered.append(p)

    if not filtered:
        print(f"[YOLO] No confident match for {target_classes}")
        return None

    # 5. Return the prediction with the highest confidence
    best_prediction = max(filtered, key=lambda x: x["confidence"])
    return (best_prediction["x"], best_prediction["y"])

