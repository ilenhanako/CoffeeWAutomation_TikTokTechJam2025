import re
import math
from typing import List, Dict, Tuple, Optional

class XMLParser:
    
    NODE_REGEX = re.compile(
        r'class="([^"]*)".*?bounds="([^"]*)".*?'
        r'(?:text="([^"]*)")?.*?'
        r'(?:content-desc="([^"]*)")?.*?'
        r'(?:resource-id="([^"]*)")?.*?'
        r'(?:clickable="([^"]*)")?',
        re.S
    )
    
    @staticmethod
    def parse_bounds(bounds_str: str) -> Tuple[int, int, int, int]:
        matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str or "")
        if len(matches) == 2:
            (x1, y1), (x2, y2) = matches
            return int(x1), int(y1), int(x2), int(y2)
        return (0, 0, 0, 0)
    
    @classmethod
    def parse_nodes(cls, xml: str) -> List[Dict]:
        nodes = []
        for match in cls.NODE_REGEX.finditer(xml):
            cls_name, bounds, text, desc, res_id, clickable = match.groups()
            nodes.append({
                "class": cls_name or "",
                "bounds": cls.parse_bounds(bounds),
                "text": text or "",
                "content_desc": desc or "",
                "resource_id": res_id or "",
                "clickable": (clickable == "true"),
            })
        return nodes
    
    @staticmethod
    def get_center_point(bounds: Tuple[int, int, int, int]) -> List[int]:
        x1, y1, x2, y2 = bounds
        return [(x1 + x2) // 2, (y1 + y2) // 2]
    
    @staticmethod
    def find_by_selector(xml: str, text: str = None, content_desc: str = None, 
                        resource_id: str = None) -> Optional[List[int]]:
        #find element coordinates by text, content-desc, or resource-id
        text_lower = (text or "").lower()
        desc_lower = (content_desc or "").lower()
        resource_id = resource_id or ""
        
        for node in XMLParser.parse_nodes(xml):
            if text_lower and text_lower in node["text"].lower():
                return XMLParser.get_center_point(node["bounds"])
            if desc_lower and desc_lower in node["content_desc"].lower():
                return XMLParser.get_center_point(node["bounds"])
            if resource_id and resource_id in node["resource_id"]:
                return XMLParser.get_center_point(node["bounds"])
        return None
    
    @staticmethod
    def find_relevant_elements(xml: str, query: str) -> List[Dict]:
        # elements that match the user query
        query_lower = query.lower()
        candidates = []
        
        for node in XMLParser.parse_nodes(xml):
            label = " ".join([
                node["text"], 
                node["content_desc"], 
                node["resource_id"]
            ]).lower()
            
            if query_lower in label:
                candidates.append(node)
        
        return candidates
    
    @staticmethod
    def is_point_inside_bounds(bounds: Tuple[int, int, int, int], x: int, y: int) -> bool:
        x1, y1, x2, y2 = bounds
        return x1 <= x <= x2 and y1 <= y <= y2
    
    @staticmethod
    def calculate_distance_squared(x1: int, y1: int, x2: int, y2: int) -> int:
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    
    @staticmethod
    def get_node_text_combined(node: Dict) -> str:
        #get combined text representation of a node
        return " ".join([
            node.get("text", ""),
            node.get("content_desc", ""),
            node.get("resource_id", ""),
            node.get("class", "")
        ]).lower()