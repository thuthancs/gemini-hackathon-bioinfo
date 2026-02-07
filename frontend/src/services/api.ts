/** API client for backend communication. */
import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import type { AnalysisRequest, AnalysisResponse, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 300000, // 5 minutes for long-running pipeline
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error status
          const message = (error.response.data as any)?.detail || error.message;
          throw new Error(message);
        } else if (error.request) {
          // Request made but no response received
          throw new Error('Network error: Could not reach server');
        } else {
          // Something else happened
          throw new Error(error.message || 'An unexpected error occurred');
        }
      }
    );
  }

  /**
   * Analyze a mutation and find potential rescue mutations.
   */
  async analyzeMutation(
    sequence: string,
    mutation: string,
    protein?: string
  ): Promise<AnalysisResponse> {
    const request: AnalysisRequest = {
      sequence,
      mutation,
      protein,
    };

    try {
      const response = await this.client.post<AnalysisResponse>('/analyze', request);
      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to analyze mutation');
    }
  }

  /**
   * Check API health status.
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>('/health');
      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to check health');
    }
  }
}

export const apiClient = new ApiClient();

