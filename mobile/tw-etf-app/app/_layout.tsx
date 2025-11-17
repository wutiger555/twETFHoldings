/**
 * Root Layout - App 根佈局
 */

import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useETFStore } from '@/stores/useETFStore';

export default function RootLayout() {
  const loadPreferences = useETFStore((state) => state.loadPreferences);
  const loadFavorites = useETFStore((state) => state.loadFavorites);
  const loadRecentlyViewed = useETFStore((state) => state.loadRecentlyViewed);

  useEffect(() => {
    // 載入使用者資料
    loadPreferences();
    loadFavorites();
    loadRecentlyViewed();
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <StatusBar style="light" />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: '#0A0A0A' },
            animation: 'slide_from_right',
          }}
        >
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen
            name="etf/[code]"
            options={{
              presentation: 'card',
              animation: 'slide_from_bottom',
            }}
          />
        </Stack>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
