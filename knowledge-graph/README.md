# Knowledge Graph GUI Testing Tool

A GraphRAG-powered system for automated GUI testing of native apps without DOM access. This tool converts business scenarios into executable test steps using knowledge graph traversal and vector similarity search.

## Architecture

```
Business Scenario Query → Vector Search → Knowledge Graph → ExecutorSteps
```

1. **Business Scenarios** stored in ChromaDB vector store for semantic search
2. **Knowledge Graph** in Neo4j containing UI states, components, and action relationships  
3. **GraphRAG** combines vector search + graph traversal for comprehensive test planning

## Knowledge Graph Structure

### Nodes
- `:State` - UI states (HomePage, ProfilePage, SettingsPage)
- `:Component` - UI components (buttons, inputs, navigation)

### Relationships
- `[:HAS_COMPONENT]` - State contains component
- `[:CONTAINS]` - Hierarchical state relationships
- `[:TAP|SWIPE|SCROLL|TYPE]` - Action relationships from components to target states

## Setup

### Prerequisites
- Neo4j database running on `localhost:7687`
- Python 3.8+

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start Neo4j (if not already running)
# Update password in main.py to match your Neo4j instance
```

### Initialize Knowledge Graph
```bash
python main.py
# Select option 3 to setup knowledge graph
```

## Usage

### 1. Demonstrate Complete Flow
```bash
python main.py
# Select option 1
```
Shows the complete GraphRAG pipeline with example scenarios.

### 2. Interactive Query Mode  
```bash
python main.py
# Select option 2
```
Enter business scenarios and get executable test steps.

### 3. Populate Graph from Ontology
```bash
python -m src.graph.populate_graph
```
Loads your UI ontology (states, components, actions) into Neo4j.

## Example Flow

### Input Business Scenario
```
"User wants to log in and reach dashboard"
```

### Vector Search Finds Similar Scenarios
```
Feature: User can log in
Goal: Reach Dashboard  
Given app.launched()
When I choose to log in with a valid account
Then I should eventually be on Dashboard
```

### Knowledge Graph Provides Executable Steps
```python
[
    ExecutorStep(
        step_id=1, 
        description='Tap UserButton', 
        action_type='tap',
        query_for_qwen='Tap on the user profile button in the top navigation',
        alternative_actions=['Long press on user avatar', 'Swipe left to access profile'],
        expected_state='ProfilePage'
    ),
    ExecutorStep(
        step_id=2,
        description='Tap SettingsButton',
        action_type='tap', 
        query_for_qwen='Tap the settings button (gear icon) on profile page',
        alternative_actions=['Access settings from profile menu'],
        expected_state='SettingsPage'
    )
]
```

## Neo4j Queries

View the knowledge graph structure:

```cypher
// All nodes and relationships
MATCH (n) RETURN n LIMIT 25

// States and their components  
MATCH (s:State)-[:HAS_COMPONENT]->(c:Component) RETURN s, c

// Action paths from components to states
MATCH (c:Component)-[r:TAP|SWIPE|SCROLL|TYPE]->(s:State) RETURN c, r, s

// Find paths from HomePage to ProfilePage
MATCH path = (home:State {name: 'HomePage'})-[:HAS_COMPONENT]->(c:Component)
             -[action]->(profile:State {name: 'ProfilePage'})
RETURN path
```

## Ontology

Current ontology includes:

**States:**
- HomePage (with STEM, Explore, Following, Friends, ForYou sections)
- ProfilePage  
- SettingsPage

**Components:**
- Buttons: LikeButton, CommentButton, ShareButton, FollowButton
- Navigation: ProfileNavBar, SearchButton
- Inputs: NameInput, UserNameInput, BioInput, LinksInput

**Actions:**
- TAP, SWIPE, SCROLL, TYPE with properties for query_for_qwen and alternatives

## File Structure

```
knowledge-graph/
├── src/
│   ├── models/
│   │   ├── ontology.py      # State, Component, Action models
│   │   └── scenario.py      # Business scenario models
│   ├── graph/
│   │   ├── neo4j_knowledge_graph.py  # Core Neo4j interface
│   │   ├── populate_graph.py         # Ontology → Neo4j loader  
│   │   └── query_interface.py        # High-level query API
├── main.py                  # Main entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Next Steps

1. **Extend Ontology**: Add more states, components, and action relationships
2. **Business Scenarios**: Add your actual test scenarios to the vector store
3. **Action Properties**: Enhance action relationships with more detailed properties
4. **Visualization**: Use Neo4j Browser or build custom graph visualization
5. **Integration**: Connect to your actual GUI testing framework

## Troubleshooting

- **Neo4j Connection**: Ensure Neo4j is running and credentials are correct
- **Dependencies**: Install all requirements with `pip install -r requirements.txt`  
- **Empty Results**: Add business scenarios to vector store first
- **Graph Visualization**: Access Neo4j Browser at http://localhost:7474