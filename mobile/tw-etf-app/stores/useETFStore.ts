/**
 * Zustand Store - ETF 狀態管理
 */

import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {
  ETF,
  ETFDetail,
  LoadingState,
  FilterOptions,
  UserPreferences,
} from '@/types';
import { api } from '@/services/api';

interface ETFStore {
  // ============================================================
  // State
  // ============================================================

  // ETF 列表
  etfs: ETF[];
  etfsLoading: LoadingState;
  etfsError: string | null;

  // ETF 詳情 (快取)
  etfDetails: Record<string, ETFDetail>;
  currentETF: ETFDetail | null;
  currentETFLoading: LoadingState;

  // 篩選和排序
  filters: FilterOptions;

  // 使用者偏好
  favorites: string[];
  recentlyViewed: string[];
  preferences: UserPreferences;

  // ============================================================
  // Actions - ETF List
  // ============================================================

  /**
   * 載入 ETF 列表
   */
  loadETFs: (refresh?: boolean) => Promise<void>;

  /**
   * 設定篩選選項
   */
  setFilters: (filters: Partial<FilterOptions>) => void;

  /**
   * 重置篩選
   */
  resetFilters: () => void;

  // ============================================================
  // Actions - ETF Detail
  // ============================================================

  /**
   * 載入 ETF 詳情
   */
  loadETFDetail: (code: string) => Promise<void>;

  /**
   * 清除當前 ETF
   */
  clearCurrentETF: () => void;

  // ============================================================
  // Actions - Favorites
  // ============================================================

  /**
   * 切換收藏
   */
  toggleFavorite: (code: string) => Promise<void>;

  /**
   * 檢查是否收藏
   */
  isFavorite: (code: string) => boolean;

  /**
   * 載入收藏列表
   */
  loadFavorites: () => Promise<void>;

  // ============================================================
  // Actions - Recently Viewed
  // ============================================================

  /**
   * 添加到最近查看
   */
  addToRecentlyViewed: (code: string) => Promise<void>;

  /**
   * 載入最近查看
   */
  loadRecentlyViewed: () => Promise<void>;

  // ============================================================
  // Actions - Preferences
  // ============================================================

  /**
   * 更新偏好設定
   */
  updatePreferences: (prefs: Partial<UserPreferences>) => Promise<void>;

  /**
   * 載入偏好設定
   */
  loadPreferences: () => Promise<void>;

  // ============================================================
  // Actions - Utility
  // ============================================================

  /**
   * 清除所有快取
   */
  clearCache: () => Promise<void>;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'dark',
  favorites: [],
  recentlyViewed: [],
  notifications: true,
  language: 'zh-TW',
};

export const useETFStore = create<ETFStore>((set, get) => ({
  // Initial State
  etfs: [],
  etfsLoading: 'idle',
  etfsError: null,

  etfDetails: {},
  currentETF: null,
  currentETFLoading: 'idle',

  filters: {
    issuer: 'all',
    sort: 'name',
    direction: 'asc',
    searchQuery: '',
  },

  favorites: [],
  recentlyViewed: [],
  preferences: DEFAULT_PREFERENCES,

  // ============================================================
  // Implementations
  // ============================================================

  loadETFs: async (refresh = false) => {
    const { etfs, etfsLoading } = get();

    // 避免重複載入
    if (!refresh && etfs.length > 0) return;
    if (etfsLoading === 'loading') return;

    set({ etfsLoading: 'loading', etfsError: null });

    try {
      const response = await api.getETFList({
        page: 1,
        limit: 100,
        issuer: get().filters.issuer === 'all' ? undefined : get().filters.issuer,
      });

      set({
        etfs: response.items,
        etfsLoading: 'success',
        etfsError: null,
      });
    } catch (error: any) {
      set({
        etfsLoading: 'error',
        etfsError: error.message || '載入 ETF 列表失敗',
      });
    }
  },

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));

    // 重新載入列表
    get().loadETFs(true);
  },

  resetFilters: () => {
    set({
      filters: {
        issuer: 'all',
        sort: 'name',
        direction: 'asc',
        searchQuery: '',
      },
    });
    get().loadETFs(true);
  },

  loadETFDetail: async (code: string) => {
    const { etfDetails } = get();

    // 檢查快取
    if (etfDetails[code]) {
      set({ currentETF: etfDetails[code], currentETFLoading: 'success' });
      return;
    }

    set({ currentETFLoading: 'loading' });

    try {
      const detail = await api.getETFDetail(code);

      set((state) => ({
        etfDetails: { ...state.etfDetails, [code]: detail },
        currentETF: detail,
        currentETFLoading: 'success',
      }));

      // 添加到最近查看
      await get().addToRecentlyViewed(code);
    } catch (error: any) {
      set({ currentETFLoading: 'error' });
      throw error;
    }
  },

  clearCurrentETF: () => {
    set({ currentETF: null, currentETFLoading: 'idle' });
  },

  toggleFavorite: async (code: string) => {
    const { favorites } = get();
    const newFavorites = favorites.includes(code)
      ? favorites.filter((c) => c !== code)
      : [code, ...favorites];

    set({ favorites: newFavorites });

    // 持久化
    try {
      await AsyncStorage.setItem('favorites', JSON.stringify(newFavorites));
    } catch (error) {
      console.warn('Failed to save favorites', error);
    }
  },

  isFavorite: (code: string) => {
    return get().favorites.includes(code);
  },

  loadFavorites: async () => {
    try {
      const stored = await AsyncStorage.getItem('favorites');
      if (stored) {
        set({ favorites: JSON.parse(stored) });
      }
    } catch (error) {
      console.warn('Failed to load favorites', error);
    }
  },

  addToRecentlyViewed: async (code: string) => {
    const { recentlyViewed } = get();
    const newRecent = [
      code,
      ...recentlyViewed.filter((c) => c !== code),
    ].slice(0, 20); // 最多保存 20 筆

    set({ recentlyViewed: newRecent });

    try {
      await AsyncStorage.setItem('recentlyViewed', JSON.stringify(newRecent));
    } catch (error) {
      console.warn('Failed to save recently viewed', error);
    }
  },

  loadRecentlyViewed: async () => {
    try {
      const stored = await AsyncStorage.getItem('recentlyViewed');
      if (stored) {
        set({ recentlyViewed: JSON.parse(stored) });
      }
    } catch (error) {
      console.warn('Failed to load recently viewed', error);
    }
  },

  updatePreferences: async (prefs: Partial<UserPreferences>) => {
    const newPrefs = { ...get().preferences, ...prefs };
    set({ preferences: newPrefs });

    try {
      await AsyncStorage.setItem('preferences', JSON.stringify(newPrefs));
    } catch (error) {
      console.warn('Failed to save preferences', error);
    }
  },

  loadPreferences: async () => {
    try {
      const stored = await AsyncStorage.getItem('preferences');
      if (stored) {
        set({ preferences: JSON.parse(stored) });
      }
    } catch (error) {
      console.warn('Failed to load preferences', error);
    }
  },

  clearCache: async () => {
    set({
      etfs: [],
      etfDetails: {},
      currentETF: null,
      etfsLoading: 'idle',
      currentETFLoading: 'idle',
    });

    await api.clearCache();
  },
}));
