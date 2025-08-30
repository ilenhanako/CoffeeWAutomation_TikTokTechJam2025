#!/usr/bin/env python3

from ..models.ontology import HomePage, ProfilePage, SettingsPage
from .neo4j_knowledge_graph import Neo4jKnowledgeGraph


def populate_knowledge_graph_from_ontology(kg: Neo4jKnowledgeGraph):
    """Populate Neo4j knowledge graph with states and components from ontology"""
    
    # Create state instances from ontology
    home_page = HomePage()
    profile_page = ProfilePage() 
    settings_page = SettingsPage()
    
    # Add states to knowledge graph
    print("Adding states to knowledge graph...")
    kg.add_state(home_page)
    kg.add_state(profile_page)
    kg.add_state(settings_page)
    
    # Add action relationships based on typical app navigation patterns
    print("Adding action relationships...")
    
    # HomePage actions
    kg.add_action_relationship(
        component_id="HomePage_UserButton",
        action_type="tap", 
        target_state="ProfilePage",
        properties={
            "query_for_qwen": "Tap on the user profile button in the top navigation",
            "alternative_actions": ["Long press on user avatar", "Swipe left to access profile"]
        }
    )
    
    kg.add_action_relationship(
        component_id="HomePage_LikeButton",
        action_type="tap",
        target_state="HomePage",  # Stays on same page but updates state
        properties={
            "query_for_qwen": "Tap the like button (heart icon) on a video post",
            "alternative_actions": ["Double tap on the video to like"]
        }
    )
    
    kg.add_action_relationship(
        component_id="HomePage_CommentButton", 
        action_type="tap",
        target_state="HomePage",  # Opens comment panel overlay
        properties={
            "query_for_qwen": "Tap the comment button (speech bubble icon) on a video post",
            "alternative_actions": ["Long press on video to reveal options, then select 'Comment'"]
        }
    )
    
    kg.add_action_relationship(
        component_id="HomePage_ShareButton",
        action_type="tap", 
        target_state="HomePage",  # Opens share sheet
        properties={
            "query_for_qwen": "Tap the share button (arrow icon) on a video post",
            "alternative_actions": ["Long press on video and select share"]
        }
    )
    
    kg.add_action_relationship(
        component_id="HomePage_SearchButton",
        action_type="tap",
        target_state="HomePage",  # Opens search overlay  
        properties={
            "query_for_qwen": "Tap the search button (magnifying glass) in navigation",
            "alternative_actions": ["Swipe down to reveal search bar"]
        }
    )
    
    # Navigation between feed sections
    for section in ["STEM", "Explore", "Following", "Friends", "ForYou"]:
        kg.add_action_relationship(
            component_id=f"HomePage_{section}",
            action_type="tap",
            target_state="HomePage",  # Same state, different content
            properties={
                "query_for_qwen": f"Tap on the {section} tab in the feed navigation",
                "alternative_actions": [f"Swipe horizontally to {section} section"]
            }
        )
    
    # ProfilePage actions  
    kg.add_action_relationship(
        component_id="ProfilePage_SettingsButton",
        action_type="tap",
        target_state="SettingsPage",
        properties={
            "query_for_qwen": "Tap the settings button (gear icon) on profile page",
            "alternative_actions": ["Access settings from profile menu"]
        }
    )
    
    kg.add_action_relationship(
        component_id="ProfilePage_FollowButton", 
        action_type="tap",
        target_state="ProfilePage",  # Updates follow status
        properties={
            "query_for_qwen": "Tap the Follow button on user profile",
            "alternative_actions": ["Long press to see follow options"]
        }
    )
    
    kg.add_action_relationship(
        component_id="ProfilePage_MessageButton",
        action_type="tap", 
        target_state="ProfilePage",  # Opens message interface
        properties={
            "query_for_qwen": "Tap the Message button to send direct message",
            "alternative_actions": ["Long press for message options"]
        }
    )
    
    # SettingsPage actions
    for input_field in ["NameInput", "UserNameInput", "BioInput", "LinksInput"]:
        kg.add_action_relationship(
            component_id=f"SettingsPage_{input_field}",
            action_type="tap",
            target_state="SettingsPage",  # Opens keyboard for editing
            properties={
                "query_for_qwen": f"Tap on the {input_field.replace('Input', '')} input field to edit",
                "alternative_actions": [f"Long press {input_field.replace('Input', '')} field for options"]
            }
        )
        
        kg.add_action_relationship(
            component_id=f"SettingsPage_{input_field}",
            action_type="type", 
            target_state="SettingsPage",  # Updates field content
            properties={
                "query_for_qwen": f"Type new {input_field.replace('Input', '').lower()} in the input field",
                "alternative_actions": ["Use voice input", "Paste from clipboard"]
            }
        )
    
    # Add swipe actions for general navigation
    for state_name in ["HomePage", "ProfilePage"]:
        kg.add_action_relationship(
            component_id=f"{state_name}_ProfileNavBar",
            action_type="swipe",
            target_state="HomePage" if state_name == "ProfilePage" else "ProfilePage",
            properties={
                "query_for_qwen": f"Swipe {'right' if state_name == 'ProfilePage' else 'left'} on the navigation bar",
                "alternative_actions": ["Use back gesture", "Tap navigation buttons"]
            }
        )
    
    # Add scroll actions for content browsing
    print("Adding scroll actions...")
    
    # HomePage scroll actions for browsing video content
    kg.add_action_relationship(
        component_id="HomePage_LikeButton",
        action_type="scroll",
        target_state="HomePage",  # Stays on same page but shows different content
        properties={
            "query_for_qwen": "Scroll down through the video feed to find videos to like",
            "alternative_actions": ["Swipe up on feed", "Flick scroll to browse quickly"]
        }
    )
    
    kg.add_action_relationship(
        component_id="HomePage_CommentButton",
        action_type="scroll", 
        target_state="HomePage",
        properties={
            "query_for_qwen": "Scroll through video feed to find videos to comment on",
            "alternative_actions": ["Swipe up/down to browse videos", "Quick scroll to find content"]
        }
    )
    
    # Add scroll for feed sections
    for section in ["STEM", "Explore", "Following", "Friends", "ForYou"]:
        kg.add_action_relationship(
            component_id=f"HomePage_{section}",
            action_type="scroll",
            target_state="HomePage",
            properties={
                "query_for_qwen": f"Scroll through the {section} feed to browse content",
                "alternative_actions": [f"Swipe vertically in {section} section", "Quick scroll to find videos"]
            }
        )
    
    # ProfilePage scroll actions for browsing user content
    kg.add_action_relationship(
        component_id="ProfilePage_Following",
        action_type="scroll",
        target_state="ProfilePage",
        properties={
            "query_for_qwen": "Scroll through the following list to browse followed users",
            "alternative_actions": ["Swipe up/down in following section"]
        }
    )
    
    kg.add_action_relationship(
        component_id="ProfilePage_Followers", 
        action_type="scroll",
        target_state="ProfilePage",
        properties={
            "query_for_qwen": "Scroll through followers list to see who follows this user",
            "alternative_actions": ["Swipe vertically through followers"]
        }
    )
    
    print("Knowledge graph population completed!")


def main():
    """Main function to populate the knowledge graph"""
    # Initialize knowledge graph connection
    kg = Neo4jKnowledgeGraph(
        uri="bolt://localhost:7687",
        username="neo4j", 
        password="tiktoktechjam"  # Change this to your Neo4j password
    )
    
    try:
        populate_knowledge_graph_from_ontology(kg)
        print("\n✅ Successfully populated knowledge graph with ontology data")
        print("You can now view the graph in Neo4j Browser at http://localhost:7474")
        print("\nSample Cypher queries to try:")
        print("MATCH (n) RETURN n LIMIT 25")
        print("MATCH (s:State)-[:HAS_COMPONENT]->(c:Component) RETURN s, c")
        print("MATCH (c:Component)-[r:TAP]->(s:State) RETURN c, r, s")
        
    except Exception as e:
        print(f"❌ Error populating knowledge graph: {e}")
        print("Make sure Neo4j is running on localhost:7687")
        
    finally:
        kg.close()


if __name__ == "__main__":
    main()