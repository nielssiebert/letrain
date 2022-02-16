import { Component, Input, OnInit } from '@angular/core';
import { Valve } from '../Valve';

@Component({
  selector: 'app-valve',
  templateUrl: './valve.component.html',
  styleUrls: ['./valve.component.css']
})
export class ValveComponent implements OnInit {

  @Input() valve?: Valve;

  constructor() { }

  ngOnInit(): void {
  }

}
