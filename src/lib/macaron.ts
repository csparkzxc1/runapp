// 걸음/계단 마일스톤 (1회/일).
// 출석/광고 보상은 src/lib/rewards.ts.

export const STEP_MILESTONES = [
  { key: 'steps_1000', threshold: 1000, reward: 1 },
  { key: 'steps_5000', threshold: 5000, reward: 2 },
  { key: 'steps_10000', threshold: 10000, reward: 5 },
] as const;

export const FLIGHT_MILESTONES = [
  { key: 'flights_10', threshold: 10, reward: 1 },
] as const;

export interface DailyActivity {
  steps: number;
  flights: number;
}

export interface MilestoneResult {
  earned: number;
  newMilestones: string[];
}

/**
 * 마일스톤 도달 시 1회/일 보상.
 * 이미 grantedMilestones에 있는 마일스톤은 중복 적립 안 함.
 */
export function calculateMilestoneRewards(
  activity: DailyActivity,
  grantedMilestones: string[]
): MilestoneResult {
  let earned = 0;
  const newMilestones: string[] = [];

  for (const m of STEP_MILESTONES) {
    if (activity.steps >= m.threshold && !grantedMilestones.includes(m.key)) {
      earned += m.reward;
      newMilestones.push(m.key);
    }
  }

  for (const m of FLIGHT_MILESTONES) {
    if (activity.flights >= m.threshold && !grantedMilestones.includes(m.key)) {
      earned += m.reward;
      newMilestones.push(m.key);
    }
  }

  return { earned, newMilestones };
}
