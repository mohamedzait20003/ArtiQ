import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Model {
  id: string;
  name: string;
  size: number;
  description: string;
}

export interface Dataset {
  id: string;
  name: string;
  size: number;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiBaseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  /**
   * Get first 10 models from API
   */
  getModels(): Observable<Model[]> {
    return this.http.get<Model[]>(`${this.apiBaseUrl}/artifact/model/first10`);
  }

  /**
   * Get first 10 datasets from API
   */
  getDatasets(): Observable<Dataset[]> {
    return this.http.get<Dataset[]>(`${this.apiBaseUrl}/artifact/dataset/first10`);
  }

  /**
   * Search models by name with fuzzy matching
   */
  searchModels(name: string): Observable<Model[]> {
    if (!name || name.trim() === '') {
      return this.getModels();
    }
    return this.http.get<Model[]>(`${this.apiBaseUrl}/artifact/model/byName/${encodeURIComponent(name)}`);
  }

  /**
   * Search datasets by name with fuzzy matching
   */
  searchDatasets(name: string): Observable<Dataset[]> {
    if (!name || name.trim() === '') {
      return this.getDatasets();
    }
    return this.http.get<Dataset[]>(`${this.apiBaseUrl}/artifact/dataset/byName/${encodeURIComponent(name)}`);
  }

  /**
   * Delete a model by ID
   */
  deleteModel(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiBaseUrl}/artifacts/model/${id}`);
  }

  /**
   * Delete a dataset by ID
   */
  deleteDataset(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiBaseUrl}/artifacts/dataset/${id}`);
  }

  /**
   * Update a model
   */
  updateModel(id: string, data: Partial<Model>): Observable<Model> {
    return this.http.put<Model>(`${this.apiBaseUrl}/artifact/model/${id}`, data);
  }

  /**
   * Update a dataset
   */
  updateDataset(id: string, data: Partial<Dataset>): Observable<Dataset> {
    return this.http.put<Dataset>(`${this.apiBaseUrl}/artifact/dataset/${id}`, data);
  }
}
