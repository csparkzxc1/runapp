import {
  daypartForTime,
  getYardState,
  seasonForDate,
} from '../season';

const at = (y: number, m1to12: number, d: number, h = 12): Date =>
  new Date(y, m1to12 - 1, d, h, 0, 0);

describe('seasonForDate', () => {
  it('Jan → winter', () => expect(seasonForDate(at(2026, 1, 15))).toBe('winter'));
  it('Feb → winter', () => expect(seasonForDate(at(2026, 2, 28))).toBe('winter'));
  it('Mar → spring', () => expect(seasonForDate(at(2026, 3, 1))).toBe('spring'));
  it('Apr → spring', () => expect(seasonForDate(at(2026, 4, 15))).toBe('spring'));
  it('May → spring', () => expect(seasonForDate(at(2026, 5, 31))).toBe('spring'));
  it('Jun → summer', () => expect(seasonForDate(at(2026, 6, 1))).toBe('summer'));
  it('Aug → summer', () => expect(seasonForDate(at(2026, 8, 31))).toBe('summer'));
  it('Sep → autumn', () => expect(seasonForDate(at(2026, 9, 1))).toBe('autumn'));
  it('Nov → autumn', () => expect(seasonForDate(at(2026, 11, 30))).toBe('autumn'));
  it('Dec → winter', () => expect(seasonForDate(at(2026, 12, 1))).toBe('winter'));
});

describe('daypartForTime', () => {
  it('05:00 → morning', () => expect(daypartForTime(at(2026, 5, 19, 5))).toBe('morning'));
  it('11:59 → morning', () => {
    const d = at(2026, 5, 19, 11);
    d.setMinutes(59);
    expect(daypartForTime(d)).toBe('morning');
  });
  it('12:00 → afternoon', () => expect(daypartForTime(at(2026, 5, 19, 12))).toBe('afternoon'));
  it('17:00 → afternoon', () => expect(daypartForTime(at(2026, 5, 19, 17))).toBe('afternoon'));
  it('18:00 → evening', () => expect(daypartForTime(at(2026, 5, 19, 18))).toBe('evening'));
  it('20:00 → evening', () => expect(daypartForTime(at(2026, 5, 19, 20))).toBe('evening'));
  it('21:00 → night', () => expect(daypartForTime(at(2026, 5, 19, 21))).toBe('night'));
  it('00:00 → night', () => expect(daypartForTime(at(2026, 5, 19, 0))).toBe('night'));
  it('04:59 → night', () => {
    const d = at(2026, 5, 19, 4);
    d.setMinutes(59);
    expect(daypartForTime(d)).toBe('night');
  });
});

describe('getYardState', () => {
  it('combines season + daypart', () => {
    // 2026-05-19 14:00 → spring + afternoon (오늘 컨텍스트와 매칭)
    expect(getYardState(at(2026, 5, 19, 14))).toEqual({
      season: 'spring',
      daypart: 'afternoon',
    });
  });

  it('winter night case', () => {
    expect(getYardState(at(2026, 1, 1, 23))).toEqual({
      season: 'winter',
      daypart: 'night',
    });
  });
});
