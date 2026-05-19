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
│   ├── macaron.ts    걸음/계단 마일스톤
│   ├── rewards.ts    출석 + 광고 보상
│   ├── tier.ts       등급 임계값 + 승급 감지
│   └── season.ts     마당 시즈널/시간대 (USP)
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

## 등급 시스템

`lifetime_steps`에 따라 자동 승급 (DB trigger). 솔로 개발자 추후 밸런싱.

| 등급 | 누적 걸음 |
|---|---|
| 천막 (tent) | 0 |
| 오두막 (cabin) | 100,000 |
| 마당집 (yard_house) | 500,000 |
| 빌라 (villa) | 1,500,000 |
| 아파트 (apartment) | 3,500,000 |
| 저택 (mansion) | 7,000,000 |

## 시즈널 마당

클라이언트 로컬 시간으로 매 렌더 계산.

| 구분 | 범위 |
|---|---|
| 봄 (벚꽃) | 3-5월 |
| 여름 | 6-8월 |
| 가을 (단풍) | 9-11월 |
| 겨울 (눈) | 12-2월 |
| 아침 | 05-11시 |
| 낮 | 12-17시 |
| 저녁 | 18-20시 |
| 밤 | 21-04시 |

## 픽셀 아트 시안 (placeholder)

Python/PIL로 자동 생성. 실제 게임에선 픽셀 아티스트 작업물로 교체.

```bash
# 모든 시안 재생성
python3 assets/scripts/render_yard.py        # 96 마당 (6 등급 × 4 계절 × 4 시간대)
python3 assets/scripts/render_character.py   # 캐릭터 9슬롯 + 4 프리셋
python3 assets/scripts/render_icons.py       # 20 UI/마일스톤/등급 아이콘
```

**구조:**
```
assets/
├── scripts/        Python 렌더러 (수정 → 일괄 재생성)
├── yard/{tier}/{season}_{daypart}.png   64×64 (8x 스케일)
├── character/parts/{slot}_{key}.png     32×48
├── character/composed/{preset}.png      32×48 프리셋
└── icons/{name}.png + {name}@16x.png    16×16 (원본 + 16배 확대)
```

각 그리드 시안: `assets/yard/_overview_tiers.png`, `assets/character/_overview.png`, `assets/icons/_overview.png`.

## Done 기준 (Phase 0)

검증됨 (컨테이너):
- [x] 모든 순수 로직 단위 테스트 50개 통과 (`npm test`)
- [x] TypeScript 클린 (`npm run typecheck`)
- [x] DB 스키마 (RLS, trigger, 등급 자동 동기화)

실기기에서 확인 필요:
- [ ] HealthKit 권한 + 걸음/계단/거리 표시
- [ ] 1000/5000/10000보 + 10층 마일스톤 적립
- [ ] 같은 날 새로고침해도 중복 적립 X
- [ ] 출석 보상 1회/일
- [ ] 광고 mock 10회/일 캡
- [ ] 등급업 자동 (DB trigger)
- [ ] `daily_activity` upsert + `profiles.macaron_balance` 누적
