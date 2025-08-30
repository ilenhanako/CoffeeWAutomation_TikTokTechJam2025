import BottomNav from "./components/layout/BottomNav.js";
import "./placeholder.scss";

type PlaceholderProps = {
  title: string;
};

function Placeholder({ title }: PlaceholderProps) {
  return (
    <page className="placeholder-page">
      <view className="placeholder-content">
        <text className="placeholder-text">{title} Page (Coming Soon)</text>
      </view>
      <BottomNav />
    </page>
  );
}

export default Placeholder;
