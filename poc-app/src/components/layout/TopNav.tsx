import { useState } from "@lynx-js/react";
import { useNavigate, useLocation } from "react-router";
import liveTV from "../../assets/topNavIcon/liveTV.png";
import search from "../../assets/topNavIcon/search.png";

import NavIcon from "./TopNavItems/NavIcon.js";
import "./topnav.scss";

type NavItem = {
  label: string;
};

const navItems: NavItem[] = [
  { label: "For You" },
  { label: "Friends" },
  { label: "Following" },
  { label: "Explore" },
  { label: "Stem" },
];

function TopNav({ onTabChange }: { onTabChange: (tab: string) => void }) {
  const [activeTab, setActiveTab] = useState("For You");
  const navigate = useNavigate();

  const handleClick = (label: string) => {
    setActiveTab(label);
    onTabChange(label);
  };

  return (
    <view className="top-nav">
      {/* Left: 15% */}
      <view className="top-nav-side">
        <image
          src={liveTV}
          className="liveTV-icon-image"
          bindtap={() => navigate("/live")}
        />
      </view>

      {/* Center: 70% */}
      <view className="top-nav-center">
        <scroll-view
          scroll-orientation="horizontal"
          className="top-nav-scroll"
        >
          {navItems.map((item) => (
            <NavIcon
              key={item.label}
              label={item.label}
              active={activeTab === item.label}
              onClick={() => handleClick(item.label)}
            />
          ))}
        </scroll-view>
      </view>

      {/* Right: 15% */}
      <view className="top-nav-side">
        <image
          src={search}
          className="search-icon-image"
          bindtap={() => navigate("/search")}
        />
      </view>
    </view>
  );
}


export default TopNav;