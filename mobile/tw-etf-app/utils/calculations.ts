/**
 * 計算工具函數
 */

import type { ETFHolding } from '@/types';

/**
 * 計算個股對 ETF 的影響
 * impactOnETF = 持股權重 × 個股漲跌幅 / 100
 */
export function calculateStockImpact(
  weight: number,
  changePercent: number
): number {
  return (weight * changePercent) / 100;
}

/**
 * 計算 ETF 總影響 (所有個股影響加總)
 */
export function calculateTotalETFImpact(holdings: ETFHolding[]): number {
  return holdings.reduce((total, holding) => {
    if (holding.changePercent && holding.weight) {
      return total + calculateStockImpact(holding.weight, holding.changePercent);
    }
    return total;
  }, 0);
}

/**
 * 取得 Top N 持股
 */
export function getTopHoldings(holdings: ETFHolding[], n: number = 10): ETFHolding[] {
  return [...holdings]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, n);
}

/**
 * 依權重排序持股
 */
export function sortByWeight(holdings: ETFHolding[], desc: boolean = true): ETFHolding[] {
  return [...holdings].sort((a, b) => desc ? b.weight - a.weight : a.weight - b.weight);
}

/**
 * 依漲跌幅排序持股
 */
export function sortByChange(holdings: ETFHolding[], desc: boolean = true): ETFHolding[] {
  return [...holdings].sort((a, b) => {
    const aChange = a.changePercent || 0;
    const bChange = b.changePercent || 0;
    return desc ? bChange - aChange : aChange - bChange;
  });
}

/**
 * 依影響力排序持股
 */
export function sortByImpact(holdings: ETFHolding[], desc: boolean = true): ETFHolding[] {
  return [...holdings].sort((a, b) => {
    const aImpact = calculateStockImpact(a.weight, a.changePercent || 0);
    const bImpact = calculateStockImpact(b.weight, b.changePercent || 0);
    return desc ? bImpact - aImpact : aImpact - bImpact;
  });
}

/**
 * 產生圓餅圖資料
 */
export function generatePieChartData(
  holdings: ETFHolding[],
  maxSlices: number = 10,
  colors: string[]
): Array<{ label: string; value: number; color: string; percentage: number }> {
  const topHoldings = getTopHoldings(holdings, maxSlices);
  const others = holdings.slice(maxSlices);

  const chartData = topHoldings.map((holding, index) => ({
    label: holding.stockName,
    value: holding.weight,
    color: colors[index % colors.length],
    percentage: holding.weight,
  }));

  // 如果還有其他持股，加入 "其他" 項目
  if (others.length > 0) {
    const othersWeight = others.reduce((sum, h) => sum + h.weight, 0);
    chartData.push({
      label: '其他',
      value: othersWeight,
      color: colors[maxSlices % colors.length],
      percentage: othersWeight,
    });
  }

  return chartData;
}

/**
 * 計算統計數據
 */
export function calculateHoldingsStats(holdings: ETFHolding[]): {
  totalWeight: number;
  avgWeight: number;
  maxWeight: number;
  minWeight: number;
  posit iveCount: number;
  negativeCount: number;
  avgChange: number;
} {
  const weights = holdings.map((h) => h.weight);
  const changes = holdings.map((h) => h.changePercent || 0);

  return {
    totalWeight: weights.reduce((sum, w) => sum + w, 0),
    avgWeight: weights.reduce((sum, w) => sum + w, 0) / weights.length,
    maxWeight: Math.max(...weights),
    minWeight: Math.min(...weights),
    positiveCount: changes.filter((c) => c > 0).length,
    negativeCount: changes.filter((c) => c < 0).length,
    avgChange: changes.reduce((sum, c) => sum + c, 0) / changes.length,
  };
}
