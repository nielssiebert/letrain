import { Component, Input, OnInit } from '@angular/core';
import { ValveService } from '../service/valve.service';
import { Valve } from './Valve';
import { ValveComponent } from './valve/valve.component';

@Component({
  selector: 'app-valves',
  templateUrl: './valves.component.html',
  styleUrls: ['./valves.component.css']
})
export class ValvesComponent implements OnInit {


  valves: Valve[] = [];
  constructor( private valveService: ValveService) {
  }

  getValves(): void {
    this.valves = this.valveService.getValves();
  }

  ngOnInit(): void {
    this.getValves();
  }

}
