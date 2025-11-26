import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-reset',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './reset.component.html',
  styleUrls: ['./reset.component.css']
})
export class ResetComponent implements OnInit {
  resetForm!: FormGroup;
  emailSent = false;
  loading = false;
  error: string | null = null;

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.resetForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  onSubmit(): void {
    if (this.resetForm.valid) {
      this.loading = true;
      this.error = null;
      
      const { email } = this.resetForm.value;
      
      // Simulate API call
      setTimeout(() => {
        this.loading = false;
        this.emailSent = true;
        console.log('Password reset email sent to:', email);
      }, 1500);
    }
  }

  resendEmail(): void {
    this.emailSent = false;
    this.resetForm.reset();
  }
}
