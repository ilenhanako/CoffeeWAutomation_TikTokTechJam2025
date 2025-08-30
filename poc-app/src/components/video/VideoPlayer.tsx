import { useState } from "react";
import "./videoplayer.scss";

type VideoPlayerProps = {
  src: string;
  autoplay?: boolean;
  loop?: boolean;
  accessibilityLabel: string;
  id: string;
};

function VideoPlayer({ src, autoplay = true, loop = true, accessibilityLabel, id }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(autoplay);

  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <view className="video-player" bindtap={handleTogglePlay}>
      <lynx-video
        id={id}
        accessibility-label={accessibilityLabel}
        src={src}
        autoplay={autoplay}
        loop={loop}
        paused={!isPlaying}
      ></lynx-video>

      {!isPlaying && (
        <view className="video-overlay">
          <text className="play-icon">▶</text>
        </view>
      )}
    </view>
  );
}

export default VideoPlayer;
