import { computeTier, detectTierUp } from '../tier';

describe('computeTier', () => {
  it('starts at tent', () => {
    expect(computeTier(0)).toBe('tent');
  });

  it('clamps negative to tent', () => {
    expect(computeTier(-1)).toBe('tent');
  });

  it('stays tent below 100k', () => {
    expect(computeTier(99_999)).toBe('tent');
  });

  it('upgrades to cabin at 100k', () => {
    expect(computeTier(100_000)).toBe('cabin');
  });

  it('upgrades to yard_house at 500k', () => {
    expect(computeTier(500_000)).toBe('yard_house');
  });

  it('upgrades to villa at 1.5M', () => {
    expect(computeTier(1_500_000)).toBe('villa');
  });

  it('upgrades to apartment at 3.5M', () => {
    expect(computeTier(3_500_000)).toBe('apartment');
  });

  it('caps at mansion above 7M', () => {
    expect(computeTier(7_000_000)).toBe('mansion');
    expect(computeTier(99_999_999)).toBe('mansion');
  });
});

describe('detectTierUp', () => {
  it('detects no upgrade when below next threshold', () => {
    const r = detectTierUp('tent', 50_000);
    expect(r.upgraded).toBe(false);
    expect(r.newTier).toBe('tent');
  });

  it('detects tent → cabin', () => {
    const r = detectTierUp('tent', 100_000);
    expect(r.upgraded).toBe(true);
    expect(r.newTier).toBe('cabin');
  });

  it('detects skipping multiple tiers (tent → villa)', () => {
    const r = detectTierUp('tent', 2_000_000);
    expect(r.upgraded).toBe(true);
    expect(r.newTier).toBe('villa');
  });

  it('returns no upgrade if already at that tier', () => {
    const r = detectTierUp('cabin', 200_000);
    expect(r.upgraded).toBe(false);
    expect(r.newTier).toBe('cabin');
  });
});
