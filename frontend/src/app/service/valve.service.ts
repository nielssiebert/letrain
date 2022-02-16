import { Injectable } from '@angular/core';
import { Valve } from '../valves/Valve';
import { ValveFactor } from '../valves/ValveFactor';
import { ValveTimer } from '../valves/ValveTimer';

@Injectable({
  providedIn: 'root'
})
export class ValveService {
  valve1: Valve = {
    factor : {
      id : 1,
      name : "valveFactor1",
      percent : 100
    },
    isActive : false,
    name : "valve1",
    isOn : false,
    id : 1,
    // scheduler : {
    //   everyDay : 1,
    //   id: 1,
    //   name: "valveScheduler1",
    //   times: [{
    //     hours: 8,
    //     minutes: 0,
    //     seconds: 0
    //   },{
    //     hours: 20,
    //     minutes: 0,
    //     seconds: 0
    //   }]
    // },
    timer : {
      id : 1,
      h : 0,
      m : 10,
      s : 0
    }

  };
  valve2: Valve = {
    factor : {
      id : 1,
      name : "valveFactor2",
      percent : 100
    },
    isActive : false,
    name : "valve2",
    isOn : false,
    id : 2,
    // scheduler : {
    //   everyDay : 1,
    //   id: 1,
    //   name: "valveScheduler2",
    //   times: [{
    //     hours: 7,
    //     minutes: 0,
    //     seconds: 0
    //   },{
    //     hours: 21,
    //     minutes: 0,
    //     seconds: 0
    //   }]
    // },
    timer : {
      id : 1,
      h : 0,
      m : 10,
      s : 0
    }

  };
  getValves(){
      return [this.valve1,this.valve2];
  }
  constructor() { }
}
