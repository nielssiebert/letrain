import { Time } from "@angular/common";

export interface ValveScheduler {
    id: number;
    name: string;
    everyDay: number;
    times: {
      hours: number;
      minutes: number;
      seconds: number;
    }[];
    //everySecond: number;
  }