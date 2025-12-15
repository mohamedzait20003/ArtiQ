/**
 * API Type Definitions
 */

export interface ArtifactMetadata {
  id: string;
  name: string;
  type: string;
  description?: string;
  author?: string;
  version?: string;
  tags?: string[];
  createdAt?: string;
  updatedAt?: string;
}

export interface AuthResponse {
  token: string;
  user: any;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}
