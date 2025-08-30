
import "./navicon.scss"

type NavIconProps = {
  label: string;
  src: string;
  activeIcon: string;
  onClick?: () => void;
  active?: boolean;
};

const NavIcon: React.FC<NavIconProps> = ({ label, src, activeIcon, onClick, active }) => {
  return (
    <view accessibility-label={label} className={`nav-icon ${active ? "active" : ""}`} bindtap={() => onClick?.()}>
      <image src={active ? activeIcon : src} className="nav-icon-image" />
      <text className="nav-icon-label">{label}</text>
    </view>
  );
};

export default NavIcon;
