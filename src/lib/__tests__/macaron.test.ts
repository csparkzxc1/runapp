import { calculateMilestoneRewards } from '../macaron';

describe('calculateMilestoneRewards', () => {
  it('returns nothing below all thresholds', () => {
    const r = calculateMilestoneRewards({ steps: 999, flights: 9 }, []);
    expect(r.earned).toBe(0);
    expect(r.newMilestones).toEqual([]);
  });

  it('awards +1 at 1000 steps', () => {
    const r = calculateMilestoneRewards({ steps: 1000, flights: 0 }, []);
    expect(r.earned).toBe(1);
    expect(r.newMilestones).toEqual(['steps_1000']);
  });

  it('awards 1+2=3 at 5000 steps cumulatively', () => {
    const r = calculateMilestoneRewards({ steps: 5000, flights: 0 }, []);
    expect(r.earned).toBe(3);
    expect(r.newMilestones).toEqual(['steps_1000', 'steps_5000']);
  });

  it('awards 1+2+5=8 at 10000 steps cumulatively', () => {
    const r = calculateMilestoneRewards({ steps: 10_000, flights: 0 }, []);
    expect(r.earned).toBe(8);
    expect(r.newMilestones).toEqual([
      'steps_1000',
      'steps_5000',
      'steps_10000',
    ]);
  });

  it('awards +1 at 10 flights', () => {
    const r = calculateMilestoneRewards({ steps: 0, flights: 10 }, []);
    expect(r.earned).toBe(1);
    expect(r.newMilestones).toEqual(['flights_10']);
  });

  it('awards full daily total at 10k steps + 10 flights = 9', () => {
    const r = calculateMilestoneRewards({ steps: 10_000, flights: 10 }, []);
    expect(r.earned).toBe(9);
    expect(r.newMilestones).toEqual([
      'steps_1000',
      'steps_5000',
      'steps_10000',
      'flights_10',
    ]);
  });

  it('skips already-granted milestones (idempotent re-sync)', () => {
    const r = calculateMilestoneRewards(
      { steps: 10_000, flights: 10 },
      ['steps_1000', 'steps_5000']
    );
    expect(r.earned).toBe(5 + 1);
    expect(r.newMilestones).toEqual(['steps_10000', 'flights_10']);
  });

  it('returns zero earned when all milestones already granted', () => {
    const r = calculateMilestoneRewards(
      { steps: 12_345, flights: 99 },
      ['steps_1000', 'steps_5000', 'steps_10000', 'flights_10']
    );
    expect(r.earned).toBe(0);
    expect(r.newMilestones).toEqual([]);
  });

  it('awards mid-day milestones partially (1000 yes, 5000 no)', () => {
    const r = calculateMilestoneRewards({ steps: 4999, flights: 9 }, []);
    expect(r.earned).toBe(1);
    expect(r.newMilestones).toEqual(['steps_1000']);
  });
});
