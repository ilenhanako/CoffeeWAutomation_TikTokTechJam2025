// src/pages/Home.tsx
//import FeedList from "../components/feed/Feed.js";
import TopNav from "./components/layout/TopNav.js";
import BottomNav from "./components/layout/BottomNav.js";
import search from "./assets/lynx-logo.png";

 
const Home: React.FC = () => {
  return (
    <view className="h-screen w-full bg-black text-white">
      <TopNav onTabChange={(tab) => console.log("Active tab:", tab)} />
      <view style={{ flex: 1 }} />
      <image src={ search } className="liveTV-icon-image"/>
      <BottomNav />
    </view>
  )
}

export default Home;
