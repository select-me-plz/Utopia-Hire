import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Message {
  _id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export interface UploadedCV {
  _id: string;
  path: string;
  name: string;
  cvImprovements: string | null;
  messages: Message[];
  createdAt?: Date;
  updatedAt?: Date;
}

export interface CVStatus {
  hasCV: boolean;
  uploadedCvs: UploadedCV[];
  user: {
    id: string;
    fullName: string;
    email: string;
  };
}

export interface CVUploadResponse {
  message: string;
  uploadedCv: UploadedCV;
  totalCvs: number;
}

export interface CVImprovements {
  improvements: string | null;
  cvPath: string;
  cvName: string;
}

export interface AddMessageRequest {
  role: 'user' | 'assistant';
  content: string;
}

export interface AddMessageResponse {
  message: string;
  addedMessage: Message;
  totalMessages: number;
}

export interface GetMessagesResponse {
  messages: Message[];
  totalMessages: number;
}

@Injectable({ providedIn: 'root' })
export class CVService {
  private readonly API_BASE_URL = 'http://localhost:3000';

  constructor(private readonly http: HttpClient) {}

  /** Get all CVs + user info */
  getCVStatus(): Observable<CVStatus> {
    return this.http
      .get<CVStatus>(`${this.API_BASE_URL}/api/cv/status`)
      .pipe(catchError(this.handleError));
  }

  /** Upload a new CV (creates a new CV document) */
  uploadCV(file: File): Observable<CVUploadResponse> {
    const formData = new FormData();
    formData.append('cv', file, file.name);

    return this.http
      .post<CVUploadResponse>(`${this.API_BASE_URL}/api/cv/upload`, formData)
      .pipe(catchError(this.handleError));
  }

  /** Get a specific CV by ID */
  getCVById(cvId: string): Observable<UploadedCV> {
    return this.http
      .get<UploadedCV>(`${this.API_BASE_URL}/api/cv/${cvId}`)
      .pipe(catchError(this.handleError));
  }

  /** Get improvements for CV by ID */
  getCVImprovements(cvId: string): Observable<CVImprovements> {
    return this.http
      .get<CVImprovements>(`${this.API_BASE_URL}/api/cv/${cvId}/improvements`)
      .pipe(catchError(this.handleError));
  }

  /** Add a message to a CV conversation */
  addMessage(cvId: string, message: AddMessageRequest): Observable<AddMessageResponse> {
    return this.http
      .post<AddMessageResponse>(`${this.API_BASE_URL}/api/cv/${cvId}/messages`, message)
      .pipe(catchError(this.handleError));
  }

  /** Get all messages for a CV */
  getMessages(cvId: string): Observable<GetMessagesResponse> {
    return this.http
      .get<GetMessagesResponse>(`${this.API_BASE_URL}/api/cv/${cvId}/messages`)
      .pipe(catchError(this.handleError));
  }

  /** Delete CV by ID */
  deleteCV(cvId: string): Observable<{ message: string; totalCvs: number }> {
    return this.http
      .delete<{ message: string; totalCvs: number }>(
        `${this.API_BASE_URL}/api/cv/${cvId}`
      )
      .pipe(catchError(this.handleError));
  }

  /** Download CV file as Blob */
  downloadCVFile(cvId: string): Observable<Blob> {
    const url = `${this.API_BASE_URL}/api/cv/${cvId}/file`;
    console.log('Downloading CV from URL:', url);
    return this.http
      .get(url, {
        responseType: 'blob',
      })
      .pipe(catchError((error) => {
        console.error('Download CV file error:', error);
        console.error('Error status:', error.status);
        console.error('Error URL:', error.url);
        return this.handleError(error);
      }));
  }

  /** Convert stored CV path to full URL */
  getCVUrl(path: string): string {
    return `${this.API_BASE_URL}${path}`;
  }

  /** Error handler */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      errorMessage =
        error.error?.error ||
        `Server Error Code: ${error.status}\nMessage: ${error.message}`;
    }

    console.error('CV Service Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
