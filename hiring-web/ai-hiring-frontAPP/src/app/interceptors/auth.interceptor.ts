import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  // Skip adding token for login and register endpoints
  const isPublicRoute = req.url.includes('/api/auth/login') || req.url.includes('/api/auth/register');
  
  if (!isPublicRoute) {
    const token = authService.getToken();
    if (token) {
      // Clone the request and add the Authorization header
      const clonedReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
      return next(clonedReq);
    }
  }
  
  return next(req);
};

