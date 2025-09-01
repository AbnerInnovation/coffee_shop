<template>
  <div>
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Stats Cards -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Orders Today</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">24</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Revenue Today</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">$1,234.56</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Active Tables</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">8/12</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Popular Item</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">Cappuccino</dd>
      </div>
    </div>
    
    <div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Recent Orders -->
      <div class="overflow-hidden rounded-lg bg-white shadow">
        <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Recent Orders</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Order #</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Table</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Amount</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="order in recentOrders" :key="order.id" class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">#{{ order.id }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ order.table }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <span :class="getStatusBadgeClass(order.status)" class="inline-flex rounded-full px-2 text-xs font-semibold leading-5">
                      {{ order.status }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    ${{ order.amount.toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-4 text-right">
            <router-link to="/orders" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              View all orders
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Low Stock Items -->
      <div class="overflow-hidden rounded-lg bg-white shadow">
        <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Low Stock Items</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Item</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Category</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Stock</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="item in lowStockItems" :key="item.id" class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="flex items-center">
                      <div class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full" :src="item.image" :alt="item.name" />
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ item.name }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ item.category }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ item.stock }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <span :class="getStockStatusClass(item.stock)" class="inline-flex rounded-full px-2 text-xs font-semibold leading-5">
                      {{ getStockStatusLabel(item.stock) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-4 text-right">
            <router-link to="/inventory" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              View inventory
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Mock data - replace with API calls in a real application
const recentOrders = ref([
  { id: '1001', table: 'T-05', status: 'Preparing', amount: 24.50 },
  { id: '1000', table: 'T-12', status: 'Ready', amount: 18.75 },
  { id: '999', table: 'T-08', status: 'Completed', amount: 32.20 },
  { id: '998', table: 'T-03', status: 'Preparing', amount: 15.90 },
  { id: '997', table: 'T-11', status: 'Completed', amount: 27.50 },
]);

const lowStockItems = ref([
  { id: 1, name: 'Espresso Beans', category: 'Coffee', stock: 2, image: 'https://images.unsplash.com/photo-1511920170033-f8396924c348?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60' },
  { id: 2, name: 'Oat Milk', category: 'Dairy', stock: 1, image: 'https://images.unsplash.com/photo-1622180203372-8a193de24d75?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60' },
  { id: 3, name: 'Chocolate Croissant', category: 'Pastry', stock: 3, image: 'https://images.unsplash.com/photo-1509446639701-edb004beb7eb?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60' },
  { id: 4, name: 'Vanilla Syrup', category: 'Syrups', stock: 0, image: 'https://images.unsplash.com/photo-1603366615912-0a5d1c6b4e3b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60' },
]);

function getStatusBadgeClass(status) {
  const statusClasses = {
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Preparing': 'bg-blue-100 text-blue-800',
    'Ready': 'bg-green-100 text-green-800',
    'Completed': 'bg-gray-100 text-gray-800',
    'Cancelled': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function getStockStatusClass(stock) {
  if (stock === 0) return 'bg-red-100 text-red-800';
  if (stock <= 3) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
}

function getStockStatusLabel(stock) {
  if (stock === 0) return 'Out of Stock';
  if (stock <= 3) return 'Low Stock';
  return 'In Stock';
}
</script>
