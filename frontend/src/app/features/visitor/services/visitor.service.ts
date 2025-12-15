import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, delay } from 'rxjs/operators';

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

export interface VisitorStats {
    totalModels: number;
    totalDatasets: number;
    totalCategories: number;
    totalDownloads: number;
}

@Injectable({
    providedIn: 'root'
})
export class VisitorService {
    private apiBaseUrl = 'http://localhost:8000';

    constructor(private http: HttpClient) { }

    /**
     * Get visitor statistics
     */
    getStats(): Observable<VisitorStats> {
        const stats: VisitorStats = {
            totalModels: 2500,
            totalDatasets: 1200,
            totalCategories: 50,
            totalDownloads: 10000000
        };
        return of(stats);
    }

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
     * Get model by ID (read-only for visitors)
     */
    getModelById(id: string): Observable<Model | null> {
        return this.http.get<Model>(`${this.apiBaseUrl}/artifact/model/${id}`).pipe(
            map(model => model || null)
        );
    }

    /**
     * Get dataset by ID (read-only for visitors)
     */
    getDatasetById(id: string): Observable<Dataset | null> {
        return this.http.get<Dataset>(`${this.apiBaseUrl}/artifact/dataset/${id}`).pipe(
            map(dataset => dataset || null)
        );
    }
}
