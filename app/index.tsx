import { Link } from 'expo-router';
import { Text, View } from 'react-native';

export default function Home() {
  return (
    <View style={{ flex: 1, padding: 20, paddingTop: 60 }}>
      <Text style={{ fontSize: 28, fontWeight: 'bold' }}>🍡 macaron</Text>
      <Text style={{ marginTop: 8, color: '#666' }}>Phase 0 PoC</Text>

      <Link
        href="/poc-health"
        style={{
          marginTop: 32,
          padding: 16,
          backgroundColor: '#fff5fa',
          borderRadius: 8,
          fontSize: 16,
        }}
      >
        → HealthKit + 적립 PoC 열기
      </Link>
    </View>
  );
}
