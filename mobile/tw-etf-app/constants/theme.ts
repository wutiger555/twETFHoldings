/**
 * 設計系統 - 極簡現代風格
 * 靈感來源: Robinhood, Webull, Trading212
 */

export const Colors = {
  // 主色調 - 深色主題 (預設)
  dark: {
    // 背景
    background: '#0A0A0A',           // 主背景 - 純黑
    backgroundSecondary: '#1A1A1A',  // 次要背景
    backgroundTertiary: '#2A2A2A',   // 卡片背景

    // 文字
    text: '#FFFFFF',                 // 主文字
    textSecondary: '#A0A0A0',        // 次要文字
    textTertiary: '#6A6A6A',         // 三級文字

    // 品牌色
    primary: '#00D4FF',              // 主品牌色 - 科技藍
    primaryDark: '#00A8CC',          // 深色變體
    primaryLight: '#33DDFF',         // 淺色變體

    // 功能色
    success: '#00D46A',              // 漲 - 綠色
    danger: '#FF3B69',               // 跌 - 紅色
    warning: '#FFB800',              // 警告 - 金色
    info: '#00D4FF',                 // 資訊 - 藍色

    // 邊框和分隔線
    border: '#2A2A2A',
    borderLight: '#3A3A3A',
    divider: '#1F1F1F',

    // 陰影和覆蓋層
    overlay: 'rgba(0, 0, 0, 0.8)',
    shadow: 'rgba(0, 0, 0, 0.5)',

    // 圖表色彩 (彩虹漸變)
    chart: {
      primary: '#00D4FF',
      secondary: '#7B61FF',
      tertiary: '#FF3B69',
      quaternary: '#00D46A',
      quinary: '#FFB800',
      gradient: ['#00D4FF', '#7B61FF', '#FF3B69', '#00D46A', '#FFB800']
    }
  },

  // 淺色主題
  light: {
    background: '#FFFFFF',
    backgroundSecondary: '#F5F5F5',
    backgroundTertiary: '#EFEFEF',

    text: '#0A0A0A',
    textSecondary: '#6A6A6A',
    textTertiary: '#A0A0A0',

    primary: '#00A8CC',
    primaryDark: '#008AAA',
    primaryLight: '#00D4FF',

    success: '#00B856',
    danger: '#E62E5C',
    warning: '#E6A500',
    info: '#00A8CC',

    border: '#E0E0E0',
    borderLight: '#F0F0F0',
    divider: '#EBEBEB',

    overlay: 'rgba(255, 255, 255, 0.95)',
    shadow: 'rgba(0, 0, 0, 0.1)',

    chart: {
      primary: '#00A8CC',
      secondary: '#6B51E6',
      tertiary: '#E62E5C',
      quaternary: '#00B856',
      quinary: '#E6A500',
      gradient: ['#00A8CC', '#6B51E6', '#E62E5C', '#00B856', '#E6A500']
    }
  }
};

export const Typography = {
  // 字體大小
  sizes: {
    xs: 10,
    sm: 12,
    base: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
  },

  // 字重
  weights: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
    extrabold: '800' as const,
  },

  // 行高
  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  }
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  '2xl': 32,
  '3xl': 40,
  '4xl': 48,
  '5xl': 64,
};

export const BorderRadius = {
  none: 0,
  sm: 4,
  base: 8,
  md: 12,
  lg: 16,
  xl: 20,
  full: 9999,
};

export const Shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.25,
    shadowRadius: 24,
    elevation: 12,
  }
};

export const Animation = {
  // 動畫時長
  duration: {
    fast: 150,
    normal: 250,
    slow: 350,
  },

  // 緩動函數
  easing: {
    default: 'ease-in-out',
    smooth: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  }
};

// 預設主題
export const theme = {
  colors: Colors.dark,
  typography: Typography,
  spacing: Spacing,
  borderRadius: BorderRadius,
  shadows: Shadows,
  animation: Animation,
};

export type Theme = typeof theme;
