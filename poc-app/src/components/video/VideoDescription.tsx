// src/components/Video/VideoOverlay.tsx

type VideoOverlayProps = {
  username: string;
  description: string;
  music: string;
};

const VideoDescription: React.FC<VideoOverlayProps> = ({ username, description, music }) => {
  return (
    <view className="video-description">
      <text className="video-username">@ {username}</text>
      <text className="video-description-text">{description}</text>
      <text className="video-music">🎵 {music}</text>
    </view>
  );
};

export default VideoDescription;
