#!/usr/bin/env python3
"""
Main entry point for the Knowledge Graph GUI Testing Tool

This demonstrates the complete flow:
1. Business scenario query → Vector search for similar scenarios
2. Knowledge graph traversal for executable paths  
3. ExecutorStep generation for GUI automation
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.neo4j_knowledge_graph import Neo4jKnowledgeGraph
from src.graph.populate_graph import populate_knowledge_graph_from_ontology
from src.graph.query_interface import GraphQueryInterface


def setup_knowledge_graph():
    """Initialize and populate the knowledge graph"""
    print("🚀 Setting up Knowledge Graph for GUI Testing")
    print("=" * 50)
    
    # Initialize Neo4j connection
    kg = Neo4jKnowledgeGraph(
        uri="bolt://localhost:7687",
        username="neo4j", 
        password="tiktoktechjam"  # Change this to your actual Neo4j password
    )
    
    print("📊 Populating knowledge graph from ontology...")
    populate_knowledge_graph_from_ontology(kg)
    
    return kg


def demonstrate_graphrag_flow():
    """Demonstrate the complete GraphRAG flow"""
    print("\n🧠 Demonstrating GraphRAG Flow")
    print("=" * 50)
    
    kg = setup_knowledge_graph()
    query_interface = GraphQueryInterface(kg)
    
    try:
        # Step 1: Add business scenarios to vector store
        print("\n📚 Step 1: Adding business scenarios to vector store")
        query_interface.add_sample_business_scenarios()
        
        # Step 2: Demonstrate queries
        print("\n🎯 Step 2: Querying with business scenarios")
        
        test_scenarios = [
            {
                "query": "User wants to log in and reach dashboard",
                "description": "Authentication flow"
            },
            {
                "query": "I want to comment on a video I see in my feed", 
                "description": "Social interaction"
            },
            {
                "query": "Update my profile bio information",
                "description": "Profile management"
            },
            {
                "query": "Like a video post that I enjoy watching",
                "description": "Content engagement"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n--- Test Scenario {i}: {scenario['description']} ---")
            print(f"Query: {scenario['query']}")
            
            # Get executable plan
            plan = query_interface.query_business_scenario(scenario['query'])
            
            print(f"\n📋 Generated ExecutorSteps:")
            if plan.steps:
                for step in plan.steps:
                    print(f"  {step.step_id}. {step.description}")
                    print(f"     Action: {step.action_type}")
                    print(f"     Query for LLM: {step.query_for_qwen}")
                    if step.alternative_actions:
                        print(f"     Alternatives: {', '.join(step.alternative_actions[:2])}")
                    if step.expected_state:
                        print(f"     Expected State: {step.expected_state}")
                    print()
            else:
                print("  No executable steps generated")
            
            print("-" * 60)
        
        # Step 3: Show knowledge graph structure
        print("\n🗺️  Step 3: Knowledge Graph Navigation Map")
        nav_map = query_interface.get_navigation_graph()
        
        for state, connections in nav_map.items():
            print(f"\n{state}:")
            for conn in connections[:3]:  # Show first 3 connections per state
                print(f"  {conn['action']} {conn['component']} → {conn['destination']}")
        
        print("\n✅ GraphRAG demonstration completed successfully!")
        print("\nNext steps:")
        print("1. Start Neo4j and view graph at http://localhost:7474")
        print("2. Run sample queries: MATCH (n) RETURN n LIMIT 25")
        print("3. Explore relationships: MATCH (c:Component)-[r]->(s:State) RETURN c,r,s")
        
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        print("Make sure Neo4j is running on localhost:7687 with correct credentials")
        
    finally:
        kg.close()


def interactive_query_mode():
    """Interactive mode for querying the knowledge graph"""
    print("\n🔍 Interactive Query Mode")
    print("Enter business scenarios to get executable test steps")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    kg = setup_knowledge_graph()
    query_interface = GraphQueryInterface(kg)
    
    # Add sample scenarios if not already present
    query_interface.add_sample_business_scenarios()
    
    try:
        while True:
            query = input("\n📝 Enter your business scenario: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
                
            print(f"\n🔍 Processing: {query}")
            print("-" * 30)
            
            plan = query_interface.query_business_scenario(query)
            
            if plan.steps:
                print(f"\n📋 Executable Test Plan: {plan.scenario_title}")
                for step in plan.steps:
                    print(f"\n  Step {step.step_id}: {step.description}")
                    print(f"    Action Type: {step.action_type}")
                    print(f"    Description: {step.query_for_qwen}")
                    if step.expected_state:
                        print(f"    Expected Result: {step.expected_state}")
            else:
                print("❌ No executable plan could be generated")
                print("Try rephrasing your scenario or check if similar scenarios exist")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        kg.close()


def main():
    """Main function with menu options"""
    print("🧪 Knowledge Graph GUI Testing Tool")
    print("==================================")
    print("\nOptions:")
    print("1. Demonstrate complete GraphRAG flow")
    print("2. Interactive query mode") 
    print("3. Setup knowledge graph only")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            demonstrate_graphrag_flow()
        elif choice == "2":
            interactive_query_mode()
        elif choice == "3":
            setup_knowledge_graph()
            print("✅ Knowledge graph setup completed")
        else:
            print("Invalid choice. Running demonstration by default.")
            demonstrate_graphrag_flow()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Ensure Neo4j is running on localhost:7687")
        print("- Check your Neo4j credentials")
        print("- Install required dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main()