import math
import random
from typing import List, Tuple, Dict
from utils.xml_parser import XMLParser

class CoordinateUtils:
    #coordinate manipulation for clicking
    
    @staticmethod
    def normalize_action_coordinates(action, original_width, original_height, model_width, model_height):
        if 'arguments' not in action or 'coordinate' not in action['arguments']:
            return action

        x, y = action['arguments']['coordinate']

        
        should_scale = (
            model_width and model_height and
            0 <= x <= model_width and
            0 <= y <= model_height
        )

        if should_scale:
            nx = (x / float(model_width)) * float(original_width)
            ny = (y / float(model_height)) * float(original_height)
        else:
         
            nx, ny = float(x), float(y)

        # Clamp to screen bounds
        nx = max(0, min(int(round(nx)), max(0, original_width - 1)))
        ny = max(0, min(int(round(ny)), max(0, original_height - 1)))

        action['arguments']['coordinate'] = [nx, ny]
        return action
    
    @staticmethod
    def snap_to_nearest_tappable(x, y, xml: str, screen_w: int, screen_h: int,
                                 max_dist_px: int = 160, prefer_right_rail: bool = True,
                                 right_rail_ratio: float = 0.25,
                                 prefer_keywords = ("comment","like","share","send","reply")):
        nodes = XMLParser.parse_nodes(xml)
        if not nodes:
            return [x,y]

     
        cands = []
        for n in nodes:
            cls = n["class"].lower()
            interactive = (
                n["clickable"] or n["resource_id"] or n["content_desc"] or n["text"] or
                any(k in cls for k in ["button","imagebutton","checkbox","switch","tab","edittext","imageview"])
            )
            if interactive:
                cands.append(n)
        if not cands:
            return [x,y]

        # if point is already inside some candidate, prefer the smallest containing node
        inside = [n for n in cands if XMLParser.is_point_inside_bounds(n["bounds"], x, y)]
        if inside:
            inside.sort(key=lambda n: (n["bounds"][2]-n["bounds"][0])*(n["bounds"][3]-n["bounds"][1]))
            chosen = inside[0]
            return XMLParser.get_center_point(chosen["bounds"])

        # otherwise score by distance + bonuses
        best = None
        best_score = 1e18
        rail_x0 = int(screen_w * (1.0 - right_rail_ratio)) if prefer_right_rail else None

        import math
        for n in cands:
            cx,cy = XMLParser.get_center_point(n["bounds"])
            d2 = XMLParser.calculate_distance_squared(cx,cy,x,y)
            d = math.sqrt(d2)
            if d > max_dist_px:
                continue  # too far to be relevant

            score = d  # base score = Euclidean distance
            if n["clickable"]:
                score *= 0.6  # clickable bonus

            label = XMLParser.get_node_text_combined(n)
            if any(k in label for k in prefer_keywords):
                score *= 0.7  # keyword bonus

            if prefer_right_rail and rail_x0 is not None:
                x1,_,_,_ = n["bounds"]
                if x1 >= rail_x0:
                    score *= 0.75 

            if score < best_score:
                best_score = score
                best = n

        return XMLParser.get_center_point(best["bounds"]) if best else [x,y]
    
    @staticmethod
    def build_click_box(driver, xml: str, x: int, y: int, default_box_ratio=0.12):
        nodes = XMLParser.parse_nodes(xml)

        closest = None
        min_dist = 1e18
        for n in nodes:
            if not n["clickable"]:
                continue
            cx, cy = XMLParser.get_center_point(n["bounds"])
            d = (cx - x)**2 + (cy - y)**2
            if d < min_dist:
                min_dist = d
                closest = n

        if closest:
            print(f"Using XML bounds for nearest tappable element: {closest['bounds']}")
            x1,y1,x2,y2 = closest["bounds"]
        else:
            size = driver.get_screen_size()
            w, h = int(size["width"]), int(size["height"])
            box = int(max(16, w * default_box_ratio))
            x1 = x - box // 2
            y1 = y - box // 2
            x2 = x + box // 2
            y2 = y + box // 2

            # Clamp to screen
            x1 = max(1, min(x1, w - 2))
            x2 = max(1, min(x2, w - 2))
            y1 = max(1, min(y1, h - 2))
            y2 = max(1, min(y2, h - 2))

            # proper ordering
            if x1 > x2: x1, x2 = x2, x1
            if y1 > y2: y1, y2 = y2, y1

            print(f"No XML bounds found. Using centered box: ({x1},{y1}) -> ({x2},{y2})")

        return (x1, y1, x2, y2)
    