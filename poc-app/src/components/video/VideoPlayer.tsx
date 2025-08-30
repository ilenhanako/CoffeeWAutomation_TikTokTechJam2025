import demoSecondVideo from "../../assets/videos/IMG_0569.mp4"
import "./videoplayer.scss";


type VideoPlayerProps = {
  src: string;
  autoplay?: boolean;
  loop?: boolean;
};

const VideoPlayer: React.FC<VideoPlayerProps> = ({ src, autoplay = true, loop = true }) => {
  return (
    <view className="video-player">
      <lynx-video src={src} autoplay={autoplay} loop={loop} ></lynx-video>
    </view>
  );
};

export default VideoPlayer;
