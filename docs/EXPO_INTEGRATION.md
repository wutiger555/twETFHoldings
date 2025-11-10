# React Native Expo 整合指南

從零開始建立 React Native Expo App，整合後端 API。

---

## 📋 目錄

1. [為什麼選擇 Expo](#為什麼選擇-expo)
2. [環境準備](#環境準備)
3. [建立 Expo 專案](#建立-expo-專案)
4. [專案架構](#專案架構)
5. [API 整合](#api-整合)
6. [核心功能實作](#核心功能實作)
7. [測試與除錯](#測試與除錯)
8. [打包與發布](#打包與發布)

---

## 為什麼選擇 Expo？

### Expo vs React Native CLI

| 特性 | Expo | React Native CLI |
|------|------|------------------|
| **設定難度** | ⭐ 超簡單 | ⭐⭐⭐⭐ 複雜 |
| **開發速度** | ⭐⭐⭐⭐⭐ 快 | ⭐⭐⭐ 中等 |
| **更新方式** | OTA（即時） | 需重新打包 |
| **原生功能** | 大部分支援 | 完全支援 |
| **打包** | 雲端打包 | 本地打包 |
| **檔案大小** | 較大 | 較小 |

**結論**: Expo 適合快速開發和迭代，是 MVP 的最佳選擇。

---

## 環境準備

### 必要軟體

#### 1. Node.js 18+

```bash
# macOS (使用 Homebrew)
brew install node@18

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 驗證
node --version  # v18.x.x
npm --version   # 9.x.x
```

#### 2. Expo CLI

```bash
# 安裝 Expo CLI
npm install -g expo-cli

# 或使用 npx (不需安裝)
npx expo --version

# 驗證
expo --version
```

#### 3. Expo Go App

在手機上安裝 Expo Go：

- **iOS**: https://apps.apple.com/app/expo-go/id982107779
- **Android**: https://play.google.com/store/apps/details?id=host.exp.exponent

#### 4. 開發工具 (可選)

- **VS Code**: https://code.visualstudio.com/
- **Xcode** (iOS 模擬器): App Store (僅 macOS)
- **Android Studio** (Android 模擬器)

---

## 建立 Expo 專案

### Step 1: 初始化專案

```bash
# 在專案根目錄外建立 (與後端分開)
cd ..
npx create-expo-app etf-mobile-app

# 進入專案
cd etf-mobile-app
```

### Step 2: 專案結構

```
etf-mobile-app/
├── app/                    # 主要程式碼
│   ├── (tabs)/            # Tab 導航
│   │   ├── index.tsx      # 首頁
│   │   ├── explore.tsx    # 探索頁
│   │   └── _layout.tsx    # Tab 佈局
│   ├── _layout.tsx        # 根佈局
│   └── +not-found.tsx     # 404 頁面
├── assets/                # 圖片、字體等
├── components/            # 共用元件
├── constants/             # 常數
├── hooks/                 # 自訂 Hooks
├── services/              # API 服務
├── store/                 # 狀態管理
├── types/                 # TypeScript 型別
├── app.json               # Expo 配置
├── package.json
└── tsconfig.json
```

### Step 3: 安裝依賴

```bash
# 核心依賴
npm install

# Navigation (已內建在 Expo Router)
# 狀態管理
npm install zustand

# API 請求
npm install axios

# 圖表
npm install react-native-chart-kit react-native-svg

# AsyncStorage (本地儲存)
npx expo install @react-native-async-storage/async-storage

# SQLite (本地資料庫)
npx expo install expo-sqlite

# 其他有用的套件
npx expo install expo-constants
npx expo install expo-linking
```

### Step 4: 啟動開發伺服器

```bash
# 啟動
npx expo start

# 或使用特定平台
npx expo start --ios       # iOS 模擬器
npx expo start --android   # Android 模擬器
npx expo start --web       # Web 瀏覽器

# 掃描 QR Code 在實體手機上測試
# 使用 Expo Go App 掃描終端機顯示的 QR Code
```

---

## 專案架構

### 建議的目錄結構

```bash
# 建立目錄
mkdir -p services api types store hooks utils
```

詳細結構：

```
etf-mobile-app/
├── services/              # API 呼叫層
│   ├── api.ts            # Axios 配置
│   ├── etf.ts            # ETF API
│   ├── stock.ts          # 股票 API
│   └── cache.ts          # 快取管理
│
├── store/                 # Zustand 狀態管理
│   ├── etfStore.ts       # ETF 狀態
│   ├── stockStore.ts     # 股票狀態
│   └── userStore.ts      # 使用者狀態
│
├── types/                 # TypeScript 型別定義
│   ├── etf.ts
│   ├── stock.ts
│   └── api.ts
│
├── components/            # 共用元件
│   ├── ETFCard.tsx
│   ├── StockItem.tsx
│   ├── PriceChart.tsx
│   └── SearchBar.tsx
│
├── hooks/                 # 自訂 Hooks
│   ├── useETF.ts
│   ├── useStock.ts
│   └── useCache.ts
│
└── utils/                 # 工具函數
    ├── format.ts          # 格式化
    ├── storage.ts         # AsyncStorage 封裝
    └── constants.ts       # 常數
```

---

## API 整合

### Step 1: 建立 API 配置

創建 `services/api.ts`:

```typescript
import axios from 'axios';
import Constants from 'expo-constants';

// API Base URL
// 開發環境: 使用你的電腦 IP 或 ngrok
// 生產環境: 使用部署的 URL
const API_BASE_URL = __DEV__
  ? 'http://192.168.1.100:5000/api/v1'  // 替換成你的 IP
  : 'https://your-app.railway.app/api/v1';

// 創建 Axios 實例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器
api.interceptors.response.use(
  (response) => {
    console.log(`[API] ✅ ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`[API] ❌ ${error.config?.url}`, error.message);
    return Promise.reject(error);
  }
);

export default api;
```

### Step 2: 建立 ETF 服務

創建 `services/etf.ts`:

```typescript
import api from './api';
import { ETF, ETFHolding, ETFListResponse } from '../types/etf';

export const etfService = {
  /**
   * 取得所有 ETF 清單
   */
  async getETFs(page: number = 1, limit: number = 50): Promise<ETFListResponse> {
    const response = await api.get('/etf/etfs', {
      params: { page, limit }
    });
    return response.data.data;
  },

  /**
   * 取得單一 ETF 資訊
   */
  async getETF(code: string): Promise<ETF> {
    const response = await api.get(`/etf/etf/${code}`);
    return response.data.data;
  },

  /**
   * 取得 ETF 持股
   */
  async getETFHoldings(code: string, enrichPrices: boolean = false): Promise<ETFHolding[]> {
    const response = await api.get(`/etf/etf/${code}/holdings`, {
      params: { enrich_prices: enrichPrices }
    });
    return response.data.data.holdings;
  },

  /**
   * 搜尋 ETF
   */
  async searchETFs(query: string, limit: number = 20) {
    const response = await api.get('/search', {
      params: { q: query, type: 'ETF', limit }
    });
    return response.data.data;
  },
};
```

### Step 3: 建立股票服務

創建 `services/stock.ts`:

```typescript
import api from './api';
import { Stock, StockHistory } from '../types/stock';

export const stockService = {
  /**
   * 取得個股資訊
   */
  async getStock(code: string): Promise<Stock> {
    const response = await api.get(`/stock/${code}`);
    return response.data.data;
  },

  /**
   * 取得個股歷史價格
   */
  async getStockHistory(code: string, period: string = '30d'): Promise<StockHistory[]> {
    const response = await api.get(`/stock/${code}/history`, {
      params: { period }
    });
    return response.data.data.prices;
  },

  /**
   * 批次取得股票價格
   */
  async getBatchStocks(codes: string[]) {
    const response = await api.post('/stock/batch', { codes });
    return response.data.data;
  },
};
```

### Step 4: 建立型別定義

創建 `types/etf.ts`:

```typescript
export interface ETF {
  code: string;
  name: string;
  type?: string;
  issuer?: string;
}

export interface ETFHolding {
  stock_code: string;
  stock_name: string;
  shares: number;
  weight: number;
  current_price?: number;
  market_value?: number;
}

export interface ETFListResponse {
  items: ETF[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}
```

創建 `types/stock.ts`:

```typescript
export interface Stock {
  code: string;
  name: string;
  price: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  date: string;
}

export interface StockHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
```

---

## 核心功能實作

### 1. ETF 列表頁面

創建 `app/(tabs)/index.tsx`:

```typescript
import { StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, View } from '@/components/Themed';
import { useEffect, useState } from 'react';
import { etfService } from '@/services/etf';
import { ETF } from '@/types/etf';

export default function TabOneScreen() {
  const [etfs, setEtfs] = useState<ETF[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // 載入 ETF 清單
  const loadETFs = async () => {
    try {
      setLoading(true);
      const data = await etfService.getETFs();
      setEtfs(data.items);
    } catch (error) {
      console.error('載入 ETF 清單失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  // 下拉刷新
  const onRefresh = async () => {
    setRefreshing(true);
    await loadETFs();
    setRefreshing(false);
  };

  useEffect(() => {
    loadETFs();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ETF 列表</Text>

      <FlatList
        data={etfs}
        keyExtractor={(item) => item.code}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text style={styles.code}>{item.code}</Text>
            <Text style={styles.name}>{item.name}</Text>
          </View>
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  item: {
    padding: 15,
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  code: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  name: {
    fontSize: 14,
    color: '#666',
  },
});
```

### 2. 狀態管理 (Zustand)

創建 `store/etfStore.ts`:

```typescript
import { create } from 'zustand';
import { ETF, ETFHolding } from '@/types/etf';
import { etfService } from '@/services/etf';

interface ETFState {
  // 狀態
  etfs: ETF[];
  selectedETF: ETF | null;
  holdings: ETFHolding[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchETFs: () => Promise<void>;
  selectETF: (code: string) => Promise<void>;
  fetchHoldings: (code: string) => Promise<void>;
}

export const useETFStore = create<ETFState>((set) => ({
  // 初始狀態
  etfs: [],
  selectedETF: null,
  holdings: [],
  loading: false,
  error: null,

  // 取得 ETF 清單
  fetchETFs: async () => {
    set({ loading: true, error: null });
    try {
      const data = await etfService.getETFs();
      set({ etfs: data.items, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch ETFs', loading: false });
    }
  },

  // 選擇 ETF
  selectETF: async (code: string) => {
    set({ loading: true, error: null });
    try {
      const etf = await etfService.getETF(code);
      set({ selectedETF: etf, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch ETF', loading: false });
    }
  },

  // 取得持股
  fetchHoldings: async (code: string) => {
    set({ loading: true, error: null });
    try {
      const holdings = await etfService.getETFHoldings(code);
      set({ holdings, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch holdings', loading: false });
    }
  },
}));
```

### 3. 自訂 Hook

創建 `hooks/useETF.ts`:

```typescript
import { useEffect } from 'react';
import { useETFStore } from '@/store/etfStore';

export function useETF(code?: string) {
  const {
    etfs,
    selectedETF,
    holdings,
    loading,
    error,
    fetchETFs,
    selectETF,
    fetchHoldings,
  } = useETFStore();

  useEffect(() => {
    if (code) {
      selectETF(code);
      fetchHoldings(code);
    }
  }, [code]);

  return {
    etfs,
    selectedETF,
    holdings,
    loading,
    error,
    fetchETFs,
    selectETF,
    fetchHoldings,
  };
}
```

---

## 測試與除錯

### 取得本機 IP

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4

# 在 .env 中設定
echo "API_URL=http://192.168.1.100:5000/api/v1" > .env
```

### 使用 React Native Debugger

```bash
# 安裝
brew install --cask react-native-debugger  # macOS

# 啟動
open "rndebugger://set-debugger-loc?host=localhost&port=19000"

# 在 App 中按 Cmd+D (iOS) 或 Cmd+M (Android)
# 選擇 "Debug"
```

### 查看網路請求

在 Chrome DevTools 中：
1. 開啟 Network tab
2. 在 App 中執行 API 請求
3. 查看請求和回應

---

## 打包與發布

### iOS (TestFlight)

```bash
# 1. 安裝 EAS CLI
npm install -g eas-cli

# 2. 登入 Expo
eas login

# 3. 配置專案
eas build:configure

# 4. 建置 iOS
eas build --platform ios

# 5. 提交到 TestFlight
eas submit --platform ios
```

### Android (Google Play)

```bash
# 建置 Android
eas build --platform android

# 提交到 Google Play
eas submit --platform android
```

---

## 附錄：完整範例檔案

詳細的範例檔案請見 `mobile/` 目錄。

---

**開始開發你的 React Native App 吧！** 🚀
