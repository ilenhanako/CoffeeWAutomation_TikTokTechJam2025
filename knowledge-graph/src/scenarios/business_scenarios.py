"""
Business Scenarios for GUI Testing - TikTok-style App

This file contains all the business scenarios that are stored in the vector database
for semantic search. These scenarios cover Main Page, Profile Page, and Settings Page flows.
"""

from typing import List
from ..models.scenario import BusinessScenario, ScenarioType


def get_all_business_scenarios() -> List[BusinessScenario]:
    """Return all business scenarios for the GUI testing system"""
    
    scenarios = [
        # ========== MAIN PAGE (For You / Following Feed) ==========
        
        BusinessScenario(
            id=1,
            title="Navigate to main feed on app launch",
            feature="Main Page Navigation",
            goal="Access primary content feed",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["app.launched()", "User is logged in"],
            when_actions=["App opens to main screen"],
            then_expectations=[
                "For You tab is selected by default",
                "First video auto-plays",
                "Navigation bar is visible at bottom",
                "invariant video_player_controls_present"
            ],
            tags=["navigation", "launch", "main_page", "feed"]
        ),
        
        BusinessScenario(
            id=2,
            title="Switch between For You and Following tabs",
            feature="Main Page Navigation",
            goal="Toggle between content feeds",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on main page", "Both tabs are visible"],
            when_actions=["I tap Following tab", "I tap For You tab"],
            then_expectations=[
                "Tab selection indicator moves",
                "Feed content changes appropriately",
                "Previous video stops playing",
                "New feed video starts playing"
            ],
            tags=["navigation", "tabs", "feed_switch", "main_page"]
        ),
        
        BusinessScenario(
            id=3,
            title="Scroll through For You feed vertically",
            feature="Main Page Content Consumption",
            goal="Browse recommended videos",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on For You tab"],
            when_actions=["I swipe up to next video", "I continue swiping"],
            then_expectations=[
                "Next video loads and plays automatically",
                "Previous video stops and disappears",
                "Smooth transition between videos",
                "Video metadata loads (username, description, sounds)"
            ],
            tags=["scroll", "video_feed", "browse", "swipe"]
        ),
        
        BusinessScenario(
            id=4,
            title="Interact with video on main feed",
            feature="Main Page Video Interaction",
            goal="Engage with video content",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am viewing a video on main feed"],
            when_actions=["I tap like button", "I tap comment button", "I tap share button"],
            then_expectations=[
                "Like button animates and changes state",
                "Comment panel slides up from bottom",
                "Share menu appears with options",
                "All interactions are recorded"
            ],
            tags=["interaction", "like", "comment", "share", "engagement"]
        ),
        
        BusinessScenario(
            id=5,
            title="Access video creator's profile from main feed",
            feature="Main Page Profile Navigation",
            goal="View creator profile from video",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am watching a video", "Creator username is visible"],
            when_actions=["I tap on creator's username or profile picture"],
            then_expectations=[
                "Creator's profile page opens",
                "Video pauses in background",
                "Profile shows creator's video grid",
                "Follow/Following status is visible"
            ],
            tags=["profile", "creator", "navigation", "username"]
        ),
        
        BusinessScenario(
            id=6,
            title="Use sound from video on main feed",
            feature="Main Page Sound Interaction",
            goal="Access original sound",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am viewing a video with music/sound"],
            when_actions=["I tap on the spinning sound disc", "I tap on sound name"],
            then_expectations=[
                "Sound detail page opens",
                "Shows other videos using same sound",
                "Use This Sound button is available",
                "Sound metadata is displayed"
            ],
            tags=["sound", "music", "audio", "discover"]
        ),
        
        BusinessScenario(
            id=7,
            title="Pull to refresh main feed",
            feature="Main Page Content Refresh",
            goal="Get fresh content recommendations",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am at top of main feed"],
            when_actions=["I pull down from top of screen", "I release"],
            then_expectations=[
                "Refresh indicator appears",
                "New videos load at top of feed",
                "Content is updated",
                "Feed scrolls to refreshed content"
            ],
            tags=["refresh", "pull_to_refresh", "update", "content"]
        ),
        
        BusinessScenario(
            id=8,
            title="Handle video playback controls on main feed",
            feature="Main Page Video Playback",
            goal="Control video playback",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["A video is playing on main feed"],
            when_actions=["I tap video to pause", "I tap again to resume"],
            then_expectations=[
                "Video pauses when tapped",
                "Play/pause icon briefly appears",
                "Video resumes from same position",
                "Audio controls remain consistent"
            ],
            tags=["playback", "video_controls", "pause", "resume"]
        ),
        
        # ========== PROFILE PAGE ==========
        
        BusinessScenario(
            id=9,
            title="Navigate to own profile page",
            feature="Profile Page Navigation",
            goal="Access personal profile",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am logged in", "I am on main page"],
            when_actions=["I tap Profile tab in bottom navigation"],
            then_expectations=[
                "My profile page loads",
                "Profile stats are visible (followers, following, likes)",
                "My video grid is displayed",
                "Edit Profile button is present"
            ],
            tags=["profile", "navigation", "personal", "stats"]
        ),
        
        BusinessScenario(
            id=10,
            title="View and edit profile information",
            feature="Profile Page Management",
            goal="Update profile details",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on my profile page"],
            when_actions=["I tap Edit Profile", "I modify username/bio", "I tap Save"],
            then_expectations=[
                "Edit profile screen opens",
                "All editable fields are accessible",
                "Changes save successfully",
                "Updated info reflects on profile"
            ],
            tags=["edit_profile", "username", "bio", "save"]
        ),
        
        BusinessScenario(
            id=11,
            title="Browse own video grid on profile",
            feature="Profile Page Content",
            goal="View personal content library",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on my profile", "I have posted videos"],
            when_actions=["I scroll through video grid", "I tap on a video"],
            then_expectations=[
                "Video grid loads with thumbnails",
                "Tapped video opens in full screen",
                "Video plays from my content",
                "I can navigate back to grid"
            ],
            tags=["video_grid", "personal_content", "thumbnails", "playback"]
        ),
        
        BusinessScenario(
            id=12,
            title="Switch between video tabs on profile",
            feature="Profile Page Organization",
            goal="Navigate different content types",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on profile page"],
            when_actions=["I tap Videos tab", "I tap Liked tab", "I tap Private tab"],
            then_expectations=[
                "Content changes based on selected tab",
                "Tab indicator updates",
                "Appropriate videos display for each section",
                "Private tab requires authentication"
            ],
            tags=["tabs", "videos", "liked", "private", "organization"]
        ),
        
        BusinessScenario(
            id=13,
            title="View follower and following lists",
            feature="Profile Page Social Graph",
            goal="Access social connections",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on profile page"],
            when_actions=["I tap followers count", "I tap following count"],
            then_expectations=[
                "Follower/Following list opens",
                "User profiles are displayed",
                "I can follow/unfollow from list",
                "Search functionality is available"
            ],
            tags=["followers", "following", "social_graph", "connections"]
        ),
        
        BusinessScenario(
            id=14,
            title="Visit another user's profile",
            feature="Profile Page Browsing",
            goal="Explore other creator profiles",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I found another user's profile"],
            when_actions=["I browse their video grid", "I check their bio and stats"],
            then_expectations=[
                "Profile loads completely",
                "Follow button is visible and functional",
                "Video count and engagement stats show",
                "I can play their videos"
            ],
            tags=["other_profile", "creator", "browse", "follow"]
        ),
        
        BusinessScenario(
            id=15,
            title="Follow/Unfollow user from profile page",
            feature="Profile Page Social Actions",
            goal="Manage following relationships",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am viewing another user's profile"],
            when_actions=["I tap Follow button", "I tap Following to unfollow"],
            then_expectations=[
                "Follow button changes to Following",
                "Follower count increases for target user",
                "My Following count updates",
                "User appears in my Following feed"
            ],
            tags=["follow", "unfollow", "social_action", "relationship"]
        ),
        
        BusinessScenario(
            id=16,
            title="Share profile with others",
            feature="Profile Page Sharing",
            goal="Share user profile externally",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am viewing a profile page"],
            when_actions=["I tap share icon", "I select sharing method"],
            then_expectations=[
                "Share options appear",
                "Profile link is generated",
                "External app opens for sharing",
                "Share analytics are tracked"
            ],
            tags=["share", "profile_share", "external", "link"]
        ),
        
        # ========== SETTINGS PAGE ==========
        
        BusinessScenario(
            id=17,
            title="Navigate to settings from profile",
            feature="Settings Navigation",
            goal="Access app settings",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on my profile page"],
            when_actions=["I tap three-line menu icon", "I tap Settings and Privacy"],
            then_expectations=[
                "Settings menu opens",
                "Main setting categories are visible",
                "Account settings are accessible",
                "Privacy options are available"
            ],
            tags=["settings", "navigation", "menu", "privacy"]
        ),
        
        BusinessScenario(
            id=18,
            title="Update account information in settings",
            feature="Settings Account Management",
            goal="Modify account details",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings", "I am logged in"],
            when_actions=["I tap Account", "I update phone/email", "I save changes"],
            then_expectations=[
                "Account page loads",
                "Current info is pre-filled",
                "Verification process starts if needed",
                "Changes save successfully"
            ],
            tags=["account", "phone", "email", "verification"]
        ),
        
        BusinessScenario(
            id=19,
            title="Configure privacy settings",
            feature="Settings Privacy Control",
            goal="Manage account privacy",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Privacy", "I toggle private account", "I adjust who can comment/message"],
            then_expectations=[
                "Privacy options page opens",
                "Current privacy state is shown",
                "Toggle switches update immediately",
                "Changes take effect across app"
            ],
            tags=["privacy", "private_account", "toggle", "comments"]
        ),
        
        BusinessScenario(
            id=20,
            title="Manage notification preferences",
            feature="Settings Notifications",
            goal="Control notification types",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Notifications", "I toggle specific notification types"],
            then_expectations=[
                "Notification settings page loads",
                "All notification types are listed",
                "Toggle switches work properly",
                "System notification permissions update"
            ],
            tags=["notifications", "toggle", "permissions", "preferences"]
        ),
        
        BusinessScenario(
            id=21,
            title="Adjust content preferences",
            feature="Settings Content Control",
            goal="Customize content experience",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Content Preferences", "I adjust content filters"],
            then_expectations=[
                "Content settings page opens",
                "Filter options are available",
                "Restricted mode can be enabled",
                "Changes affect main feed content"
            ],
            tags=["content", "filters", "restricted_mode", "preferences"]
        ),
        
        BusinessScenario(
            id=22,
            title="Manage data and storage settings",
            feature="Settings Data Management",
            goal="Control app data usage",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Data Saver", "I adjust video quality", "I clear cache"],
            then_expectations=[
                "Data settings page loads",
                "Current storage usage is shown",
                "Quality options are available",
                "Cache clearing confirmation appears"
            ],
            tags=["data", "storage", "cache", "quality"]
        ),
        
        BusinessScenario(
            id=23,
            title="Access help and support from settings",
            feature="Settings Support",
            goal="Get help with app issues",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Help", "I browse help topics", "I report a problem"],
            then_expectations=[
                "Help center opens",
                "FAQ categories are organized",
                "Search functionality works",
                "Problem reporting form is available"
            ],
            tags=["help", "support", "faq", "report"]
        ),
        
        BusinessScenario(
            id=24,
            title="Log out from settings",
            feature="Settings Authentication",
            goal="Sign out of account",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am logged in", "I am in Settings"],
            when_actions=["I scroll to bottom", "I tap Log Out", "I confirm logout"],
            then_expectations=[
                "Logout confirmation dialog appears",
                "Account signs out successfully",
                "App returns to welcome screen",
                "Local data is cleared appropriately"
            ],
            tags=["logout", "sign_out", "confirmation", "authentication"]
        ),
        
        BusinessScenario(
            id=25,
            title="Switch account from settings",
            feature="Settings Multi-Account",
            goal="Change to different account",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I have multiple accounts", "I am in Settings"],
            when_actions=["I tap Account", "I tap Switch Account", "I select different account"],
            then_expectations=[
                "Account list appears",
                "I can select from saved accounts",
                "App switches to selected account",
                "Profile and content update accordingly"
            ],
            tags=["multi_account", "switch_account", "account_list"]
        ),
        
        BusinessScenario(
            id=26,
            title="Enable two-factor authentication",
            feature="Settings Security",
            goal="Enhance account security",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings", "2FA is not enabled"],
            when_actions=["I tap Security", "I enable 2FA", "I verify phone number"],
            then_expectations=[
                "Security settings page opens",
                "2FA setup process begins",
                "Verification code is sent",
                "2FA is activated successfully"
            ],
            tags=["security", "2fa", "verification", "authentication"]
        ),
        
        BusinessScenario(
            id=27,
            title="Manage blocked accounts",
            feature="Settings Privacy Management",
            goal="Control blocked users list",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings", "I have blocked some users"],
            when_actions=["I tap Privacy", "I tap Blocked Accounts", "I unblock a user"],
            then_expectations=[
                "Blocked accounts list loads",
                "All blocked users are shown",
                "Unblock option is available",
                "User is removed from blocked list"
            ],
            tags=["blocked", "privacy", "unblock", "management"]
        ),
        
        BusinessScenario(
            id=28,
            title="Download personal data",
            feature="Settings Data Rights",
            goal="Export account data",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am in Settings"],
            when_actions=["I tap Privacy", "I tap Download Data", "I request data export"],
            then_expectations=[
                "Data download page opens",
                "Export options are available",
                "Request confirmation is required",
                "Export status is trackable"
            ],
            tags=["data_export", "privacy", "download", "rights"]
        ),
        
        # ========== CROSS-PAGE NAVIGATION SCENARIOS ==========
        
        BusinessScenario(
            id=29,
            title="Navigate between main pages using bottom navigation",
            feature="Cross-Page Navigation",
            goal="Switch between primary app sections",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on any main page"],
            when_actions=["I tap different bottom navigation tabs"],
            then_expectations=[
                "Page transitions are smooth",
                "Previous page state is preserved",
                "Active tab indicator updates",
                "Content loads appropriately for each page"
            ],
            tags=["navigation", "bottom_nav", "transitions", "tabs"]
        ),
        
        BusinessScenario(
            id=30,
            title="Return to main feed from profile or settings",
            feature="Cross-Page Navigation",
            goal="Navigate back to primary content",
            scenario_type=ScenarioType.FEATURE,
            given_conditions=["I am on profile or settings page"],
            when_actions=["I tap Home tab", "I use back gesture/button"],
            then_expectations=[
                "Main feed loads",
                "Video playback resumes if applicable",
                "Feed position is preserved or refreshed",
                "Navigation state is updated"
            ],
            tags=["navigation", "back", "home", "feed_resume"]
        )
    ]
    
    return scenarios


def get_scenarios_by_feature(feature: str) -> List[BusinessScenario]:
    """Get all scenarios for a specific feature"""
    all_scenarios = get_all_business_scenarios()
    return [s for s in all_scenarios if s.feature.lower() == feature.lower()]


def get_scenarios_by_tag(tag: str) -> List[BusinessScenario]:
    """Get all scenarios containing a specific tag"""
    all_scenarios = get_all_business_scenarios()
    return [s for s in all_scenarios if tag.lower() in [t.lower() for t in s.tags]]


def get_scenario_by_id(scenario_id: int) -> BusinessScenario:
    """Get a specific scenario by ID"""
    all_scenarios = get_all_business_scenarios()
    for scenario in all_scenarios:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"No scenario found with ID {scenario_id}")