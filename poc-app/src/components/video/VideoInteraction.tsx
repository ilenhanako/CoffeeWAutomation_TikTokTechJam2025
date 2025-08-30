import { useState } from "@lynx-js/react";
import "./videointeraction.scss";
import likedd from "../../assets/videoicons/liked.png";
import like from "../../assets/videoicons/like.png";
import commentIcon from "../../assets/videoicons/comment.png";
import shareIcon from "../../assets/videoicons/share.png";
import { useNavigate, useLocation } from "react-router";


type VideoActionsProps = {
  likes: number;
  comments: number;
  shares: number;
  avatar: string;
};

function VideoInteraction({ likes, comments, shares, avatar }: VideoActionsProps) {
  const navigate = useNavigate();
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(likes);

  const handleLike = () => {
    if (liked) {
      setLikeCount((c) => c - 1);
    } else {
      setLikeCount((c) => c + 1);
    }
    setLiked((prev) => !prev);
  };

  return (
    <view className="video-actions">
      <image accessibility-label="User Avatar" src={avatar} className="video-actions__avatar" bindtap={() => navigate("/profile")} />

      <view accessibility-label="Like button" className="video-actions__item" bindtap={handleLike}>
        <image
          src={liked ?  likedd : like}
          className="video-actions__icon"
        />
        <text className="video-actions__count">{likeCount}</text>
      </view>

      <view accessibility-label="Comment button" className="video-actions__item" bindtap={() => console.log("Comment tapped")}>
        <image src={commentIcon} className="video-actions__icon" />
        <text className="video-actions__count">{comments}</text>
      </view>

      <view accessibility-label="Share button" className="video-actions__item" bindtap={() => console.log("Share tapped")}>
        <image src={shareIcon} className="video-actions__icon" />
        <text className="video-actions__count">{shares}</text>
      </view>
    </view>
  );
}

export default VideoInteraction;
