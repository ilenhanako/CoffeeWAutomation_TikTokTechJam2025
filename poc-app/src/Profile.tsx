// src/pages/Profile.tsx
import "./profile.scss";
import profilePic from "./assets/videoicons/profile.png";
import thumbnail1 from "./assets/profileThumbnails/pic1.jpg";
import thumbnail2 from "./assets/profileThumbnails/pic2.jpg";
import thumbnail3 from "./assets/profileThumbnails/pic3.jpg";
import thumbnail4 from "./assets/profileThumbnails/pic4.jpg";
import setting from "./assets/profileThumbnails/settings.png";
import { useNavigate, useLocation } from "react-router";


function Profile() {
    const navigate = useNavigate();

  return (
    <page className="profile-page">
        <view className="profile-topnav">
            <image src={setting} className="profile-settings" bindtap={() => navigate("/settings")}/>
        </view>
      {/* Header */}
      <view className="profile-header">
        <image src={profilePic} className="profile-avatar" />
        <text className="profile-username">@username</text>
        <text className="profile-bio">This is a sample bio.</text>
      </view>

      {/* Stats */}
      <view className="profile-stats">
        <view className="stat-item">
          <text className="stat-value">120</text>
          <text className="stat-label">Following</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">8.2k</text>
          <text className="stat-label">Followers</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">56.4k</text>
          <text className="stat-label">Likes</text>
        </view>
      </view>

      {/* Action buttons */}
      <view className="profile-actions">
        <text className="profile-btn" bindtap={() => console.log("Follow tapped")}>
          Follow
        </text>
        <text className="profile-btn secondary" bindtap={() => console.log("Message tapped")}>
          Message
        </text>
      </view>

      {/* Video grid */}
      <scroll-view
        className="video-grid"
        scroll-orientation="vertical"
      >
        <view className="video-row">
          <image src={thumbnail1} className="video-thumb" />
          <image src={thumbnail2} className="video-thumb" />
        </view>
        <view className="video-row">
          <image src={thumbnail3} className="video-thumb" />
          <image src={thumbnail4} className="video-thumb" />
        </view>
      </scroll-view>
    </page>
  );
}

export default Profile;
