// index.tsx
import { root } from '@lynx-js/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import Home from './Home.js';
import Placeholder from './Placeholder.js';
import App from './App.js';
import Profile from './Profile.js';
import Settings from './Settings.js';

root.render(
  <MemoryRouter>
    <Routes>
      {/* default landing page */}
      <Route path="/" element={<App />} />

      {/* other routes */}
      <Route path="/shop" element={<Placeholder title="Shop" />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/search" element={<Placeholder title="Search" />} />
      <Route path="/live" element={<Placeholder title="Live" />} />
      <Route path="/upload" element={<Placeholder title="Upload" />} />
      <Route path="/inbox" element={<Placeholder title="Inbox" />} />
      <Route path="/settings" element={<Settings />} />

      {/* fallback */}
      <Route path="*" element={<Placeholder title="Not Found" />} />
    </Routes>
  </MemoryRouter>
);

if ((import.meta as any).webpackHot) {
  (import.meta as any).webpackHot.accept();
}
