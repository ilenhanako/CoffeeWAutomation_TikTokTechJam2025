<<<<<<< HEAD
import "./profile.scss";
import { useState, useEffect } from "@lynx-js/react";
import { getProfile } from "./data/profile.js";
=======
// src/pages/Profile.tsx
import "./profile.scss";
import profilePic from "./assets/videoicons/profile.png";
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
import thumbnail1 from "./assets/profileThumbnails/pic1.jpg";
import thumbnail2 from "./assets/profileThumbnails/pic2.jpg";
import thumbnail3 from "./assets/profileThumbnails/pic3.jpg";
import thumbnail4 from "./assets/profileThumbnails/pic4.jpg";
import setting from "./assets/profileThumbnails/settings.png";
<<<<<<< HEAD
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

      {/* Profile header */}
      <view className="profile-header">
        <image src={profile.avatar} className="profile-avatar" />
        <text className="profile-username">@{profile.username}</text>
        <text className="profile-bio">{profile.bio}</text>
=======
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
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
      </view>

      {/* Stats */}
      <view className="profile-stats">
        <view className="stat-item">
<<<<<<< HEAD
          <text className="stat-value">5k</text>
          <text className="stat-label">Following</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">10.2k</text>
          <text className="stat-label">Followers</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">10.4k</text>
=======
          <text className="stat-value">120</text>
          <text className="stat-label">Following</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">8.2k</text>
          <text className="stat-label">Followers</text>
        </view>
        <view className="stat-item">
          <text className="stat-value">56.4k</text>
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
          <text className="stat-label">Likes</text>
        </view>
      </view>

      {/* Action buttons */}
      <view className="profile-actions">
<<<<<<< HEAD
        <text className="profile-btn" bindtap={() => navigate("/edit")}>
          Edit
=======
        <text className="profile-btn" bindtap={() => console.log("Follow tapped")}>
          Follow
        </text>
        <text className="profile-btn secondary" bindtap={() => console.log("Message tapped")}>
          Message
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
        </text>
      </view>

      {/* Video grid */}
<<<<<<< HEAD
      <scroll-view className="video-grid" scroll-orientation="vertical">
=======
      <scroll-view
        className="video-grid"
        scroll-orientation="vertical"
      >
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
        <view className="video-row">
          <image src={thumbnail1} className="video-thumb" />
          <image src={thumbnail2} className="video-thumb" />
        </view>
        <view className="video-row">
          <image src={thumbnail3} className="video-thumb" />
          <image src={thumbnail4} className="video-thumb" />
        </view>
      </scroll-view>
<<<<<<< HEAD

      <BottomNav />
=======
>>>>>>> 514ca7cc0b4f05d7807be43bf2c88e66f0661426
    </page>
  );
}

export default Profile;
