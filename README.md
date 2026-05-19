# macaron

운동 데이터를 마카롱(화폐)으로 환산해서 픽셀 아지트를 꾸미는 한국 시장 타깃 React Native + Expo 앱.

**Phase 0 PoC** — HealthKit → Supabase → 마일스톤 적립까지 vertical slice.

## Stack

- React Native + Expo Dev Client (SDK 54)
- TypeScript, expo-router
- Supabase (Auth + Postgres + RLS)
- react-native-health (iOS HealthKit)
- Zustand + @tanstack/react-query

## 셋업

```bash
# 1. 의존성 설치
npm install

# 2. .env 작성 (.env.example 참고)
cp .env.example .env
# EXPO_PUBLIC_SUPABASE_URL, EXPO_PUBLIC_SUPABASE_ANON_KEY 채우기

# 3. Supabase 스키마 적용
# Dashboard → SQL Editor → supabase/schema.sql 내용 실행
# Dashboard → Authentication → Providers → Anonymous Sign-ins ON

# 4. 네이티브 프로젝트 생성
npx expo prebuild --clean

# 5. 실기기로 실행 (HealthKit은 시뮬레이터 ❌)
npx expo run:ios --device
```

## 폴더

```
app/                expo-router screens
├── _layout.tsx     루트 레이아웃 (QueryClient provider)
├── index.tsx       홈 → poc-health로 이동
└── poc-health.tsx  HealthKit + 적립 PoC 화면

src/
├── lib/
│   ├── health.ts     HealthKit 래퍼
│   ├── supabase.ts   Supabase 클라이언트
│   └── macaron.ts    마일스톤 계산 로직
├── stores/userStore.ts
├── hooks/useHealth.ts
└── types/index.ts

supabase/
└── schema.sql      DB 스키마 (profiles, daily_activity, RLS, trigger)
```

## 마카롱 적립 규칙 (v2)

| 이벤트 | 보상 | 빈도 |
|---|---|---|
| 출석 | 1 | 1회/일 (Phase 1+) |
| 1000보 도달 | 1 | 1회/일 |
| 5000보 도달 | 2 | 1회/일 |
| 10000보 도달 | 5 | 1회/일 |
| 10층 도달 | 1 | 1회/일 |
| 광고 시청 | 1 | 최대 10회/일 (Phase 1+) |

헤비 유저 일일 최대치 = 1 + 1 + 2 + 5 + 1 + 10 = **20 마카롱**

## Done 기준 (Phase 0)

- [ ] 실기기 빌드 OK
- [ ] HealthKit 권한 + 걸음/계단/거리 표시
- [ ] 1000/5000/10000보 + 10층 마일스톤 적립
- [ ] 같은 날 새로고침해도 중복 적립 X
- [ ] `daily_activity` upsert + `profiles.macaron_balance` 누적
- [ ] `profiles.lifetime_steps` 누적 (등급업 준비)
