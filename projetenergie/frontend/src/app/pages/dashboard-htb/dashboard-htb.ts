import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnergyService, EnergyRecord } from '../../services/energy.service';

@Component({
  selector: 'app-dashboard-htb',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-htb.html',
  styleUrl: './dashboard-htb.scss'
})
export class DashboardHtbComponent implements OnInit {
  records: EnergyRecord[] = [];
  loading = true;

  constructor(private energyService: EnergyService) {}

  ngOnInit(): void {
    this.energyService.getEnergyData('htb').subscribe({
      next: (data) => {
        this.records = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des données HTB', err);
        this.loading = false;
      }
    });
  }
}
