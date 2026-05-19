import type { ExpoConfig } from 'expo/config';

const config: ExpoConfig = {
  name: 'macaron',
  slug: 'macaron',
  version: '0.0.1',
  scheme: 'macaron',
  orientation: 'portrait',
  userInterfaceStyle: 'automatic',
  newArchEnabled: true,
  ios: {
    bundleIdentifier: 'com.csparkzxc1.macaron',
    supportsTablet: false,
    infoPlist: {
      NSHealthShareUsageDescription:
        '걸음수와 계단 데이터를 읽어서 마카롱으로 환산합니다.',
      NSHealthUpdateUsageDescription: '운동 기록을 위해 사용합니다.',
    },
    entitlements: {
      'com.apple.developer.healthkit': true,
      'com.apple.developer.healthkit.access': [],
    },
  },
  android: {
    package: 'com.csparkzxc1.macaron',
  },
  plugins: [
    'expo-router',
    [
      'expo-build-properties',
      {
        ios: {
          deploymentTarget: '15.1',
        },
      },
    ],
  ],
  experiments: {
    typedRoutes: true,
  },
};

export default config;
