import { ref } from 'vue';
import restaurantUsersService, { type RestaurantUser } from '@/services/restaurantUsersService';

/**
 * Composable for managing users state and operations
 */
export function useUsers() {
  const users = ref<RestaurantUser[]>([]);
  const loading = ref(false);
  const error = ref('');
  const currentFilter = ref('all');

  /**
   * Load all users
   */
  const loadUsers = async () => {
    loading.value = true;
    error.value = '';
    try {
      users.value = await restaurantUsersService.getUsers();
    } catch (err) {
      console.error('Error loading users:', err);
      error.value = 'Failed to load users';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Filter users by role
   */
  const filterByRole = async (role: string) => {
    currentFilter.value = role;
    loading.value = true;
    error.value = '';
    try {
      if (role === 'all') {
        users.value = await restaurantUsersService.getUsers();
      } else {
        users.value = await restaurantUsersService.getUsersByRole(role);
      }
    } catch (err) {
      console.error('Error filtering users:', err);
      error.value = 'Failed to filter users';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Toggle user active status
   */
  const toggleUserStatus = async (user: RestaurantUser) => {
    try {
      error.value = '';
      await restaurantUsersService.updateUser(user.id, {
        is_active: !user.is_active
      });
      await loadUsers();
      return { success: true, wasActive: user.is_active };
    } catch (err: any) {
      console.error('Error toggling user status:', err);
      error.value = err.response?.data?.detail || 'Failed to toggle user status';
      return { success: false };
    }
  };

  /**
   * Delete user
   */
  const deleteUser = async (userId: number) => {
    try {
      error.value = '';
      await restaurantUsersService.deleteUser(userId);
      await loadUsers();
      return { success: true };
    } catch (err: any) {
      console.error('Error deleting user:', err);
      error.value = err.response?.data?.detail || 'Failed to delete user';
      return { success: false };
    }
  };

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = '';
  };

  return {
    // State
    users,
    loading,
    error,
    currentFilter,
    
    // Actions
    loadUsers,
    filterByRole,
    toggleUserStatus,
    deleteUser,
    clearError
  };
}
