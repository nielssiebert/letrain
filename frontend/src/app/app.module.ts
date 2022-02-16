import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { MatSliderModule } from '@angular/material/slider';
import { AppComponent } from './app.component';
import { RelayToggleComponent } from './relay-toggle/relay-toggle.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonToggleModule} from '@angular/material/button-toggle';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import {MatCardModule} from '@angular/material/card';
import { ValvesComponent } from './valves/valves.component';
import { ValveComponent } from './valves/valve/valve.component';
import { SchedulerComponent } from './scheduler/scheduler.component';

@NgModule({
  declarations: [
    AppComponent,
    RelayToggleComponent,
    ValvesComponent,
    ValveComponent,
    SchedulerComponent
  ],
  imports: [
    BrowserModule,
    MatSliderModule,
    MatButtonToggleModule,
    MatSlideToggleModule,
    MatCardModule,
    BrowserAnimationsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
