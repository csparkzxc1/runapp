import { useEffect, useState } from 'react';
import { Button, ScrollView, Text, View } from 'react-native';
import { useUserStore } from '@/stores/userStore';
import { supabase } from '@/lib/supabase';
import {
  getTodayDistance,
  getTodayFlightsClimbed,
  getTodayStepCount,
  initHealthKit,
} from '@/lib/health';
import { calculateMilestoneRewards } from '@/lib/macaron';

const todayDate = () => new Date().toISOString().split('T')[0];

export default function PoCHealth() {
  const userId = useUserStore((s) => s.userId);
  const setUserId = useUserStore((s) => s.setUserId);

  const [steps, setSteps] = useState(0);
  const [flights, setFlights] = useState(0);
  const [distance, setDistance] = useState(0);
  const [macaronBalance, setMacaronBalance] = useState(0);
  const [todayEarned, setTodayEarned] = useState(0);
  const [milestones, setMilestones] = useState<string[]>([]);
  const [status, setStatus] = useState<string>('idle');
  const [error, setError] = useState<string | null>(null);

  // 익명 로그인 (1회)
  useEffect(() => {
    if (userId) return;
    supabase.auth.getSession().then(async ({ data }) => {
      if (data.session?.user) {
        setUserId(data.session.user.id);
        return;
      }
      const { data: signIn, error: signInErr } =
        await supabase.auth.signInAnonymously();
      if (signInErr) {
        setError(`auth: ${signInErr.message}`);
        return;
      }
      if (signIn.user) setUserId(signIn.user.id);
    });
  }, [userId, setUserId]);

  const sync = async () => {
    if (!userId) {
      setError('userId 없음 — 로그인 대기 중');
      return;
    }
    setError(null);
    setStatus('reading healthkit…');

    try {
      await initHealthKit();
      const [s, f, d] = await Promise.all([
        getTodayStepCount(),
        getTodayFlightsClimbed(),
        getTodayDistance(),
      ]);
      setSteps(s);
      setFlights(f);
      setDistance(d);

      setStatus('syncing supabase…');
      const today = todayDate();

      const { data: existing, error: readErr } = await supabase
        .from('daily_activity')
        .select('*')
        .eq('user_id', userId)
        .eq('activity_date', today)
        .maybeSingle();
      if (readErr) throw readErr;

      const grantedSoFar: string[] = existing?.milestones_granted ?? [];
      const { earned, newMilestones } = calculateMilestoneRewards(
        { steps: s, flights: f },
        grantedSoFar
      );

      const totalEarned = (existing?.macaron_earned ?? 0) + earned;
      const totalMilestones = [...grantedSoFar, ...newMilestones];

      const { error: upErr } = await supabase.from('daily_activity').upsert(
        {
          user_id: userId,
          activity_date: today,
          steps: s,
          flights_climbed: f,
          distance_meters: d,
          macaron_earned: totalEarned,
          milestones_granted: totalMilestones,
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'user_id,activity_date' }
      );
      if (upErr) throw upErr;

      if (earned > 0) {
        const { data: prof, error: profErr } = await supabase
          .from('profiles')
          .select('macaron_balance, lifetime_steps')
          .eq('id', userId)
          .single();
        if (profErr) throw profErr;

        const stepDelta = Math.max(0, s - (existing?.steps ?? 0));

        const { error: updErr } = await supabase
          .from('profiles')
          .update({
            macaron_balance: (prof?.macaron_balance ?? 0) + earned,
            lifetime_steps: (prof?.lifetime_steps ?? 0) + stepDelta,
            updated_at: new Date().toISOString(),
          })
          .eq('id', userId);
        if (updErr) throw updErr;
      }

      const { data: prof2 } = await supabase
        .from('profiles')
        .select('macaron_balance')
        .eq('id', userId)
        .single();

      setTodayEarned(totalEarned);
      setMilestones(totalMilestones);
      setMacaronBalance(prof2?.macaron_balance ?? 0);
      setStatus(earned > 0 ? `+${earned} 마카롱!` : 'sync 완료');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setStatus('error');
    }
  };

  return (
    <ScrollView style={{ flex: 1, padding: 20, paddingTop: 40 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold' }}>마카롱 PoC</Text>
      <Text style={{ marginTop: 8, color: '#666' }}>
        User: {userId?.substring(0, 8) ?? '...'}
      </Text>
      <Text style={{ marginTop: 4, color: '#666' }}>Status: {status}</Text>
      {error && (
        <Text style={{ marginTop: 4, color: '#c00' }}>Error: {error}</Text>
      )}

      <View
        style={{
          marginTop: 20,
          padding: 16,
          backgroundColor: '#fff5fa',
          borderRadius: 8,
        }}
      >
        <Text style={{ fontSize: 28, fontWeight: 'bold' }}>
          🍡 {macaronBalance}
        </Text>
        <Text>오늘 적립: +{todayEarned}</Text>
      </View>

      <View style={{ marginTop: 20 }}>
        <Text>걸음: {steps.toLocaleString()}</Text>
        <Text>계단: {flights}층</Text>
        <Text>거리: {(distance / 1000).toFixed(2)}km</Text>
      </View>

      <View style={{ marginTop: 20 }}>
        <Text style={{ fontWeight: 'bold' }}>도달한 마일스톤:</Text>
        {milestones.length === 0 ? (
          <Text style={{ color: '#999' }}>(아직 없음)</Text>
        ) : (
          milestones.map((m) => <Text key={m}>✓ {m}</Text>)
        )}
      </View>

      <View style={{ marginTop: 20 }}>
        <Button title="새로고침 + 적립" onPress={sync} />
      </View>
    </ScrollView>
  );
}
