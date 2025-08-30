import profileIcon from "../assets/videoicons/profile.png";
import demoVideo from "../assets/videos/IMG_0157.mp4";
import demoSecondVideo from "../assets/videos/IMG_0569.mp4"

export type Video = {
  id: number;
  src: string;
  username: string;
  avatar: string;
  description: string;
  music: string;
  likes: number;
  comments: number;
  shares: number;
};

export const videos: Video[] = [
  {
    id: 1,
    src: demoVideo,
    username: "demo_user",
    avatar: profileIcon,
    description: "Just chilling 😎 #fun",
    music: "Cool Beat - Demo Artist",
    likes: 1234,
    comments: 56,
    shares: 12,
  },
  {
    id: 2,
    src: demoSecondVideo,
    username: "catlover",
    avatar: profileIcon,
    description: "Cat vibes 🐱 #cute",
    music: "Chill Song - Demo Artist",
    likes: 980,
    comments: 42,
    shares: 8,
  },
];
