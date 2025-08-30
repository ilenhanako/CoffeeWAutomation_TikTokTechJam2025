import { useCallback, useEffect, useState } from '@lynx-js/react'

import './App.css'
import TopNav from "./components/layout/TopNav.js";
import BottomNav from "./components/layout/BottomNav.js";
import FeedList from './components/feed/Feed.js'


function App() {

  return (
    <view>
      <view className='Background' />
      <view className='App'>
        <TopNav onTabChange={(tab) => console.log("Active tab:", tab)} />
        <FeedList/>
        <BottomNav />
      </view>
    </view>
  )
}

export default App