import { useQuery } from '@tanstack/react-query';
import {
  getTodayDistance,
  getTodayFlightsClimbed,
  getTodayStepCount,
  initHealthKit,
} from '@/lib/health';

export interface TodayActivity {
  steps: number;
  flights: number;
  distance: number;
}

export const useTodayActivity = (enabled = true) =>
  useQuery<TodayActivity>({
    queryKey: ['health', 'today'],
    enabled,
    queryFn: async () => {
      await initHealthKit();
      const [steps, flights, distance] = await Promise.all([
        getTodayStepCount(),
        getTodayFlightsClimbed(),
        getTodayDistance(),
      ]);
      return { steps, flights, distance };
    },
  });
