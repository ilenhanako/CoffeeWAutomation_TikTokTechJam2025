import { useNavigate, useLocation } from "react-router";
import { useState, useEffect } from "@lynx-js/react";

import homeFilled from "../../assets/bottomNavIcons/homeFilled.png";
import homeOutline from "../../assets/bottomNavIcons/homeOutline.png";
import inboxFilled from "../../assets/bottomNavIcons/inboxFilled.png";
import inboxOutline from "../../assets/bottomNavIcons/inboxOutline.png";
import shopFilled from "../../assets/bottomNavIcons/shopFilled.png";
import shopOutline from "../../assets/bottomNavIcons/shopOutline.png";
import upload from "../../assets/bottomNavIcons/upload.png";
import profileFilled from "../../assets/bottomNavIcons/profileFilled.png";
import profileOutline from "../../assets/bottomNavIcons/profileOutline.png";

import "./bottomnav.scss";
import NavIcon from "./BottomNavItems/NavIcon.js";

type NavItem = {
  label: string;
  route: string;
  icon: string;
  activeIcon: string;
};

const navItems: NavItem[] = [
  { label: "Home", route: "/home", icon: homeOutline, activeIcon: homeFilled },
  { label: "Shop", route: "/shop", icon: shopOutline, activeIcon: shopFilled },
  { label: "Upload", route: "/upload", icon: upload, activeIcon: upload },
  { label: "Inbox", route: "/inbox", icon: inboxOutline, activeIcon: inboxFilled },
  { label: "Profile", route: "/profile", icon: profileOutline, activeIcon: profileFilled },
];

function BottomNav() {
    const navigate = useNavigate();
    const location = useLocation();

    const [activeRoute, setActiveRoute] = useState(location.pathname);

    useEffect(() => {
    setActiveRoute(location.pathname);
    }, [location.pathname]);

    const isHome = activeRoute === "/home";
    const navBackground = isHome ? "white" : "black";

    return (
    <view className="bottom-nav" style={{ backgroundColor: navBackground }}>
        {navItems.map((item) => (
        <NavIcon
            key={item.label}
            label={item.label}
            src={item.icon}
            activeIcon={item.activeIcon}
            active={activeRoute === item.route}
            onClick={() => navigate(item.route)}
        />
        ))}
    </view>
    );
}

export default BottomNav;