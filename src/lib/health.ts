import AppleHealthKit, {
  HealthKitPermissions,
  HealthValue,
} from 'react-native-health';

const PERMISSIONS: HealthKitPermissions = {
  permissions: {
    read: [
      AppleHealthKit.Constants.Permissions.StepCount,
      AppleHealthKit.Constants.Permissions.FlightsClimbed,
      AppleHealthKit.Constants.Permissions.DistanceWalkingRunning,
    ],
    write: [],
  },
};

export const initHealthKit = (): Promise<void> =>
  new Promise((resolve, reject) => {
    AppleHealthKit.initHealthKit(PERMISSIONS, (err) => {
      if (err) return reject(new Error(err));
      resolve();
    });
  });

const startOfToday = (): string => {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d.toISOString();
};

export const getTodayStepCount = (): Promise<number> =>
  new Promise((resolve, reject) => {
    AppleHealthKit.getStepCount(
      { date: startOfToday() },
      (err, result: HealthValue) => {
        if (err) return reject(new Error(err));
        resolve(Math.floor(result.value ?? 0));
      }
    );
  });

export const getTodayFlightsClimbed = (): Promise<number> =>
  new Promise((resolve, reject) => {
    AppleHealthKit.getFlightsClimbed(
      { date: startOfToday() },
      (err, result: HealthValue) => {
        if (err) return reject(new Error(err));
        resolve(Math.floor(result.value ?? 0));
      }
    );
  });

export const getTodayDistance = (): Promise<number> =>
  new Promise((resolve, reject) => {
    AppleHealthKit.getDistanceWalkingRunning(
      { date: startOfToday() },
      (err, result: HealthValue) => {
        if (err) return reject(new Error(err));
        resolve(result.value ?? 0);
      }
    );
  });
