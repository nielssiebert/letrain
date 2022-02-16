import { ValveTimer } from "./ValveTimer";
import { ValveScheduler } from "./ValveScheduler";
import { ValveFactor } from "./ValveFactor";
export interface Valve {
    id: number;
    name: string;
    isActive: boolean;
    isOn: boolean;
    timer?: ValveTimer;
    factor?: ValveFactor;
    scheduler?: ValveScheduler;
  }