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
import {
  DAILY_AD_LIMIT,
  checkAttendance,
  grantAdReward,
} from '@/lib/rewards';
import { detectTierUp } from '@/lib/tier';
import { DAYPART_LABEL, SEASON_LABEL, getYardState } from '@/lib/season';
import type { TierLevel } from '@/types';

const todayDate = () => new Date().toISOString().split('T')[0];

const TIER_LABEL: Record<TierLevel, string> = {
  tent: '천막',
  cabin: '오두막',
  yard_house: '마당집',
  villa: '빌라',
  apartment: '아파트',
  mansion: '저택',
};

export default function PoCHealth() {
  const userId = useUserStore((s) => s.userId);
  const setUserId = useUserStore((s) => s.setUserId);

  const [steps, setSteps] = useState(0);
  const [flights, setFlights] = useState(0);
  const [distance, setDistance] = useState(0);
  const [macaronBalance, setMacaronBalance] = useState(0);
  const [todayEarned, setTodayEarned] = useState(0);
  const [milestones, setMilestones] = useState<string[]>([]);
  const [attendanceClaimed, setAttendanceClaimed] = useState(false);
  const [adsWatched, setAdsWatched] = useState(0);
  const [currentTier, setCurrentTier] = useState<TierLevel>('tent');
  const [lifetimeSteps, setLifetimeSteps] = useState(0);
  const [status, setStatus] = useState<string>('idle');
  const [error, setError] = useState<string | null>(null);

  const yard = getYardState();

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

      // 1. 마일스톤
      const grantedSoFar: string[] = existing?.milestones_granted ?? [];
      const { earned: milestoneEarned, newMilestones } =
        calculateMilestoneRewards({ steps: s, flights: f }, grantedSoFar);

      // 2. 출석 (오늘 첫 sync면 자동 지급)
      const attendanceState = existing?.attendance_claimed ?? false;
      const attendance = checkAttendance(attendanceState);

      const earnedThisSync = milestoneEarned + attendance.earned;
      const totalEarned = (existing?.macaron_earned ?? 0) + earnedThisSync;
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
          attendance_claimed: true,
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'user_id,activity_date' }
      );
      if (upErr) throw upErr;

      let newBalance = 0;
      let newTier: TierLevel = currentTier;
      let newLifetime = lifetimeSteps;

      if (earnedThisSync > 0) {
        const { data: prof, error: profErr } = await supabase
          .from('profiles')
          .select('macaron_balance, lifetime_steps, current_tier')
          .eq('id', userId)
          .single();
        if (profErr) throw profErr;

        const stepDelta = Math.max(0, s - (existing?.steps ?? 0));
        newLifetime = (prof?.lifetime_steps ?? 0) + stepDelta;
        newBalance = (prof?.macaron_balance ?? 0) + earnedThisSync;

        const tierCheck = detectTierUp(
          (prof?.current_tier ?? 'tent') as TierLevel,
          newLifetime
        );
        newTier = tierCheck.newTier;

        const { error: updErr } = await supabase
          .from('profiles')
          .update({
            macaron_balance: newBalance,
            lifetime_steps: newLifetime,
            // current_tier는 DB trigger가 lifetime_steps 변경 시 자동 동기화
            updated_at: new Date().toISOString(),
          })
          .eq('id', userId);
        if (updErr) throw updErr;

        if (tierCheck.upgraded) {
          setStatus(
            `+${earnedThisSync} 마카롱! 🎉 등급업: ${TIER_LABEL[newTier]}`
          );
        } else {
          setStatus(`+${earnedThisSync} 마카롱!`);
        }
      } else {
        setStatus('sync 완료 (적립 없음)');
      }

      // 최종 상태 read-back (DB trigger 결과 포함)
      const { data: prof2 } = await supabase
        .from('profiles')
        .select('macaron_balance, lifetime_steps, current_tier')
        .eq('id', userId)
        .single();

      setTodayEarned(totalEarned);
      setMilestones(totalMilestones);
      setAttendanceClaimed(true);
      setAdsWatched(existing?.ads_watched ?? 0);
      setMacaronBalance(prof2?.macaron_balance ?? newBalance);
      setLifetimeSteps(prof2?.lifetime_steps ?? newLifetime);
      setCurrentTier((prof2?.current_tier ?? newTier) as TierLevel);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setStatus('error');
    }
  };

  // 광고 시청 시뮬레이션 (Phase 1에서 실제 AdMob 연동)
  const watchAd = async () => {
    if (!userId) return;
    setError(null);
    setStatus('mock ad…');

    try {
      const today = todayDate();
      const { data: existing, error: readErr } = await supabase
        .from('daily_activity')
        .select('*')
        .eq('user_id', userId)
        .eq('activity_date', today)
        .maybeSingle();
      if (readErr) throw readErr;

      const currentAds = existing?.ads_watched ?? 0;
      const result = grantAdReward(currentAds);

      if (result.earned === 0) {
        setStatus(`광고 한도(${DAILY_AD_LIMIT}회) 도달`);
        return;
      }

      const newEarned = (existing?.macaron_earned ?? 0) + result.earned;

      const { error: upErr } = await supabase.from('daily_activity').upsert(
        {
          user_id: userId,
          activity_date: today,
          ads_watched: result.newAdsWatched,
          macaron_earned: newEarned,
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'user_id,activity_date' }
      );
      if (upErr) throw upErr;

      const { data: prof } = await supabase
        .from('profiles')
        .select('macaron_balance')
        .eq('id', userId)
        .single();

      const { error: updErr } = await supabase
        .from('profiles')
        .update({
          macaron_balance: (prof?.macaron_balance ?? 0) + result.earned,
          updated_at: new Date().toISOString(),
        })
        .eq('id', userId);
      if (updErr) throw updErr;

      setAdsWatched(result.newAdsWatched);
      setTodayEarned(newEarned);
      setMacaronBalance((prof?.macaron_balance ?? 0) + result.earned);
      setStatus(`광고 +${result.earned} (${result.newAdsWatched}/${DAILY_AD_LIMIT})`);
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

      <View
        style={{
          marginTop: 20,
          padding: 16,
          backgroundColor: '#f0f8ff',
          borderRadius: 8,
        }}
      >
        <Text style={{ fontWeight: 'bold' }}>🏠 마당</Text>
        <Text>
          {SEASON_LABEL[yard.season]} · {DAYPART_LABEL[yard.daypart]}
        </Text>
        <Text style={{ marginTop: 8 }}>
          등급: {TIER_LABEL[currentTier]} ({lifetimeSteps.toLocaleString()}보)
        </Text>
      </View>

      <View style={{ marginTop: 20 }}>
        <Text>걸음: {steps.toLocaleString()}</Text>
        <Text>계단: {flights}층</Text>
        <Text>거리: {(distance / 1000).toFixed(2)}km</Text>
      </View>

      <View style={{ marginTop: 20 }}>
        <Text style={{ fontWeight: 'bold' }}>오늘 보상 현황:</Text>
        <Text>출석: {attendanceClaimed ? '✓ 받음' : '아직'}</Text>
        <Text>
          광고: {adsWatched} / {DAILY_AD_LIMIT}
        </Text>
        <Text style={{ marginTop: 8, fontWeight: 'bold' }}>마일스톤:</Text>
        {milestones.length === 0 ? (
          <Text style={{ color: '#999' }}>(아직 없음)</Text>
        ) : (
          milestones.map((m) => <Text key={m}>✓ {m}</Text>)
        )}
      </View>

      <View style={{ marginTop: 20, gap: 8 }}>
        <Button title="새로고침 + 적립" onPress={sync} />
        <View style={{ height: 8 }} />
        <Button title="🎬 광고 시청 (mock)" onPress={watchAd} />
      </View>
    </ScrollView>
  );
}
