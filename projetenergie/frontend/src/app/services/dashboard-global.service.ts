import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RendementRecord {
  id: number;
  date: string;
  vente_woyofal: number | null;
  vente_classique: number | null;
  production_senelec: number | null;
  production_ipp: number | null;
  energie_hta: number | null;
  energie_htb: number | null;
  producteur_hta: number | null;
  producteur_htb: number | null;
  client_hta: number | null;
  client_htb: number | null;
  rendement_global: number | null;
  rendement_hta: number | null;
  rendement_htb: number | null;
}

@Injectable({ providedIn: 'root' })
export class DashboardGlobalService {
  private http = inject(HttpClient);
  private readonly API_URL = '/api/v1';

  getRendements(limit = 500): Observable<RendementRecord[]> {
    return this.http.get<RendementRecord[]>(`${this.API_URL}/rendements`, {
      params: { skip: 0, limit }
    });
  }
}
