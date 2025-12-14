import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { ArtifactMetadata, AuthResponse } from './api.types';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiBaseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Authenticate with the backend
   */
  authenticate(): Observable<AuthResponse> {
    // Return empty response for now - authentication handled by other means
    return of({ token: '', user: null });
  }

  /**
   * Get all artifacts
   */
  getAllArtifacts(): Observable<ArtifactMetadata[]> {
    return this.http.get<ArtifactMetadata[]>(`${this.apiBaseUrl}/artifacts`);
  }

  /**
   * Get artifacts by type
   */
  getArtifactsByType(type: string): Observable<ArtifactMetadata[]> {
    return this.http.get<ArtifactMetadata[]>(`${this.apiBaseUrl}/artifacts?type=${type}`);
  }

  /**
   * Get artifact by ID
   */
  getArtifactById(id: string): Observable<ArtifactMetadata> {
    return this.http.get<ArtifactMetadata>(`${this.apiBaseUrl}/artifacts/${id}`);
  }

  /**
   * Create a new artifact
   */
  createArtifact(artifact: Partial<ArtifactMetadata>): Observable<ArtifactMetadata> {
    return this.http.post<ArtifactMetadata>(`${this.apiBaseUrl}/artifacts`, artifact);
  }

  /**
   * Update an artifact
   */
  updateArtifact(id: string, artifact: Partial<ArtifactMetadata>): Observable<ArtifactMetadata> {
    return this.http.put<ArtifactMetadata>(`${this.apiBaseUrl}/artifacts/${id}`, artifact);
  }

  /**
   * Delete an artifact
   */
  deleteArtifact(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiBaseUrl}/artifacts/${id}`);
  }
}
