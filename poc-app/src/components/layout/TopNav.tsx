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
  { label: "Stem"},
  { label: "Explore"},
  { label: "Following" },
  { label: "Friends" },
  { label: "For You" },
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
      <view className="top-nav-side">
        <image
          accessibility-label="liveTV-icon"
          src={liveTV}
          className="liveTV-icon-image"
          bindtap={() => navigate("/live")}
        />
      </view>
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

      <view className="top-nav-side">
        <image
          accessibility-label="search-icon"
          src={search}
          className="search-icon-image"
          bindtap={() => navigate("/search")}
        />
      </view>
    </view>
  );
}


export default TopNav;