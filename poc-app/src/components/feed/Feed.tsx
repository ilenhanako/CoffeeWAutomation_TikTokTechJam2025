// src/components/Feed/FeedList.tsx
import { videos } from "../../data/videos.js";
import FeedItem from "./FeedItem.js";
import "./feed.scss";
function FeedList(){
  return (
    <scroll-view scroll-orientation="vertical" className="feed-list" >
      {videos.map(video => (
        <FeedItem key={video.id} video={video} />
      ))}
    </scroll-view>
  );
};

export default FeedList;
