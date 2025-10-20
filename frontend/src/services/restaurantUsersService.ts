import api from './api';

export interface RestaurantUser {
  id: number;
  email: string;
  full_name: string;
  role: 'sysadmin' | 'admin' | 'staff' | 'customer';
  is_active: boolean;
  restaurant_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateRestaurantUser {
  email: string;
  full_name: string;
  password: string;
  role: 'admin' | 'staff' | 'customer';
  is_active?: boolean;
}

export interface UpdateRestaurantUser {
  email?: string;
  full_name?: string;
  password?: string;
  role?: 'admin' | 'staff' | 'customer';
  is_active?: boolean;
}

export interface UserCountByRole {
  admin: number;
  staff: number;
  customer: number;
}

class RestaurantUsersService {
  /**
   * Get all users for the current restaurant
   */
  async getUsers(skip: number = 0, limit: number = 100): Promise<RestaurantUser[]> {
    return await api.get(`/restaurant-users/?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get users by role
   */
  async getUsersByRole(role: string, skip: number = 0, limit: number = 100): Promise<RestaurantUser[]> {
    return await api.get(`/restaurant-users/by-role/${role}?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get count of users by role
   */
  async getUserCountByRole(): Promise<UserCountByRole> {
    return await api.get('/restaurant-users/count-by-role');
  }

  /**
   * Get a specific user by ID
   */
  async getUser(userId: number): Promise<RestaurantUser> {
    return await api.get(`/restaurant-users/${userId}`);
  }

  /**
   * Create a new user
   */
  async createUser(user: CreateRestaurantUser): Promise<RestaurantUser> {
    return await api.post('/restaurant-users/', user);
  }

  /**
   * Update a user
   */
  async updateUser(userId: number, user: UpdateRestaurantUser): Promise<RestaurantUser> {
    return await api.put(`/restaurant-users/${userId}`, user);
  }

  /**
   * Delete a user
   */
  async deleteUser(userId: number): Promise<void> {
    return await api.delete(`/restaurant-users/${userId}`);
  }
}

export default new RestaurantUsersService();
