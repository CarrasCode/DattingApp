import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../../services/auth-service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService); // Inyectamos el servicio aquí dentro
  const token = localStorage.getItem('access_token');

  // Solo añadimos token si existe
  let authReq = req;
  if (token && !req.url.includes('auth')) {
    authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si es un 401 y NO llevamos ya intentando refrescar (evitar bucles)
      if (error.status === 401 && !req.url.includes('auth')) {
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
          // Intentamos refrescar
          return authService.refreshToken(refreshToken).pipe(
            switchMap((newTokens) => {
              // Si funciona, reintentamos la petición original con el NUEVO token
              const newReq = req.clone({
                setHeaders: { Authorization: `Bearer ${newTokens.access}` },
              });
              return next(newReq);
            }),
            catchError((refreshErr) => {
              // Si el refresh también falla, nos rendimos
              authService.logout(); // Borramos todo
              return throwError(() => refreshErr);
            }),
          );
        }
      }
      return throwError(() => error);
    }),
  );
};
