# Plan de Aprendizaje: Angular Moderno (v21+)

> [!NOTE]
> Este plan se basa estrictamente en la documentación oficial (`angular.dev`) y las mejores prácticas modernas encontradas (Signals, Standalone Components, etc.).

## 1. Fundamentos (Essentials) ✅

- [x] **Arquitectura de Componentes**: Entender `Standalone Components`.
- [x] **Style Guide Compliance**: Adoptar convenciones de nombres, estructura y `inject()`.
- [x] **Templates y Data Binding**: Sintaxis moderna (`@if`, `@for`).
- [x] **Manejo de Eventos**: Interacción básica de usuario.
- [x] **Inputs y Outputs**: Comunicación entre componentes con Signals (`input()`, `output()`).
- [x] **Inyección de Dependencias**: Servicios y `inject()`.

## 2. Reactividad y Estado (Signals) ✅

- [x] **Signals**: El nuevo estándar de reactividad (`signal()`, `computed()`).

## 3. Características Avanzadas ✅

- [x] **Routing**: Navegación en aplicaciones SPA.
- [x] **Formularios**: Reactive Forms.
- [x] **Optimizaciones**: Deferrable Views (`@defer`).

---

## 🚀 Fase 2: Integración Real (Backend Django)

## 4. Conexión HTTP y Entornos

- [ ] **HttpClient Moderno**: `provideHttpClient` y `withFetch`.
- [ ] **Environments**: Gestionar URLs de desarrollo vs producción.

## 5. Autenticación (JWT)

- [ ] **Login Real**: POST a `api/users/auth/login/`.
- [ ] **Manejo de Sesión**: Guardar Tokens (localStorage vs Cookies).
- [ ] **Interceptors**: Adjuntar token automáticamente a las peticiones.

## 6. Consumo de Datos (Relación Frontend-Backend) ✅

- [x] **Resource API**: La nueva forma experimental (`rxResource`) o `HttpClient` clásico para traer usuarios.
- [x] **Manejo de Errores**: Feedback visual al usuario.

## 7. Seguridad Avanzada

- [ ] **Token Refresh**: Interceptar 401, refrescar token y reintentar.

---

## Lección Actual: HTTP & Environments

**Objetivo**: Configurar el cliente HTTP y preparar la URL de la API.
