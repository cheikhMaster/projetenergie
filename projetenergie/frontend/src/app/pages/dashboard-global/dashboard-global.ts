import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardGlobalService, RendementRecord } from '../../services/dashboard-global.service';

interface SummaryCard {
  label: string;
  value: string;
  unit: string;
  category: 'hta' | 'htb' | 'production' | 'ventes';
}

@Component({
  selector: 'app-dashboard-global',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-global.html',
  styleUrl: './dashboard-global.scss'
})
export class DashboardGlobalComponent implements OnInit {
  private service = inject(DashboardGlobalService);

  records = signal<RendementRecord[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  private sum = (key: keyof RendementRecord) =>
    this.records().reduce((acc, r) => acc + (Number(r[key]) || 0), 0);

  private avg = (key: keyof RendementRecord) => {
    const values = this.records()
      .map(r => r[key])
      .filter((v): v is number => v !== null && v !== undefined && !isNaN(Number(v)));
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + Number(b), 0) / values.length;
  };

  private fmt = (n: number) =>
    new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 }).format(n);

  private fmtPct = (n: number) =>
    new Intl.NumberFormat('fr-FR', { style: 'percent', maximumFractionDigits: 1 }).format(n);

  cards = computed<SummaryCard[]>(() => {
    if (this.records().length === 0) return [];
    return [
      // HTA
      { category: 'hta', label: 'Énergie HTA (total)', value: this.fmt(this.sum('energie_hta')), unit: 'MWh' },
      { category: 'hta', label: 'Rendement HTA (moyen)', value: this.fmtPct(this.avg('rendement_hta')), unit: '' },
      // HTB
      { category: 'htb', label: 'Énergie HTB (total)', value: this.fmt(this.sum('energie_htb')), unit: 'MWh' },
      { category: 'htb', label: 'Rendement HTB (moyen)', value: this.fmtPct(this.avg('rendement_htb')), unit: '' },
      // Production
      { category: 'production', label: 'Production Senelec (total)', value: this.fmt(this.sum('production_senelec')), unit: 'MWh' },
      { category: 'production', label: 'Production IPP (total)', value: this.fmt(this.sum('production_ipp')), unit: 'MWh' },
      // Ventes
      { category: 'ventes', label: 'Vente Woyofal (total)', value: this.fmt(this.sum('vente_woyofal')), unit: 'FCFA' },
      { category: 'ventes', label: 'Vente classique (total)', value: this.fmt(this.sum('vente_classique')), unit: 'FCFA' },
    ];
  });

  rendementGlobalMoyen = computed(() => this.fmtPct(this.avg('rendement_global')));
  nombreEnregistrements = computed(() => this.records().length);

  ngOnInit(): void {
    this.service.getRendements().subscribe({
      next: (data) => {
        this.records.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set("Impossible de charger les données du dashboard.");
        this.loading.set(false);
      }
    });
  }
}
