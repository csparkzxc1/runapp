// 마카롱 부가 보상 (마일스톤 외): 출석, 광고.

export const ATTENDANCE_REWARD = 1;
export const AD_REWARD_PER_VIEW = 1;
export const DAILY_AD_LIMIT = 10;

export interface AttendanceCheckResult {
  earned: number;
  alreadyClaimed: boolean;
}

export function checkAttendance(
  attendanceClaimed: boolean
): AttendanceCheckResult {
  if (attendanceClaimed) {
    return { earned: 0, alreadyClaimed: true };
  }
  return { earned: ATTENDANCE_REWARD, alreadyClaimed: false };
}

export interface AdRewardResult {
  earned: number;
  newAdsWatched: number;
  reachedDailyCap: boolean;
  reason?: 'cap_reached';
}

/**
 * 광고 1회 시청 보상.
 * 일일 캡(10회) 도달 시 보상 거부.
 */
export function grantAdReward(adsWatchedToday: number): AdRewardResult {
  if (adsWatchedToday >= DAILY_AD_LIMIT) {
    return {
      earned: 0,
      newAdsWatched: adsWatchedToday,
      reachedDailyCap: true,
      reason: 'cap_reached',
    };
  }
  const newCount = adsWatchedToday + 1;
  return {
    earned: AD_REWARD_PER_VIEW,
    newAdsWatched: newCount,
    reachedDailyCap: newCount >= DAILY_AD_LIMIT,
  };
}

/** 디버그: 하루 최대 적립 = 출석 1 + 마일스톤 9 + 광고 10 = 20 */
export const DAILY_MAX_MACARON = 20;
