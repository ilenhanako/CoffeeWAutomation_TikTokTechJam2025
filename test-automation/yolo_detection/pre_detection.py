# yolo_integration.py
import re
import os
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv('ROBOFLOW_API_KEY')
)

INTENT_TO_CLASS = {
    "comment": ["comment"],
    "reply": ["comment"],
    "like": ["like"],
    "heart": ["like"],
    "share": ["share"],
    "send": ["share"],
    "message": ["inbox"],
    "inbox": ["inbox"],
    "chat": ["inbox"],
    "profile": ["profile", "me"],
    "upload": ["upload", "post"],
    "friends": ["friends"],
    "explore": ["explore"],
    "search": ["search", "discover"],
    "home": ["home"],
    "following": ["following"],
    "for you": ["for you"],
    "shop": ["shop", "store"]
}

def get_prediction_from_step(image_path: str, user_query: str, confidence_threshold: float = 0.95):
    # step → possible YOLO classes
    query = user_query.lower()
    target_classes = []
    for keyword, classes in INTENT_TO_CLASS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", query):
            target_classes.extend(classes)
    target_classes = list(set(target_classes))

    if not target_classes:
        print(f"[YOLO] No intent keywords matched in query: '{user_query}'")
        return None
    
    # run YOLO
    result = client.run_workflow(
        workspace_name="tiktok-qz4gk",
        workflow_id="custom-workflow",
        images={"image": image_path},
        use_cache=True
    )

    for prediction in result[0]['output']['predictions']:
        if prediction['confidence'] < confidence_threshold:
            continue
        if prediction['class'].lower() in target_classes:
            return (prediction['x'], prediction['y'])
    
    print(f"[YOLO] No confident match for {target_classes}")
    return None
