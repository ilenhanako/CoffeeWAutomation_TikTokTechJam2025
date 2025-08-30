import { useCallback, useEffect, useState } from '@lynx-js/react'

import './App.css'
import arrow from './assets/arrow.png'
import lynxLogo from './assets/bottomNavIcons/upload.png'
import reactLynxLogo from './assets/react-logo.png'
import TopNav from "./components/layout/TopNav.js";
import BottomNav from "./components/layout/BottomNav.js";
import search from "./assets/lynx-logo.png";
import FeedList from './components/feed/Feed.js'


function App(props: { onRender?: () => void }) {
  const [alterLogo, setAlterLogo] = useState(false)

  useEffect(() => {
    console.info('Hello, ReactLynx')
  }, [])
  props.onRender?.()

  const onTap = useCallback(() => {
    setAlterLogo(prevAlterLogo => !prevAlterLogo)
  }, [])

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