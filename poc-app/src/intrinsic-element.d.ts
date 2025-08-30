import * as Lynx from '@lynx-js/types';

declare module '@lynx-js/types' {
  interface IntrinsicElements {
    "lynx-video": {
      src: string;
      autoplay?: boolean;
      loop?: boolean;
    };
  }
}
