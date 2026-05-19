import type { TierLevel } from '@/types';

// 등급 임계값 (누적 걸음 기준)
// 7천보/일 평균 가정. 솔로 개발자가 추후 밸런싱.
export const TIER_THRESHOLDS: ReadonlyArray<{
  tier: TierLevel;
  lifetimeSteps: number;
}> = [
  { tier: 'tent', lifetimeSteps: 0 },
  { tier: 'cabin', lifetimeSteps: 100_000 }, // ~14일
  { tier: 'yard_house', lifetimeSteps: 500_000 }, // ~70일
  { tier: 'villa', lifetimeSteps: 1_500_000 }, // ~7개월
  { tier: 'apartment', lifetimeSteps: 3_500_000 }, // ~16개월
  { tier: 'mansion', lifetimeSteps: 7_000_000 }, // ~3년
];

const TIER_RANK: Record<TierLevel, number> = {
  tent: 0,
  cabin: 1,
  yard_house: 2,
  villa: 3,
  apartment: 4,
  mansion: 5,
};

export function computeTier(lifetimeSteps: number): TierLevel {
  const safe = Math.max(0, lifetimeSteps);
  let result: TierLevel = 'tent';
  for (const t of TIER_THRESHOLDS) {
    if (safe >= t.lifetimeSteps) result = t.tier;
  }
  return result;
}

/** 새 누적 걸음으로 등급업 발생했는지 (이전 → 다음 비교) */
export function detectTierUp(
  previousTier: TierLevel,
  newLifetimeSteps: number
): { upgraded: boolean; newTier: TierLevel } {
  const newTier = computeTier(newLifetimeSteps);
  return {
    upgraded: TIER_RANK[newTier] > TIER_RANK[previousTier],
    newTier,
  };
}
