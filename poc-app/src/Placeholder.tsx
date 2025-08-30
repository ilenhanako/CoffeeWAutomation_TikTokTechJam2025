// src/pages/Placeholder.tsx
type PlaceholderProps = {
  title: string;
};

const Placeholder: React.FC<PlaceholderProps> = ({ title }) => {
  return (
    <page>
      <view className="flex items-center justify-center h-screen bg-black text-white">
        <text className="text-lg">{title} Page (Coming Soon)</text>
      </view>
    </page>
  );
};

export default Placeholder;
