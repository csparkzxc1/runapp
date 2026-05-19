// 마당 시즈널 자동 변화 — USP.
// 클라이언트 로컬 시간 기준. 사용자 폰의 KST가 정상 동작 기준.

export type Season = 'spring' | 'summer' | 'autumn' | 'winter';
export type Daypart = 'morning' | 'afternoon' | 'evening' | 'night';

export interface YardState {
  season: Season;
  daypart: Daypart;
}

/**
 * 한국 절기 기준:
 *  봄 3-5월 (벚꽃), 여름 6-8월, 가을 9-11월 (단풍), 겨울 12-2월 (눈)
 */
export function seasonForDate(date: Date): Season {
  const m = date.getMonth(); // 0-11
  if (m >= 2 && m <= 4) return 'spring';
  if (m >= 5 && m <= 7) return 'summer';
  if (m >= 8 && m <= 10) return 'autumn';
  return 'winter';
}

/**
 *  morning   05-11
 *  afternoon 12-17
 *  evening   18-20
 *  night     21-04
 */
export function daypartForTime(date: Date): Daypart {
  const h = date.getHours();
  if (h >= 5 && h <= 11) return 'morning';
  if (h >= 12 && h <= 17) return 'afternoon';
  if (h >= 18 && h <= 20) return 'evening';
  return 'night';
}

export function getYardState(date: Date = new Date()): YardState {
  return {
    season: seasonForDate(date),
    daypart: daypartForTime(date),
  };
}

/** 한국어 라벨 (UI용) */
export const SEASON_LABEL: Record<Season, string> = {
  spring: '봄 (벚꽃)',
  summer: '여름',
  autumn: '가을 (단풍)',
  winter: '겨울 (눈)',
};

export const DAYPART_LABEL: Record<Daypart, string> = {
  morning: '아침',
  afternoon: '낮',
  evening: '저녁',
  night: '밤',
};
