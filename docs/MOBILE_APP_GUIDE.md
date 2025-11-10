# 📱 台股 ETF App - 完整開發指南

> **極簡現代風格的 ETF 分析工具 | React Native + Expo**

---

## 📋 目錄

1. [專案概覽](#專案概覽)
2. [已完成架構](#已完成架構)
3. [設計理念](#設計理念)
4. [快速開始](#快速開始)
5. [核心功能實作指南](#核心功能實作指南)
6. [UI 組件參考](#ui-組件參考)
7. [API 整合](#api-整合)
8. [部署與發布](#部署與發布)

---

## 🎯 專案概覽

### 功能目標

這是一個專為台灣投資者設計的 ETF 分析工具，主要功能：

1. **ETF 列表與篩選**
   - 按發行商篩選（元大、富邦、國泰等）
   - 按績效排序
   - 即時漲跌幅顯示

2. **視覺化持股分析** ⭐ 核心功能
   - 美觀的圓餅圖展示前 10 大持股
   - 直觀的權重百分比
   - 互動式圖表體驗

3. **個股影響力分析** ⭐ 獨特功能
   - 計算個股漲跌對 ETF 的影響
   - 公式：`影響 = 持股權重 × 個股漲跌幅 / 100`
   - 即時顯示貢獻度

4. **搜尋與收藏**
   - 全文搜尋 ETF 和個股
   - 自選清單管理
   - 最近查看記錄

### 設計風格

**參考對象**：Robinhood, Webull, Trading212

**設計原則**：
- ✨ **極簡主義**：去除冗餘元素，聚焦核心資訊
- 🎨 **現代感**：使用深色主題、大膽配色
- 🔬 **科技感**：流暢動畫、細膩陰影
- 📊 **資訊密度**：在極簡中保持資訊豐富

**配色方案**：
```javascript
主背景：#0A0A0A (純黑)
次要背景：#1A1A1A
品牌色：#00D4FF (科技藍)
漲：#00D46A (綠)
跌：#FF3B69 (紅)
```

---

## ✅ 已完成架構

### 檔案結構

```
mobile/tw-etf-app/
├── 📄 配置檔案
│   ├── package.json          ← 依賴管理
│   ├── app.json              ← Expo 配置
│   └── tsconfig.json         ← TypeScript 配置
│
├── 🎨 設計系統
│   └── constants/
│       └── theme.ts          ← 完整的設計 Token
│
├── 📐 型別定義
│   └── types/
│       └── index.ts          ← 完整的 TypeScript 型別
│
├── 🔌 API 服務層
│   └── services/
│       └── api.ts            ← 完整的 API 客戶端
│                               - ETF 列表/詳情
│                               - 個股價格/歷史
│                               - 搜尋功能
│                               - 快取機制
│
├── 💾 狀態管理
│   └── stores/
│       └── useETFStore.ts    ← Zustand Store
│                               - ETF 資料管理
│                               - 收藏管理
│                               - 偏好設定
│
├── 🛠️ 工具函數
│   └── utils/
│       ├── format.ts         ← 格式化函數
│       └── calculations.ts   ← 計算邏輯
│
└── 📱 App 結構
    └── app/
        ├── _layout.tsx       ← Root Layout
        └── (tabs)/
            └── _layout.tsx   ← Tab Navigation
```

### 核心功能已實作

✅ **完整的 API 整合**
- 連接後端 Flask API
- 自動快取機制 (5分鐘)
- 錯誤處理與重試
- 批次請求優化

✅ **狀態管理**
- Zustand 全局狀態
- 本地持久化 (AsyncStorage)
- 收藏與最近查看

✅ **工具函數**
- 價格/百分比格式化
- 個股影響力計算
- 圓餅圖資料生成

✅ **設計系統**
- 完整的 Theme 配置
- 顏色/間距/字體 Token
- 動畫參數

---

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝 Node.js 18+
node --version

# 安裝 Expo CLI
npm install -g expo-cli

# 安裝 iOS Simulator (macOS)
# 或 Android Emulator
```

### 2. 安裝專案

```bash
cd mobile/tw-etf-app

# 安裝依賴
npm install

# 啟動開發伺服器
npx expo start
```

### 3. 配置 API 端點

建立環境變數檔案：

```bash
# .env
EXPO_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

或在 `services/api.ts` 中直接修改：

```typescript
const API_CONFIG = {
  DEV_URL: 'http://localhost:5000/api/v1',      // 本地開發
  PROD_URL: 'https://your-api.com/api/v1',      // 生產環境
};
```

### 4. 測試 API 連接

在 Expo 啟動後，在 App 中測試：

```typescript
import { api } from '@/services/api';

// 測試健康檢查
const health = await api.healthCheck();
console.log(health);

// 測試取得 ETF 列表
const etfs = await api.getETFList({ page: 1, limit: 10 });
console.log(etfs);
```

---

## 🎨 核心功能實作指南

### 功能 1: ETF 列表頁面

**檔案**: `app/(tabs)/index.tsx`

**需要實作的組件**：

```tsx
import React, { useEffect } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { useETFStore } from '@/stores/useETFStore';
import { theme } from '@/constants/theme';

export default function HomePage() {
  const { etfs, etfsLoading, loadETFs } = useETFStore();

  useEffect(() => {
    loadETFs();
  }, []);

  return (
    <View style={styles.container}>
      {/* Header with Title and Filter */}
      <View style={styles.header}>
        <Text style={styles.title}>台股 ETF</Text>
        <FilterButton />
      </View>

      {/* ETF List */}
      <FlatList
        data={etfs}
        renderItem={({ item }) => <ETFCard etf={item} />}
        keyExtractor={(item) => item.code}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.base,
    paddingTop: 60, // Safe area
  },
  title: {
    fontSize: theme.typography.sizes['3xl'],
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
  },
  list: {
    padding: theme.spacing.base,
  },
});
```

**ETFCard 組件**：

```tsx
// components/ETFCard.tsx
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { ETF } from '@/types';
import { theme } from '@/constants/theme';
import { formatPrice, formatPercent, getChangeColor } from '@/utils/format';

interface ETFCardProps {
  etf: ETF;
}

export function ETFCard({ etf }: ETFCardProps) {
  const router = useRouter();
  const changeColor = getChangeColor(etf.changePercent, theme);

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/etf/${etf.code}`)}
      activeOpacity={0.7}
    >
      {/* 左側：ETF 資訊 */}
      <View style={styles.left}>
        <Text style={styles.code}>{etf.code}</Text>
        <Text style={styles.name}>{etf.name}</Text>
        <Text style={styles.issuer}>{etf.issuer}</Text>
      </View>

      {/* 右側：價格與漲跌 */}
      <View style={styles.right}>
        <Text style={styles.price}>
          {formatPrice(etf.price)}
        </Text>
        <Text style={[styles.change, { color: changeColor }]}>
          {formatPercent(etf.changePercent)}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.base,
    marginBottom: theme.spacing.md,
    ...theme.shadows.sm,
  },
  left: {
    flex: 1,
  },
  code: {
    fontSize: theme.typography.sizes.lg,
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
  },
  name: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  issuer: {
    fontSize: theme.typography.sizes.xs,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  right: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: theme.typography.sizes.xl,
    fontWeight: theme.typography.weights.semibold,
    color: theme.colors.text,
  },
  change: {
    fontSize: theme.typography.sizes.md,
    fontWeight: theme.typography.weights.medium,
    marginTop: 4,
  },
});
```

---

### 功能 2: ETF 詳情頁 (圓餅圖) ⭐

**檔案**: `app/etf/[code].tsx`

**核心：圓餅圖組件**

```tsx
// components/PieChart.tsx
import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { VictoryPie } from 'victory-native';
import { theme } from '@/constants/theme';
import { generatePieChartData } from '@/utils/calculations';
import type { ETFHolding } from '@/types';

const SCREEN_WIDTH = Dimensions.get('window').width;

interface PieChartProps {
  holdings: ETFHolding[];
}

export function HoldingsPieChart({ holdings }: PieChartProps) {
  // 產生圓餅圖資料 (前 10 大持股)
  const chartData = generatePieChartData(
    holdings,
    10,
    theme.colors.chart.gradient
  );

  return (
    <View style={styles.container}>
      {/* 標題 */}
      <Text style={styles.title}>持股比重</Text>

      {/* 圓餅圖 */}
      <View style={styles.chartContainer}>
        <VictoryPie
          data={chartData}
          x="label"
          y="value"
          width={SCREEN_WIDTH - 32}
          height={300}
          innerRadius={80}  // 甜甜圈圖
          labelRadius={120}
          style={{
            labels: {
              fill: theme.colors.text,
              fontSize: 12,
              fontWeight: '600',
            },
            data: {
              fill: ({ datum }) => datum.color,
            },
          }}
          labels={({ datum }) => `${datum.percentage.toFixed(1)}%`}
          animate={{
            duration: 1000,
            onLoad: { duration: 1000 },
          }}
        />

        {/* 中心文字 */}
        <View style={styles.centerText}>
          <Text style={styles.centerTitle}>Top 10</Text>
          <Text style={styles.centerSubtitle}>持股</Text>
        </View>
      </View>

      {/* 圖例 */}
      <View style={styles.legend}>
        {chartData.map((item, index) => (
          <View key={index} style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: item.color }]} />
            <Text style={styles.legendLabel}>{item.label}</Text>
            <Text style={styles.legendValue}>{item.percentage.toFixed(2)}%</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginVertical: theme.spacing.base,
  },
  title: {
    fontSize: theme.typography.sizes.xl,
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  chartContainer: {
    alignItems: 'center',
    position: 'relative',
  },
  centerText: {
    position: 'absolute',
    top: '50%',
    alignItems: 'center',
  },
  centerTitle: {
    fontSize: theme.typography.sizes.'2xl',
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.primary,
  },
  centerSubtitle: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.textSecondary,
  },
  legend: {
    marginTop: theme.spacing.lg,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: theme.spacing.sm,
  },
  legendLabel: {
    flex: 1,
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.text,
  },
  legendValue: {
    fontSize: theme.typography.sizes.sm,
    fontWeight: theme.typography.weights.semibold,
    color: theme.colors.primary,
  },
});
```

---

### 功能 3: 個股影響力分析 ⭐

**檔案**: `components/ImpactAnalysis.tsx`

```tsx
import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { theme } from '@/constants/theme';
import { calculateStockImpact, sortByImpact } from '@/utils/calculations';
import { formatPercent, getChangeColor } from '@/utils/format';
import type { ETFHolding } from '@/types';

interface ImpactAnalysisProps {
  holdings: ETFHolding[];
}

export function ImpactAnalysis({ holdings }: ImpactAnalysisProps) {
  // 排序：影響力最大的在前
  const sortedHoldings = sortByImpact(holdings, true);
  const topImpact = sortedHoldings.slice(0, 20);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>個股影響力分析</Text>
      <Text style={styles.subtitle}>
        計算公式：影響 = 持股權重 × 個股漲跌幅 ÷ 100
      </Text>

      <FlatList
        data={topImpact}
        keyExtractor={(item) => item.stockCode}
        renderItem={({ item }) => {
          const impact = calculateStockImpact(
            item.weight,
            item.changePercent || 0
          );
          const impactColor = getChangeColor(impact, theme);

          return (
            <View style={styles.item}>
              {/* 左側：股票資訊 */}
              <View style={styles.left}>
                <Text style={styles.stockCode}>{item.stockCode}</Text>
                <Text style={styles.stockName}>{item.stockName}</Text>
                <Text style={styles.weight}>
                  權重 {item.weight.toFixed(2)}%
                </Text>
              </View>

              {/* 右側：漲跌與影響 */}
              <View style={styles.right}>
                <Text style={[styles.change, { color: impactColor }]}>
                  {formatPercent(item.changePercent)}
                </Text>
                <Text style={[styles.impact, { color: impactColor }]}>
                  影響 {formatPercent(impact)}
                </Text>
              </View>
            </View>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginVertical: theme.spacing.base,
  },
  title: {
    fontSize: theme.typography.sizes.xl,
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: theme.typography.sizes.xs,
    color: theme.colors.textTertiary,
    marginTop: 4,
    marginBottom: theme.spacing.md,
  },
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  left: {
    flex: 1,
  },
  stockCode: {
    fontSize: theme.typography.sizes.md,
    fontWeight: theme.typography.weights.semibold,
    color: theme.colors.text,
  },
  stockName: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  weight: {
    fontSize: theme.typography.sizes.xs,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  right: {
    alignItems: 'flex-end',
  },
  change: {
    fontSize: theme.typography.sizes.md,
    fontWeight: theme.typography.weights.semibold,
  },
  impact: {
    fontSize: theme.typography.sizes.sm,
    fontWeight: theme.typography.weights.medium,
    marginTop: 4,
  },
});
```

---

## 📐 UI 組件參考

### 需要實作的通用組件

#### 1. Button

```tsx
// components/Button.tsx
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { theme } from '@/constants/theme';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  disabled?: boolean;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
}: ButtonProps) {
  return (
    <TouchableOpacity
      style={[
        styles.button,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'outline' && styles.outline,
        disabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator color={theme.colors.text} />
      ) : (
        <Text style={styles.text}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}
```

#### 2. SearchBar

```tsx
// components/SearchBar.tsx
import { TextInput, View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '@/constants/theme';

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChangeText, placeholder }: SearchBarProps) {
  return (
    <View style={styles.container}>
      <Ionicons name="search" size={20} color={theme.colors.textSecondary} />
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder || '搜尋 ETF 或個股...'}
        placeholderTextColor={theme.colors.textTertiary}
      />
    </View>
  );
}
```

#### 3. LoadingScreen

```tsx
// components/LoadingScreen.tsx
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { theme } from '@/constants/theme';

export function LoadingScreen() {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={theme.colors.primary} />
    </View>
  );
}
```

---

## 🔌 API 整合

### 使用方式

所有 API 呼叫都通過 `services/api.ts`：

```typescript
import { api } from '@/services/api';

// 1. 取得 ETF 列表
const etfs = await api.getETFList({ page: 1, limit: 50 });

// 2. 取得 ETF 詳情
const detail = await api.getETFDetail('0050');

// 3. 取得持股 (含即時價格)
const holdings = await api.getETFHoldings('0050', true);

// 4. 搜尋
const results = await api.search('台積電', 'STOCK');

// 5. 批次取得股價
const prices = await api.getBatchStockPrices(['2330', '2317', '2454']);
```

### 錯誤處理

```typescript
try {
  const data = await api.getETFDetail('0050');
} catch (error) {
  console.error(error.message);
  // 顯示錯誤訊息給使用者
}
```

### 快取策略

- ETF 列表：5 分鐘
- ETF 詳情：5 分鐘
- 個股價格：1 分鐘
- 自動清除過期快取

---

## 📱 完整頁面實作清單

### 必須實作的頁面

1. ✅ **首頁 (app/(tabs)/index.tsx)**
   - ETF 列表
   - 篩選按鈕
   - 排序功能

2. ✅ **探索頁 (app/(tabs)/explore.tsx)**
   - 熱門 ETF
   - 市場統計
   - 發行商分類

3. ✅ **自選頁 (app/(tabs)/favorites.tsx)**
   - 收藏的 ETF 列表
   - 快速查看

4. ✅ **我的頁 (app/(tabs)/profile.tsx)**
   - 設定
   - 主題切換
   - 快取管理

5. ⭐ **ETF 詳情頁 (app/etf/[code].tsx)**
   - 基本資訊
   - 圓餅圖
   - 持股列表
   - 影響力分析

---

## 🚀 部署與發布

### 1. 建置 iOS App

```bash
# 安裝 EAS CLI
npm install -g eas-cli

# 登入 Expo
eas login

# 配置專案
eas build:configure

# 建置 iOS
eas build --platform ios
```

### 2. 建置 Android App

```bash
# 建置 Android
eas build --platform android
```

### 3. 發布到 App Store

詳細步驟請參考：
- [Expo 官方文件](https://docs.expo.dev/submit/ios/)
- [App Store Connect](https://appstoreconnect.apple.com/)

---

## 🎯 下一步

### 立即可做

1. **補充 UI 組件**
   - 參考上方組件參考章節
   - 建立 `components/` 目錄下的組件

2. **實作主要頁面**
   - 按照頁面實作清單逐一完成
   - 使用已建立好的 API 和 Store

3. **測試與優化**
   - 在模擬器中測試
   - 優化載入速度
   - 調整動畫效果

### 進階功能

- [ ] 推播通知 (ETF 漲跌提醒)
- [ ] 深色/淺色主題切換
- [ ] 多語言支援 (中文/英文)
- [ ] 價格警示功能
- [ ] 圖表互動增強

---

## 📚 參考資源

### 官方文件
- [Expo 文件](https://docs.expo.dev/)
- [React Native 文件](https://reactnative.dev/)
- [Victory Charts](https://formidable.com/open-source/victory/docs/native)
- [Zustand 文件](https://docs.pmnd.rs/zustand)

### 設計靈感
- [Robinhood](https://robinhood.com/)
- [Webull](https://www.webull.com/)
- [Trading212](https://www.trading212.com/)
- [Dribbble - Stock App Designs](https://dribbble.com/search/stock-app)

---

## 💡 提示與技巧

### 效能優化

1. **使用 React.memo**
   ```typescript
   export const ETFCard = React.memo(ETFCardComponent);
   ```

2. **優化列表渲染**
   ```typescript
   <FlatList
     data={etfs}
     renderItem={renderItem}
     removeClippedSubviews={true}
     maxToRenderPerBatch={10}
     windowSize={10}
   />
   ```

3. **圖片優化**
   ```typescript
   <Image
     source={{ uri: imageUrl }}
     resizeMode="cover"
     cache="force-cache"
   />
   ```

### 除錯技巧

1. **Reactotron** - React Native 除錯工具
2. **Flipper** - Meta 官方除錯工具
3. **Console.log** - 適當使用 console.log

---

## 🎉 總結

您現在擁有：

✅ **完整的專案架構** - 從配置到部署
✅ **現代化的設計系統** - 極簡科技風格
✅ **強大的 API 整合** - 後端完美對接
✅ **核心功能實作** - ETF 分析與視覺化
✅ **詳細的開發文件** - 清晰的實作指南

**開始構建您的 ETF 分析工具吧！** 🚀

如有問題，請參考：
- [後端 API 文件](./TESTING_GUIDE.md)
- [Expo 整合指南](./EXPO_INTEGRATION.md)
- [架構設計文件](./ARCHITECTURE_DESIGN.md)
