## Classes
**State**
HomePage
    - `STEMPage`
    - `ExplorePage`
    - `FollowingPage`
    - `FriendsPage`
    - `ForYouPage`
- `ProfilePage`
- `SettingsPage`
- `NavBar`

**UI Components [What buttons/widgets are in each state]**
HomePage:
- `LikeButton` W
- `ProfileNavBar` W
- `UserButton` W
- `Commentbutton`
- `ShareButton`
- `SearchButton`
- `LIVE`
- `STEM`
- `Explore`
- `Following`
- `Friends`
- `ForYou`
- `Search`

ProfilePage:
- `SettingsButton`
- `Following`
- `Followers`
- `Likes`
- `FollowButton`
- `MessageButton`

SettingsPage:
- `NameInput`
- `UserNameInput`
- `BioInput`
- `LinksInput`

Update my profile bio information
```
MATCH path = (foryou:State {name: 'HomePage'})-[:HAS_COMPONENT]->(navbar:Component {name: 'ProfileNavBar'})
               -[:SWIPE]->(profile:State {name: 'ProfilePage'})
               -[:HAS_COMPONENT]->(settingsBtn:Component {name: 'SettingsButton'})
               -[:TAP]->(settings:State {name: 'SettingsPage'})
  RETURN path,
         [navbar.name, settingsBtn.name] as components,
         ['SWIPE', 'TAP'] as actions,
         [profile.name, settings.name] as target_states
```

Navigate from home page to settings page
```
MATCH path = (start:State {name: 'HomePage'})-[:HAS_COMPONENT]->(c1:Component)
               -[a1:TAP|SWIPE|SCROLL|TYPE]->(mid:State)
               -[:HAS_COMPONENT]->(c2:Component)
               -[a2:TAP|SWIPE|SCROLL|TYPE]->(end:State {name: 'SettingsPage'})
  RETURN path,
         [node in nodes(path) | node.name] as node_names,
         [rel in relationships(path) | type(rel)] as relationship_types
```

View all nodes and rs
```
MATCH (n)-[r]->(m) RETURN n,r,m
```

