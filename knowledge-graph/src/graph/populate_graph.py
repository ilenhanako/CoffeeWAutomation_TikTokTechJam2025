#!/usr/bin/env python3

from ..models.ontology import (
    HomePage, STEMPage, ExplorePage, FollowingPage, FriendsPage, ForYouPage,
    ProfilePage, SettingsPage
)
from .neo4j_knowledge_graph import Neo4jKnowledgeGraph


def populate_knowledge_graph_from_ontology(kg: Neo4jKnowledgeGraph):
    """Populate Neo4j knowledge graph with states and components from ontology"""
    
    # Create base states with their own components
    home_page = HomePage()
    profile_page = ProfilePage() 
    settings_page = SettingsPage()
    
    # Add base states to knowledge graph
    print("Adding base states to knowledge graph...")
    kg.add_state(home_page)
    kg.add_state(profile_page)
    kg.add_state(settings_page)
    
    # Create substate nodes without components (they'll inherit from HomePage)
    print("Creating substate nodes...")
    substates = ['STEMPage', 'ExplorePage', 'FollowingPage', 'FriendsPage', 'ForYouPage']
    
    with kg.get_session() as session:
        for substate in substates:
            session.run("""
                MERGE (sub:State {name: $substate_name})
                SET sub.parent = 'HomePage'
            """, {"substate_name": substate})
            print(f"  ✓ Created empty {substate} node")
    
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
    
    # Navigation between feed sections - TAP on tabs navigates to specific substates
    tab_mappings = {
        "STEM": "STEMPage",
        "Explore": "ExplorePage", 
        "Following": "FollowingPage",
        "Friends": "FriendsPage",
        "ForYou": "ForYouPage"
    }
    
    for tab_name, target_state in tab_mappings.items():
        kg.add_action_relationship(
            component_id=f"HomePage_{tab_name}",
            action_type="tap",
            target_state=target_state,
            properties={
                "query_for_qwen": f"Tap on the {tab_name} tab in the feed navigation",
                "alternative_actions": [f"Swipe horizontally to {tab_name} section"]
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
    
    # Add tap actions for navbar navigation (tap to navigate between pages)
    for state_name in ["HomePage", "ProfilePage"]:
        kg.add_action_relationship(
            component_id=f"{state_name}_ProfileNavBar",
            action_type="tap",
            target_state="HomePage" if state_name == "ProfilePage" else "ProfilePage",
            properties={
                "query_for_qwen": f"Tap on the navigation bar to go to {'homepage' if state_name == 'ProfilePage' else 'profile page'}",
                "alternative_actions": ["Swipe on navigation bar", "Use back gesture"]
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
    
    # Note: Substates inherit all HomePage components automatically through inheritance
    # No need to create separate component relationships for each substate
    
    # ProfilePage scroll actions for browsing user content
    kg.add_action_relationship(
        component_id="ProfilePage_FollowingList",
        action_type="scroll",
        target_state="ProfilePage",
        properties={
            "query_for_qwen": "Scroll through the following list to browse followed users",
            "alternative_actions": ["Swipe up/down in following section"]
        }
    )
    
    kg.add_action_relationship(
        component_id="ProfilePage_FollowersList", 
        action_type="scroll",
        target_state="ProfilePage",
        properties={
            "query_for_qwen": "Scroll through followers list to see who follows this user",
            "alternative_actions": ["Swipe vertically through followers"]
        }
    )
    
    # Add inheritance relationships for substates  
    print("Adding inheritance relationships...")
    # substates list is already defined above
    
    with kg.get_session() as session:
        for substate in substates:
            # Add inheritance relationship
            session.run("""
                MATCH (parent:State {name: 'HomePage'})
                MATCH (sub:State {name: $substate_name})
                MERGE (sub)-[:INHERITS_FROM]->(parent)
            """, {"substate_name": substate})
            print(f"  ✓ {substate} inherits from HomePage")
            
        # Copy HomePage components to all substates for Neo4j graph traversal
        # (Python inheritance doesn't automatically create Neo4j relationships)
        print("Copying HomePage components to substates for graph traversal...")
        for substate in substates:
            result = session.run("""
                MATCH (home:State {name: 'HomePage'})-[:HAS_COMPONENT]->(c:Component)
                MATCH (sub:State {name: $substate_name})
                WHERE NOT (sub)-[:HAS_COMPONENT]->(c)
                CREATE (sub)-[:HAS_COMPONENT]->(c)
                RETURN count(c) as component_count
            """, {"substate_name": substate})
            
            count = result.single()['component_count']
            if count > 0:
                print(f"  ✓ Copied {count} components to {substate}")
            else:
                print(f"  ✓ {substate} already has all HomePage components")
    
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