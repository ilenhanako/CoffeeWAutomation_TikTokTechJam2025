

import profilePic from "../assets/videoicons/profile.png";

export type ProfileData = {
  username: string;
  bio: string;
  avatar: string;
};

let profile: ProfileData = {
  username: "demo_user",
  bio: "This is a sample bio.",
  avatar: profilePic
};
export function getProfile() {
  return profile;
}
export function updateProfile(newData: Partial<ProfileData>) {
  profile = { ...profile, ...newData };
}
