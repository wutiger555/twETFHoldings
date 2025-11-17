# React Native Mobile App (Expo)

此目錄將用於存放 React Native iOS/Android App 的原始碼。

## 快速開始

完整的 React Native App 開發教學請參考：

**[📱 Expo 整合指南](../docs/EXPO_INTEGRATION.md)**

## 建立 Expo 專案

```bash
# 1. 安裝 Expo CLI
npm install -g expo-cli

# 2. 建立專案（在 mobile/ 目錄）
cd mobile/
npx create-expo-app@latest tw-etf-app

# 3. 進入專案目錄
cd tw-etf-app

# 4. 啟動開發伺服器
npx expo start
```

## 預期專案結構

```
mobile/
└── tw-etf-app/               # Expo 專案根目錄
    ├── app/                  # 主要應用程式碼
    │   ├── (tabs)/          # Tab 導航頁面
    │   │   ├── index.tsx    # ETF 列表
    │   │   ├── search.tsx   # 搜尋頁面
    │   │   └── favorites.tsx # 自選清單
    │   └── etf/[code].tsx   # ETF 詳情頁
    ├── services/            # API 服務層
    │   └── api.ts           # API 客戶端
    ├── stores/              # Zustand 狀態管理
    │   └── useETFStore.ts   # ETF 狀態
    ├── types/               # TypeScript 型別
    │   └── index.ts
    ├── app.json
    ├── package.json
    └── tsconfig.json
```

## 連接後端 API

在建立 Expo 專案後，需要設定 API 端點：

```typescript
// services/api.ts
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  'http://localhost:5001/api/v1';  // 開發環境
  // 'https://your-api.railway.app/api/v1';  // 生產環境
```

## 下一步

1. 📖 閱讀 [Expo 整合指南](../docs/EXPO_INTEGRATION.md)
2. 🚀 參考 [快速開始](../docs/QUICK_START.md)
3. 🏗️ 查看 [架構設計](../docs/ARCHITECTURE_DESIGN.md)

## 需要幫助？

- Expo 官方文件：https://docs.expo.dev/
- React Native 官方文件：https://reactnative.dev/
- 專案完整教學：[EXPO_INTEGRATION.md](../docs/EXPO_INTEGRATION.md)
