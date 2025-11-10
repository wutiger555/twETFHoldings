/**
 * 台股 ETF App - TypeScript 型別定義
 */

// ============================================================
// ETF 相關型別
// ============================================================

export interface ETF {
  code: string;              // ETF 代碼 (如 "0050")
  name: string;              // ETF 名稱 (如 "元大台灣50")
  issuer: string;            // 發行商 (如 "元大投信")
  type?: string;             // ETF 類型
  price?: number;            // 當前價格
  change?: number;           // 漲跌點數
  changePercent?: number;    // 漲跌幅 %
  volume?: number;           // 成交量
  marketValue?: number;      // 市值
  nav?: number;              // 淨值
  description?: string;      // 描述
}

export interface ETFHolding {
  stockCode: string;         // 個股代碼
  stockName: string;         // 個股名稱
  shares: number;            // 持股數
  weight: number;            // 權重 %
  marketValue: number;       // 市值
  price?: number;            // 當前股價
  change?: number;           // 漲跌點數
  changePercent?: number;    // 漲跌幅 %
  impactOnETF?: number;      // 對 ETF 影響 % (weight * changePercent / 100)
}

export interface ETFDetail extends ETF {
  holdings: ETFHolding[];
  totalHoldings: number;
  topHoldings: ETFHolding[];  // Top 10 持股
  updateDate: string;
  performance: {
    day: number;
    week: number;
    month: number;
    threeMonth: number;
    year: number;
    ytd: number;
  };
}

// ============================================================
// 個股相關型別
// ============================================================

export interface Stock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  marketCap?: number;
  pe?: number;
  pb?: number;
}

export interface StockHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ============================================================
// API 相關型別
// ============================================================

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// ============================================================
// 排序和篩選
// ============================================================

export type SortOption =
  | 'name'
  | 'code'
  | 'price'
  | 'changePercent'
  | 'volume'
  | 'marketValue';

export type SortDirection = 'asc' | 'desc';

export type IssuerFilter = 'all' | '元大' | '富邦' | '國泰' | '永豐' | '群益' | string;

export interface FilterOptions {
  issuer?: IssuerFilter;
  type?: string;
  sort?: SortOption;
  direction?: SortDirection;
  searchQuery?: string;
}

// ============================================================
// 使用者相關
// ============================================================

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  favorites: string[];        // 收藏的 ETF 代碼列表
  recentlyViewed: string[];   // 最近查看的 ETF
  notifications: boolean;
  language: 'zh-TW' | 'en';
}

// ============================================================
// Chart 相關
// ============================================================

export interface ChartDataPoint {
  x: number | string | Date;
  y: number;
  label?: string;
}

export interface PieChartData {
  label: string;
  value: number;
  color: string;
  percentage: number;
}

// ============================================================
// Navigation 相關
// ============================================================

export type RootStackParamList = {
  '(tabs)': undefined;
  'etf/[code]': { code: string };
  'stock/[code]': { code: string };
  'search': undefined;
  'settings': undefined;
};

export type TabParamList = {
  'index': undefined;
  'explore': undefined;
  'favorites': undefined;
  'profile': undefined;
};

// ============================================================
// 統計相關
// ============================================================

export interface MarketStats {
  totalETFs: number;
  avgChange: number;
  advancers: number;      // 上漲家數
  decliners: number;      // 下跌家數
  unchanged: number;      // 平盤家數
  totalVolume: number;
  totalMarketValue: number;
}

export interface PopularStock {
  code: string;
  name: string;
  changePercent: number;
  volume: number;
  rank: number;
}

// ============================================================
// Error Handling
// ============================================================

export interface AppError {
  code: string;
  message: string;
  details?: any;
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
