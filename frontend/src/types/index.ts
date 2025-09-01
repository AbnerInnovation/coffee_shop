// Re-export all types from components for easier imports
export type { MenuItem, MenuItemVariant } from '@/components/menu/MenuList.vue';
export type { MenuItemFormData } from '@/components/menu/MenuItemForm.vue';

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  error?: string;
  status?: number;
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

// Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'staff' | 'customer';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
  confirmPassword: string;
}

// Common Types
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;

export type WithId<T, ID = string> = T & { id: ID };
export type WithTimestamps<T> = T & {
  createdAt: string;
  updatedAt: string;
  deletedAt?: string;
};

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type ValueOf<T> = T[keyof T];

export type AnyFunction = (...args: any[]) => any;

// Form Types
export type FormErrors<T> = {
  [P in keyof T]?: string | string[];
};

export type FormState<T> = {
  values: T;
  errors: FormErrors<T>;
  isSubmitting: boolean;
  isValid: boolean;
};

// UI Types
export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  duration?: number;
}

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info' | 'ghost' | 'link';

export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// API Error Handling
export interface ApiError extends Error {
  status?: number;
  code?: string;
  details?: any;
  response?: {
    data?: any;
    status?: number;
    statusText?: string;
    headers?: any;
  };
}

// Table Types
export interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  format?: (value: any, row: T) => any;
  render?: (row: T) => any;
  className?: string;
  headerClassName?: string;
}

export interface SortState {
  key: string;
  direction: 'asc' | 'desc';
}

// Form Field Types
export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'date' | 'time' | 'datetime-local' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'file';

export interface FormField<T = any> {
  name: keyof T | string;
  label: string;
  type?: InputType;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  options?: Array<{ label: string; value: any; disabled?: boolean }>;
  validation?: {
    required?: string | boolean;
    min?: number | { value: number; message: string };
    max?: number | { value: number; message: string };
    minLength?: number | { value: number; message: string };
    maxLength?: number | { value: number; message: string };
    pattern?: { value: RegExp; message: string };
    validate?: (value: any) => string | boolean | Promise<string | boolean>;
  };
  className?: string;
  wrapperClassName?: string;
  helpText?: string;
  prefix?: string;
  suffix?: string;
  rows?: number;
  cols?: number;
  multiple?: boolean;
  accept?: string;
  step?: number | string;
  min?: number | string;
  max?: number | string;
  autocomplete?: string;
}
