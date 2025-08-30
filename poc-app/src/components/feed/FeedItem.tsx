// src/components/Feed/FeedItem.tsx
import type { Video } from "../../data/videos.js";
import VideoPlayer from "../video/VideoPlayer.js";
import VideoDescription from "../video/VideoDescription.js";
import VideoInteraction from "../video/VideoInteraction.js";
import "./feeditem.scss";
type FeedItemProps = {
  video: Video;
  id: string;
};
function FeedItem({ video, id }: FeedItemProps) {
  return (
    <view className="feed-item" id={id}>
      {/* Fullscreen video */}
      <VideoPlayer src={video.src} accessibilityLabel={video.accessibilityLabel} id={`video-${video.id}`} />

      {/* Overlay (bottom left) */}
      <view className="feed-item__description">
        <VideoDescription
          username={video.username}
          description={video.description}
          music={video.music}
        />
      </view>

      {/* Actions (right side) */}
      <view className="feed-item__interaction">
        <VideoInteraction
          likes={video.likes}
          comments={video.comments}
          shares={video.shares}
          avatar={video.avatar}
        />
      </view>
    </view>
  );
}

export default FeedItem;
