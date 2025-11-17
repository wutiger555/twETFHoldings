/**
 * API Service Layer
 * 與後端 Flask API 通訊
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {
  ETF,
  ETFDetail,
  ETFHolding,
  Stock,
  StockHistory,
  APIResponse,
  PaginatedResponse,
  MarketStats,
  PopularStock,
  AppError,
} from '@/types';

// API 配置
const API_CONFIG = {
  // 開發環境
  DEV_URL: 'http://localhost:5001/api/v1',
  // 生產環境 (請替換為您的 Railway/Render URL)
  PROD_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5001/api/v1',
  TIMEOUT: 10000,
};

class APIService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    // 使用環境變數或預設值
    this.baseURL = __DEV__ ? API_CONFIG.DEV_URL : API_CONFIG.PROD_URL;

    // 建立 Axios 實例
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 請求攔截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );

    // 回應攔截器
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] ✅ ${response.config.url}`);
        return response;
      },
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * 錯誤處理
   */
  private handleError(error: AxiosError): AppError {
    if (error.response) {
      // 伺服器回應錯誤
      return {
        code: `HTTP_${error.response.status}`,
        message: (error.response.data as any)?.message || '伺服器錯誤',
        details: error.response.data,
      };
    } else if (error.request) {
      // 請求發送但無回應
      return {
        code: 'NETWORK_ERROR',
        message: '網路連線失敗，請檢查您的網路設定',
        details: error.message,
      };
    } else {
      // 其他錯誤
      return {
        code: 'UNKNOWN_ERROR',
        message: error.message || '發生未知錯誤',
        details: error,
      };
    }
  }

  /**
   * 快取管理
   */
  private async getCachedData<T>(key: string): Promise<T | null> {
    try {
      const cached = await AsyncStorage.getItem(key);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        // 快取 5 分鐘
        if (Date.now() - timestamp < 5 * 60 * 1000) {
          console.log(`[Cache] Hit: ${key}`);
          return data;
        }
      }
    } catch (error) {
      console.warn(`[Cache] Error reading: ${key}`, error);
    }
    return null;
  }

  private async setCachedData<T>(key: string, data: T): Promise<void> {
    try {
      await AsyncStorage.setItem(
        key,
        JSON.stringify({ data, timestamp: Date.now() })
      );
      console.log(`[Cache] Set: ${key}`);
    } catch (error) {
      console.warn(`[Cache] Error writing: ${key}`, error);
    }
  }

  // ============================================================
  // ETF API
  // ============================================================

  /**
   * 取得 ETF 列表
   */
  async getETFList(params?: {
    page?: number;
    limit?: number;
    issuer?: string;
    sort?: string;
  }): Promise<PaginatedResponse<ETF>> {
    const cacheKey = `etf_list_${JSON.stringify(params)}`;
    const cached = await this.getCachedData<PaginatedResponse<ETF>>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<PaginatedResponse<ETF>>('/etf/etfs', { params });
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  /**
   * 取得 ETF 詳情
   */
  async getETFDetail(code: string): Promise<ETFDetail> {
    const cacheKey = `etf_detail_${code}`;
    const cached = await this.getCachedData<ETFDetail>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<ETFDetail>(`/etf/etf/${code}`);
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  /**
   * 取得 ETF 持股 (含即時價格)
   */
  async getETFHoldings(code: string, enrichPrices: boolean = true): Promise<ETFHolding[]> {
    const cacheKey = `etf_holdings_${code}_${enrichPrices}`;
    const cached = await this.getCachedData<ETFHolding[]>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<ETFHolding[]>(
      `/etf/etf/${code}/holdings`,
      { params: { enrich_prices: enrichPrices } }
    );
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  // ============================================================
  // Stock API
  // ============================================================

  /**
   * 取得個股價格
   */
  async getStockPrice(code: string): Promise<Stock> {
    const cacheKey = `stock_price_${code}`;
    const cached = await this.getCachedData<Stock>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<Stock>(`/stock/${code}`);
    // 個股價格快取時間較短 (1 分鐘)
    await AsyncStorage.setItem(
      cacheKey,
      JSON.stringify({ data: response.data, timestamp: Date.now() })
    );
    return response.data;
  }

  /**
   * 取得個股歷史資料
   */
  async getStockHistory(code: string, period: string = '30d'): Promise<StockHistory[]> {
    const cacheKey = `stock_history_${code}_${period}`;
    const cached = await this.getCachedData<StockHistory[]>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<StockHistory[]>(
      `/stock/${code}/history`,
      { params: { period } }
    );
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  /**
   * 批次取得多個股價
   */
  async getBatchStockPrices(codes: string[]): Promise<Record<string, Stock>> {
    const response = await this.client.post<Record<string, Stock>>(
      '/stock/batch',
      { codes }
    );
    return response.data;
  }

  // ============================================================
  // Search API
  // ============================================================

  /**
   * 搜尋 ETF 和個股
   */
  async search(query: string, type?: 'ETF' | 'STOCK'): Promise<{
    etfs: ETF[];
    stocks: Stock[];
  }> {
    const response = await this.client.get('/search', {
      params: { q: query, type },
    });
    return response.data;
  }

  // ============================================================
  // Stats API
  // ============================================================

  /**
   * 取得市場統計
   */
  async getMarketStats(): Promise<MarketStats> {
    const cacheKey = 'market_stats';
    const cached = await this.getCachedData<MarketStats>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<MarketStats>('/stats/market');
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  /**
   * 取得熱門股票
   */
  async getPopularStocks(limit: number = 20): Promise<PopularStock[]> {
    const cacheKey = `popular_stocks_${limit}`;
    const cached = await this.getCachedData<PopularStock[]>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<PopularStock[]>('/stats/popular', {
      params: { limit },
    });
    await this.setCachedData(cacheKey, response.data);
    return response.data;
  }

  // ============================================================
  // Health Check
  // ============================================================

  /**
   * 健康檢查
   */
  async healthCheck(): Promise<{ status: string; services: Record<string, string> }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ============================================================
  // Utility Methods
  // ============================================================

  /**
   * 清除所有快取
   */
  async clearCache(): Promise<void> {
    try {
      await AsyncStorage.clear();
      console.log('[Cache] Cleared all cache');
    } catch (error) {
      console.warn('[Cache] Error clearing cache', error);
    }
  }

  /**
   * 設定 API Base URL
   */
  setBaseURL(url: string): void {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
    console.log(`[API] Base URL set to: ${url}`);
  }

  /**
   * 取得當前 Base URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }
}

// 匯出單例實例
export const api = new APIService();

// 匯出類別供測試使用
export default APIService;
