import {
  AD_REWARD_PER_VIEW,
  ATTENDANCE_REWARD,
  DAILY_AD_LIMIT,
  DAILY_MAX_MACARON,
  checkAttendance,
  grantAdReward,
} from '../rewards';

describe('checkAttendance', () => {
  it('awards 1 when not claimed yet today', () => {
    const r = checkAttendance(false);
    expect(r.earned).toBe(ATTENDANCE_REWARD);
    expect(r.alreadyClaimed).toBe(false);
  });

  it('refuses second claim same day', () => {
    const r = checkAttendance(true);
    expect(r.earned).toBe(0);
    expect(r.alreadyClaimed).toBe(true);
  });
});

describe('grantAdReward', () => {
  it('awards 1 macaron per view', () => {
    const r = grantAdReward(0);
    expect(r.earned).toBe(AD_REWARD_PER_VIEW);
    expect(r.newAdsWatched).toBe(1);
    expect(r.reachedDailyCap).toBe(false);
  });

  it('increments correctly mid-day', () => {
    const r = grantAdReward(5);
    expect(r.earned).toBe(1);
    expect(r.newAdsWatched).toBe(6);
    expect(r.reachedDailyCap).toBe(false);
  });

  it('reports cap reached on the 10th ad', () => {
    const r = grantAdReward(9);
    expect(r.earned).toBe(1);
    expect(r.newAdsWatched).toBe(10);
    expect(r.reachedDailyCap).toBe(true);
  });

  it('refuses 11th ad', () => {
    const r = grantAdReward(10);
    expect(r.earned).toBe(0);
    expect(r.newAdsWatched).toBe(10);
    expect(r.reachedDailyCap).toBe(true);
    expect(r.reason).toBe('cap_reached');
  });

  it('refuses far past cap', () => {
    const r = grantAdReward(100);
    expect(r.earned).toBe(0);
    expect(r.newAdsWatched).toBe(100);
  });
});

describe('daily maximum sanity', () => {
  it('matches the documented headline (20/day)', () => {
    const attend = checkAttendance(false).earned;
    // 마일스톤 합: 1 + 2 + 5 + 1 = 9
    const milestones = 1 + 2 + 5 + 1;
    const ads = DAILY_AD_LIMIT * AD_REWARD_PER_VIEW;
    expect(attend + milestones + ads).toBe(DAILY_MAX_MACARON);
  });
});
