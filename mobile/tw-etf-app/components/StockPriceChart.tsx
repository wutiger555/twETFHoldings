/**
 * 股價圖表組件 - 使用 react-native-wagmi-charts
 * 專業級的K線圖和折線圖顯示
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, Dimensions, TouchableOpacity } from 'react-native';
import { LineChart, CandlestickChart } from 'react-native-wagmi-charts';
import * as Haptics from 'expo-haptics';
import { theme } from '@/constants/theme';
import { formatPrice, formatDate, formatPercent } from '@/utils/format';
import type { StockHistory } from '@/types';

const SCREEN_WIDTH = Dimensions.get('window').width;

interface StockPriceChartProps {
  data: StockHistory[];
  stockCode: string;
  stockName: string;
  currentPrice?: number;
  changePercent?: number;
}

type ChartType = 'line' | 'candle';
type TimeRange = '1D' | '5D' | '1M' | '3M' | '6M' | '1Y';

export function StockPriceChart({
  data,
  stockCode,
  stockName,
  currentPrice,
  changePercent,
}: StockPriceChartProps) {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [timeRange, setTimeRange] = useState<TimeRange>('1M');

  // 轉換資料格式給 wagmi-charts
  const lineChartData = data.map((item) => ({
    timestamp: new Date(item.date).getTime(),
    value: item.close,
  }));

  const candleChartData = data.map((item) => ({
    timestamp: new Date(item.date).getTime(),
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
  }));

  // 計算價格範圍
  const prices = data.map((d) => d.close);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;

  // 漲跌顏色
  const trendColor = (changePercent || 0) >= 0
    ? theme.colors.success
    : theme.colors.danger;

  return (
    <View style={styles.container}>
      {/* Header - 股票資訊 */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.stockCode}>{stockCode}</Text>
          <Text style={styles.stockName}>{stockName}</Text>
        </View>
        <View style={styles.headerRight}>
          {currentPrice && (
            <>
              <Text style={styles.price}>
                ${formatPrice(currentPrice)}
              </Text>
              {changePercent !== undefined && (
                <Text style={[styles.change, { color: trendColor }]}>
                  {formatPercent(changePercent)}
                </Text>
              )}
            </>
          )}
        </View>
      </View>

      {/* 圖表類型切換 */}
      <View style={styles.chartTypeSelector}>
        <TouchableOpacity
          style={[
            styles.chartTypeButton,
            chartType === 'line' && styles.chartTypeButtonActive,
          ]}
          onPress={() => {
            setChartType('line');
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          }}
        >
          <Text
            style={[
              styles.chartTypeText,
              chartType === 'line' && styles.chartTypeTextActive,
            ]}
          >
            折線圖
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.chartTypeButton,
            chartType === 'candle' && styles.chartTypeButtonActive,
          ]}
          onPress={() => {
            setChartType('candle');
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          }}
        >
          <Text
            style={[
              styles.chartTypeText,
              chartType === 'candle' && styles.chartTypeTextActive,
            ]}
          >
            K線圖
          </Text>
        </TouchableOpacity>
      </View>

      {/* 圖表區域 */}
      <View style={styles.chartContainer}>
        {chartType === 'line' ? (
          <LineChart.Provider data={lineChartData}>
            <LineChart height={300} width={SCREEN_WIDTH - 32}>
              {/* 背景網格 */}
              <LineChart.Path color={trendColor} width={2}>
                <LineChart.Gradient color={trendColor} />
              </LineChart.Path>

              {/* 十字準星 */}
              <LineChart.CursorCrosshair
                color={theme.colors.textSecondary}
                snapToPoint
              >
                <LineChart.Tooltip
                  textStyle={styles.tooltipText}
                  style={styles.tooltip}
                />
                <LineChart.PriceText
                  style={styles.priceText}
                  precision={2}
                />
                <LineChart.DatetimeText
                  style={styles.dateText}
                  format={({ value }) => {
                    const date = new Date(value);
                    return formatDate(date);
                  }}
                />
              </LineChart.CursorCrosshair>
            </LineChart>
          </LineChart.Provider>
        ) : (
          <CandlestickChart.Provider data={candleChartData}>
            <CandlestickChart height={300} width={SCREEN_WIDTH - 32}>
              {/* K線 */}
              <CandlestickChart.Candles
                positiveColor={theme.colors.success}
                negativeColor={theme.colors.danger}
              />

              {/* 十字準星 */}
              <CandlestickChart.Crosshair
                color={theme.colors.textSecondary}
              >
                <CandlestickChart.Tooltip
                  textStyle={styles.tooltipText}
                  style={styles.tooltip}
                />
              </CandlestickChart.Crosshair>
            </CandlestickChart>
          </CandlestickChart.Provider>
        )}
      </View>

      {/* 時間範圍選擇 */}
      <View style={styles.timeRangeSelector}>
        {(['1D', '5D', '1M', '3M', '6M', '1Y'] as TimeRange[]).map((range) => (
          <TouchableOpacity
            key={range}
            style={[
              styles.timeRangeButton,
              timeRange === range && styles.timeRangeButtonActive,
            ]}
            onPress={() => {
              setTimeRange(range);
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              // TODO: 重新載入對應時間範圍的資料
            }}
          >
            <Text
              style={[
                styles.timeRangeText,
                timeRange === range && styles.timeRangeTextActive,
              ]}
            >
              {range}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 統計資訊 */}
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>最高</Text>
          <Text style={styles.statValue}>{formatPrice(maxPrice)}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>最低</Text>
          <Text style={styles.statValue}>{formatPrice(minPrice)}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>振幅</Text>
          <Text style={styles.statValue}>
            {((priceRange / minPrice) * 100).toFixed(2)}%
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>資料點</Text>
          <Text style={styles.statValue}>{data.length}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.base,
    marginVertical: theme.spacing.base,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.lg,
  },
  headerLeft: {
    flex: 1,
  },
  stockCode: {
    fontSize: theme.typography.sizes['2xl'],
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
  },
  stockName: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  headerRight: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: theme.typography.sizes['2xl'],
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.text,
  },
  change: {
    fontSize: theme.typography.sizes.md,
    fontWeight: theme.typography.weights.semibold,
    marginTop: 4,
  },
  chartTypeSelector: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.base,
    padding: 4,
    marginBottom: theme.spacing.md,
  },
  chartTypeButton: {
    flex: 1,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.base,
    borderRadius: theme.borderRadius.sm,
    alignItems: 'center',
  },
  chartTypeButtonActive: {
    backgroundColor: theme.colors.primary,
  },
  chartTypeText: {
    fontSize: theme.typography.sizes.sm,
    fontWeight: theme.typography.weights.semibold,
    color: theme.colors.textSecondary,
  },
  chartTypeTextActive: {
    color: theme.colors.text,
  },
  chartContainer: {
    marginVertical: theme.spacing.md,
    alignItems: 'center',
  },
  tooltip: {
    backgroundColor: theme.colors.backgroundTertiary,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.sm,
  },
  tooltipText: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.text,
  },
  priceText: {
    fontSize: theme.typography.sizes.lg,
    fontWeight: theme.typography.weights.bold,
    color: theme.colors.primary,
  },
  dateText: {
    fontSize: theme.typography.sizes.xs,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  timeRangeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: theme.spacing.md,
  },
  timeRangeButton: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
  },
  timeRangeButtonActive: {
    backgroundColor: theme.colors.backgroundTertiary,
  },
  timeRangeText: {
    fontSize: theme.typography.sizes.sm,
    color: theme.colors.textSecondary,
  },
  timeRangeTextActive: {
    color: theme.colors.primary,
    fontWeight: theme.typography.weights.semibold,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: theme.typography.sizes.xs,
    color: theme.colors.textTertiary,
    marginBottom: 4,
  },
  statValue: {
    fontSize: theme.typography.sizes.sm,
    fontWeight: theme.typography.weights.semibold,
    color: theme.colors.text,
  },
});
