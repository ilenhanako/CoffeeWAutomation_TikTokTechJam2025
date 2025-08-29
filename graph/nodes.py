
import base64, time
from typing import Dict, Any
from PIL import Image
from qwen_vl_utils import smart_resize

driver_manager = None
screenshot_mgr = None
processor = None
evaluator = None
guard = None

MAX_CYCLES = 3

def set_dependencies(dm, sm, proc, evalr, grd):
    global driver_manager, screenshot_mgr, processor, evaluator, guard
    driver_manager = dm
    screenshot_mgr = sm
    processor = proc
    evaluator = evalr
    guard = grd

def node_perceive(state: dict) -> dict:
    driver = driver_manager.get_driver()
    if driver is None:
        # create session if  missing
        driver = driver_manager.setup_driver()
        driver_manager.wait_for_app_launch(4)

    try:
        shot = screenshot_mgr.take_screenshot(driver)
    except Exception as e:
        msg = str(e).lower()
        if "instrumentation process is not running" in msg or "uiautomator2" in msg:
            print("[WARN] UiAutomator2 crashed. Restarting session...")
            try:
                driver_manager.quit_driver()
            except Exception:
                pass
            driver = driver_manager.setup_driver()
            driver_manager.wait_for_app_launch(4)
            time.sleep(1)
            shot = screenshot_mgr.take_screenshot(driver)   # retry once
        else:
            raise

    xml = driver_manager.get_page_source()
    import base64, os
    with open(shot, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return {**state, "screenshot_path": shot, "page_source_xml": xml, "screenshot_b64": b64}

def node_execute(state: Dict[str, Any]) -> Dict[str, Any]:
    # try your XML-first wrapper (it internally may call vision + qwen fallback)
    res = processor.execute_enhanced_xml_first(
        state["screenshot_path"], state["user_query"]
    )
    out = {"status": getattr(res, "status", None),
           "metadata": getattr(res, "metadata", {}),
           "action": getattr(res, "action", {})}
    return {**state, "exec_result": out, "exec_action": out.get("action", {})}

def node_evaluate(state: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(
        business_goal=state["business_goal"],
        step_description=state.get("step_description", state["user_query"]),
        expected_state_hint=state.get("expected_state_hint",
                                      "Screen reflects successful completion of the described step"),
        last_action_args=state.get("exec_action", {}),
        page_source_xml=state["page_source_xml"],
        screenshot_b64=state["screenshot_b64"],
    )
    er = evaluator.evaluate_step_outcome(**payload)
    print(f"[Evaluator] ok={er.ok} recovery={er.recovery} reason={er.reason}")
    if er.suggestions:
        for s in er.suggestions[:3]:
            print(f"   Suggestion: {s}")
    er_dict = {
        "ok": er.ok, "reason": er.reason, "recovery": er.recovery,
        "suggestions": er.suggestions, "gate_type": er.gate_type,
        "confidence": er.confidence,
    }
    return {**state, "eval_result": er_dict}

def decide_next(state: Dict[str, Any]) -> str:
    er = state.get("eval_result", {})
    if er.get("ok"):
        return "finish"
    if state.get("cycle", 0) >= MAX_CYCLES:
        return "finish"
    return "recover"

def node_recover(state: Dict[str, Any]) -> Dict[str, Any]:
    driver = driver_manager.get_driver()
    size = driver_manager.get_screen_size()

    intr = guard.detect(driver, size["width"], size["height"])

    if intr.present:
        decision = guard.decide(
            intr,
            state["business_goal"],
            state.get("step_description", state["user_query"]),
            state["page_source_xml"],
            state["screenshot_b64"]
        )
        img = Image.open(state["screenshot_path"])
        orig_w, orig_h = img.size
        # pull processor’s config
        pcfg = processor.processor_config
        resized_h, resized_w = smart_resize(img.height, img.width,
                                            factor=pcfg.patch_size * pcfg.merge_size,
                                            min_pixels=pcfg.min_pixels,
                                            max_pixels=pcfg.max_pixels)
        guard.handle(driver, processor.mobile_use, intr, decision,
                     resized_w, resized_h, orig_w, orig_h)

    # apply evaluator’s suggestions (1–3)
    for s in (state.get("eval_result", {}).get("suggestions") or [])[:3]:
        processor.execute_enhanced_xml_first(state["screenshot_path"], s)
        time.sleep(0.25)

    return {**state, "cycle": state.get("cycle", 0) + 1}

def node_finish(state: Dict[str, Any]) -> Dict[str, Any]:
    notes = list(state.get("notes", []))
    er = state.get("eval_result", {})
    notes.append(f"finish: ok={er.get('ok')} reason={er.get('reason')} cycles={state.get('cycle',0)}")
    return {**state, "done": True, "notes": notes}
