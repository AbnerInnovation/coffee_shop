import { computed, type ComputedRef } from 'vue'

interface User {
  full_name?: string
  name?: string
  email?: string
  role?: string
  staff_type?: string
  is_active?: boolean
  created_at?: string
}

/**
 * Composable para helpers de perfil de usuario
 */
export function useProfileHelpers(user: ComputedRef<User | null>) {
  /**
   * Obtiene las iniciales del usuario
   */
  const userInitials = computed(() => {
    if (!user.value) return 'U'
    const name = user.value.full_name || user.value.name || user.value.email
    return name
      ?.split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2) || 'U'
  })

  /**
   * Formatea una fecha a formato legible en español
   */
  function formatDate(dateString: string | undefined): string {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  /**
   * Obtiene la variante del badge según el rol
   */
  function getRoleBadgeVariant(role: string | undefined): 'sysadmin' | 'admin' | 'staff' | 'customer' | 'default' {
    switch (role) {
      case 'sysadmin':
        return 'sysadmin'
      case 'admin':
        return 'admin'
      case 'staff':
        return 'staff'
      case 'customer':
        return 'customer'
      default:
        return 'default'
    }
  }

  /**
   * Obtiene la variante del badge según el estado activo
   */
  function getStatusBadgeVariant(isActive: boolean | undefined): 'active' | 'inactive' {
    return isActive ? 'active' : 'inactive'
  }

  return {
    userInitials,
    formatDate,
    getRoleBadgeVariant,
    getStatusBadgeVariant
  }
}
