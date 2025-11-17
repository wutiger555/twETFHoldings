/**
 * 格式化工具函數
 */

/**
 * 格式化價格
 */
export function formatPrice(price: number | undefined, decimals: number = 2): string {
  if (price === undefined) return '--';
  return price.toFixed(decimals);
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number | undefined, decimals: number = 2): string {
  if (value === undefined) return '--';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * 格式化數量 (加上千分位)
 */
export function formatNumber(num: number | undefined): string {
  if (num === undefined) return '--';
  return num.toLocaleString('zh-TW');
}

/**
 * 格式化大數字 (K, M, B)
 */
export function formatLargeNumber(num: number | undefined): string {
  if (num === undefined) return '--';

  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(2)}B`;
  }
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`;
  }
  return num.toFixed(0);
}

/**
 * 格式化市值
 */
export function formatMarketCap(value: number | undefined): string {
  if (value === undefined) return '--';
  return `${formatLargeNumber(value)} 元`;
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}/${month}/${day}`;
}

/**
 * 格式化日期時間
 */
export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const dateStr = formatDate(d);
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  return `${dateStr} ${hour}:${minute}`;
}

/**
 * 格式化相對時間 (如: 5分鐘前, 3小時前)
 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diffInSeconds < 60) return '剛剛';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} 分鐘前`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} 小時前`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} 天前`;
  return formatDate(d);
}

/**
 * 取得漲跌顏色
 */
export function getChangeColor(value: number | undefined, theme: any): string {
  if (value === undefined || value === 0) return theme.colors.textSecondary;
  return value > 0 ? theme.colors.success : theme.colors.danger;
}

/**
 * 取得漲跌符號
 */
export function getChangeSymbol(value: number | undefined): string {
  if (value === undefined || value === 0) return '';
  return value > 0 ? '▲' : '▼';
}
