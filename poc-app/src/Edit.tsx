import { useState } from "@lynx-js/react";
import { useNavigate } from "react-router";
import { getProfile, updateProfile } from "./data/profile.js";
import profilePic from "./assets/videoicons/profile.png"; // placeholder image
import "./edit.scss";

function EditProfile() {
  const navigate = useNavigate();
  const profile = getProfile();

  const [username, setUsername] = useState(profile.username);
  const [bio, setBio] = useState(profile.bio);
  const [popupType, setPopupType] = useState<null | "success" | "error">(null);

  const handleSave = (simulateError: boolean = false) => {
    if (simulateError) {
      setPopupType("error");
    } else {
      updateProfile({ username, bio });
      setPopupType("success");
    }
  };

  const closePopup = () => {
    if (popupType === "success") {
      navigate("/profile");
    }
    setPopupType(null);
  };

  return (
    <page className="edit-page">
      <view className="edit-header">
        <text className="edit-title">Edit Profile</text>
      </view>

      <view className="edit-avatar-section">
        <image src={profilePic} className="edit-avatar" />
        <text className="edit-change-text">Change photo</text>
      </view>

      <view className="edit-field">
        <text className="edit-label">Username</text>
        <explorer-input
          value={username}
          placeholder="Enter username"
          text-color="#ffffff"
          bindinput={(e: any) => setUsername(e.detail.value)}
          accessibility-label="Username input"
        />
      </view>

      <view className="edit-field">
        <text className="edit-label">Bio</text>
        <explorer-input
          value={bio}
          placeholder="Enter Bio"
          text-color="#ffffff"
          bindinput={(e: any) => setBio(e.detail.value)}
          accessibility-label="Bio input"
        />
      </view>

      <view className="edit-actions">
        <text
          accessibility-label="Save button"
          className="save-btn"
          bindtap={() => handleSave(true)}
        >
          Save
        </text>
      </view>

      {popupType && (
        <view className="popup-overlay" bindtap={closePopup}>
          <view className="popup-box">
            <text className="popup-message">
              {popupType === "success"
                ? "Profile updated successfully ✅"
                : "Something went wrong ❌"}
            </text>
            <text className="popup-close">Tap anywhere to close</text>
          </view>
        </view>
      )}
    </page>
  );
}

export default EditProfile;
