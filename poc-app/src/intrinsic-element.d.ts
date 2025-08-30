import * as Lynx from '@lynx-js/types';

declare module '@lynx-js/types' {
  interface IntrinsicElements {
    "lynx-video": {
      id?: string;
      "accessibility-label"?: string;
      src: string;
      autoplay?: boolean;
      loop?: boolean;
      paused?: boolean;
    };

    "explorer-input": {
      id?: string;
      value?: string;
      placeholder?: string;
      "text-color"?: string;
      bindinput?: (e: { detail: { value: string } }) => void;
      bindblur?: () => void;
      "accessibility-label"?: string;
    };
  }
}
