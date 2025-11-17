import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CVService, CVStatus, UploadedCV } from '../../services/cv.service';
import { LoadingService } from '../../services/loading.service';
import { ResponseParser } from './CV_parse_flask';

interface AIResponse {
  mode: string;
  response: string;
}

interface ParserAiRequest {
  message: string;
  resume_json: {
    name: string;
    email: string;
    skills: string[];
    education: string;
  }
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly cvService = inject(CVService);
  private readonly loading = inject(LoadingService);

  readonly userFullName = computed(() => this.auth.getUser()?.fullName ?? '');

  // CV State
  cvStatus = signal<CVStatus | null>(null);
  hasCV = computed(() => (this.cvStatus()?.uploadedCvs.length ?? 0) > 0);

  isLoading = signal(false);
  uploadError = signal<string | null>(null);

  /** Tracks which CV ID is expanded for improvements */
  expandedImprovement = signal<string | null>(null);
  expandedCv = signal<UploadedCV | null>(null);
  chatMode = signal<'interview' | 'cv' | null>(null);
  response = signal<string>('');

  ngOnInit() {
    this.loadCVStatus();
  }

  expandCv(cv: UploadedCV | null) {
    this.expandedCv.set(cv);
    this.chatMode.set('cv');

    if (cv) {
      // Fetch the CV file and send to Flask endpoint
      this.loadAndSendCVToFlask(cv);
    }
  }

  /** Load CV file and send to Flask for processing */
  private loadAndSendCVToFlask(cv: UploadedCV) {
    this.isLoading.set(true);
    this.uploadError.set(null);

    console.log('Starting to download CV:', cv._id);

    this.cvService.downloadCVFile(cv._id).subscribe({
      next: (blob: Blob) => {
        console.log('✅ CV file downloaded successfully, size:', blob.size);
        
        // Create FormData to send file to Flask
        const formData = new FormData();
        formData.append('file', blob, cv.name);

        console.log('📤 Sending to Flask endpoint...');

        // Send to Flask endpoint (adjust URL as needed)
        fetch('http://localhost:5000/api/pdf_parse', {
          method: 'POST',
          body: formData,
        })
          .then((response) => {
            console.log('Flask response status:', response.status);
            if (!response.ok) {
              throw new Error(`Flask error: ${response.status} ${response.statusText}`);
            }
            return response.json();
          })
          .then((data) => {
            console.log('✅ Flask Response:', data);
            const response: ResponseParser = data;
            const AiRequest: ParserAiRequest = {
              message: `Provide feedback on this resume: ${cv.name}`,
              resume_json: {
                name: response.personal_info.name,
                email: response.personal_info.emails[0] || '',
                skills: response.skills.extracted,
                education: response.education,
              }
            };
            console.log('📤 Prepared AI Request:', AiRequest);
            fetch(
              "https://fd1frmxd-5000.uks1.devtunnels.ms/assistant",
              {method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(AiRequest),
            }).then((aiResponse) => {
              console.log('✅ AI Response status:', aiResponse.status);
              this.response.set("Response received from AI.");
            }).catch((error) => {
              console.error('❌ Error sending to AI endpoint:', error);
            });
            this.isLoading.set(false);
          })
          .catch((error) => {
            console.error('❌ Error sending CV to Flask:', error);
            this.uploadError.set(`Failed to process CV: ${error.message}`);
            this.isLoading.set(false);
          });
      },
      error: (err) => {
        console.error('❌ Error downloading CV file:', err);
        console.error('Error details:', err.message);
        this.uploadError.set(`Failed to download CV file: ${err.message}`);
        this.isLoading.set(false);
      },
    });
  }

  loadCVStatus() {
    this.isLoading.set(true);
    this.cvService.getCVStatus().subscribe({
      next: (status) => {
        this.cvStatus.set(status);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error loading CV status:', err);
        this.isLoading.set(false);
      },
    });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    // File validation
    if (file.type !== 'application/pdf') {
      this.uploadError.set('Only PDF files are allowed.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      this.uploadError.set('File size must be under 5MB.');
      return;
    }

    this.uploadError.set(null);
    this.isLoading.set(true);

    this.cvService.uploadCV(file).subscribe({
      next: () => {
        this.loadCVStatus();
      },
      error: (err) => {
        console.error('CV Upload Error:', err);
        this.uploadError.set(err.message || 'Upload failed.');
        this.isLoading.set(false);
      },
    });
  }

  triggerFileInput() {
    const input = document.getElementById('cv-file-input') as HTMLInputElement;
    input?.click();
  }

  /** Expand improvements for one CV by ID */
  toggleImprovements(cvId: string) {
    const current = this.expandedImprovement();

    // Collapse if already open
    if (current === cvId) {
      this.expandedImprovement.set(null);
      return;
    }

    this.expandedImprovement.set(cvId);

    const cv = this.cvStatus()?.uploadedCvs.find(c => c._id === cvId);
    if (!cv) return;

    // If improvements already exist, do not refetch
    if (cv.cvImprovements) return;

    // Fetch improvements
    this.cvService.getCVImprovements(cvId).subscribe({
      next: (result) => {
        const status = this.cvStatus();
        if (!status) return;

        const updatedCVs = status.uploadedCvs.map(c => {
          if (c._id === cvId) {
            return {
              ...c,
              cvImprovements: result.improvements,
            };
          }
          return c;
        });

        this.cvStatus.set({
          ...status,
          uploadedCvs: updatedCVs,
        });
      },
      error: (err) => {
        console.error('Error loading improvements:', err);
      },
    });
  }

  logout() {
    this.loading.show();
    this.auth.logout();
    setTimeout(() => {
      this.router.navigate(['/']).finally(() => this.loading.hide());
    }, 1500);
  }
}
