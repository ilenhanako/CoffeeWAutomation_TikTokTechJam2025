// src/components/Feed/FeedList.tsx
import { videos } from "../../data/videos.js";
import { useState } from "@lynx-js/react";
import FeedItem from "./FeedItem.js";
import "./feed.scss";

function FeedList() {
  const [currentIndex, setCurrentIndex] = useState(0);
  let scrollTimer: any = null;

  const handleScroll = (e: any) => {
    if (scrollTimer) clearTimeout(scrollTimer);

    scrollTimer = setTimeout(() => {
      const { scrollTop, scrollHeight } = e.detail;
      const itemHeight = scrollHeight / videos.length;

      const fracIndex = scrollTop / itemHeight;
      const baseIndex = Math.floor(fracIndex);
      const offset = fracIndex - baseIndex;

      let newIndex = currentIndex;

      const forwardThreshold = 0.1;
      const backwardThreshold = 0.2;

      if (offset > forwardThreshold && currentIndex === baseIndex) {
        newIndex = baseIndex + 1; // snap forward
      } else if (offset < (1 - backwardThreshold) && currentIndex === baseIndex + 1) {
        newIndex = baseIndex; // snap back
      }

      // Clamp
      if (newIndex < 0) newIndex = 0;
      if (newIndex >= videos.length) newIndex = videos.length - 1;

      if (newIndex !== currentIndex) {
        lynx
          .createSelectorQuery()
          .select("#feed-scroll")
          .invoke({
            method: "scrollTo",
            params: { index: newIndex, offset: 0, smooth: true },
          })
          .exec();

        setCurrentIndex(newIndex);
      }
    }, 100);
  };

  return (
    <scroll-view
      id="feed-scroll"
      scroll-orientation="vertical"
      className="feed-list"
      bindscroll={handleScroll}
    >
      {videos.map((video, i) => (
        <FeedItem key={video.id} video={video} id={`video-${i}`} />
      ))}
    </scroll-view>
  );
}

export default FeedList;
