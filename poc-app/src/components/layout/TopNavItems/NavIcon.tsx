import "./navicon.scss"

type NavIconProps = {
  label: string;
  active?: boolean;
  onClick?: () => void;
};

const NavIcon: React.FC<NavIconProps> = ({ label, active, onClick }) => {
  return (
    <view
    accessibility-label={label}
    className={`nav-icon ${active ? "active" : ""}`}
    bindtap={() => onClick && onClick()}
    >
      <text className="text-topnav">{label}</text>
    </view>
  );
};

export default NavIcon;
