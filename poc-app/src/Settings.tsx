// src/pages/SettingsPage.tsx
import "./settings.scss";

function SettingsPage() {
  return (
    <view className="settings-page">
      {/* Top navigation */}
      <view className="settings-topnav">
        <text className="settings-back">←</text>
        <text className="settings-title">Settings</text>
      </view>

      {/* Scrollable content */}
      <scroll-view scroll-orientation="vertical" className="settings-content">

        {/* Account Section */}
        <view className="settings-section">
          <text className="settings-section-title">Account</text>
          <text className="settings-item">Manage account</text>
          <text className="settings-item">Privacy</text>
          <text className="settings-item">Security</text>
        </view>

        {/* Notifications Section */}
        <view className="settings-section">
          <text className="settings-section-title">Notifications</text>
          <text className="settings-item">Push notifications</text>
          <text className="settings-item">Live notifications</text>
        </view>

        {/* General Section */}
        <view className="settings-section">
          <text className="settings-section-title">General</text>
          <text className="settings-item">Language</text>
          <text className="settings-item">Accessibility</text>
        </view>

        {/* About Section */}
        <view className="settings-section">
          <text className="settings-section-title">About</text>
          <text className="settings-item">Community Guidelines</text>
          <text className="settings-item">Terms of Service</text>
          <text className="settings-item">Privacy Policy</text>
        </view>

        {/* Logout */}
        <view className="settings-section">
          <text className="settings-item logout">Log out</text>
        </view>

      </scroll-view>
    </view>
  );
}

export default SettingsPage;
