import "./profile.scss";
import { useState, useEffect } from "@lynx-js/react";
import { getProfile } from "./data/profile.js";
import thumbnail1 from "./assets/profileThumbnails/pic1.jpg";
import thumbnail2 from "./assets/profileThumbnails/pic2.jpg";
import thumbnail3 from "./assets/profileThumbnails/pic3.jpg";
import thumbnail4 from "./assets/profileThumbnails/pic4.jpg";
import setting from "./assets/profileThumbnails/settings.png";
import { useNavigate } from "react-router";
import BottomNav from "./components/layout/BottomNav.js";

function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(getProfile());

  useEffect(() => {
    setProfile(getProfile());
  }, []);

  return (
    <page className="profile-page">
      <view className="profile-topnav">
        <image
          src={setting}
          className="profile-settings"
          bindtap={() => navigate("/settings")}
        />
      </view>

      <view className="profile-header">
        <image src={profile.avatar} className="profile-avatar" />
        <text className="profile-username">@{profile.username}</text>
        <text className="profile-bio">{profile.bio}</text>
      </view>

      <view className="profile-stats">
        <view className="stat-item">
          <text className="stat-value">5k</text>
          <text className="stat-label">Following</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">10.2k</text>
          <text className="stat-label">Followers</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">10.4k</text>
          <text className="stat-label">Likes</text>
        </view>
      </view>
      <view className="profile-actions">
        <text className="profile-btn" bindtap={() => navigate("/edit")}>
          Edit
        </text>
      </view>

      <scroll-view className="video-grid" scroll-orientation="vertical">
        <view className="video-row">
          <image src={thumbnail1} className="video-thumb" />
          <image src={thumbnail2} className="video-thumb" />
        </view>
        <view className="video-row">
          <image src={thumbnail3} className="video-thumb" />
          <image src={thumbnail4} className="video-thumb" />
        </view>
      </scroll-view>

      <BottomNav />
    </page>
  );
}

export default Profile;
