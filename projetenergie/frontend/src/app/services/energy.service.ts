import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EnergyRecord {
  id: number;
  timestamp: string;
  energy_type: string;
  category: string;
  label: string;
  value_mwh: number;
  value_fcfa?: number;
  yield_percentage?: number;
  losses_mwh?: number;
  period: string;
  year: number;
}

@Injectable({
  providedIn: 'root'
})
export class EnergyService {
  private apiUrl = 'http://localhost:8000/api/v1/energy';

  constructor(private http: HttpClient) { }

  getEnergyData(energyType?: string): Observable<EnergyRecord[]> {
    let url = this.apiUrl;
    if (energyType) {
      url += `?energy_type=${energyType}`;
    }
    return this.http.get<EnergyRecord[]>(url);
  }

  createEnergyRecord(record: Partial<EnergyRecord>): Observable<EnergyRecord> {
    return this.http.post<EnergyRecord>(this.apiUrl, record);
  }
}
