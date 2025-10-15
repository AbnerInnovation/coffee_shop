<template>
  <div class="tables-container">
    <div class="header">
      <h2>Tables Management</h2>
      <button @click="showAddTable = true" class="btn btn-primary">
        Add New Table
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading tables...</div>

    <!-- Error State -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Tables Grid -->
    <div v-else class="tables-grid">
      <div 
        v-for="table in tables" 
        :key="table.id"
        class="table-card"
        :class="{ 'occupied': table.is_occupied }"
        @click="selectTable(table)"
      >
        <div class="table-number">Table #{{ table.number }}</div>
        <div class="table-details">
          <span>Capacity: {{ table.capacity }}</span>
          <span>Location: {{ table.location }}</span>
          <span :class="table.is_occupied ? 'status-occupied' : 'status-available'">
            {{ table.is_occupied ? 'Occupied' : 'Available' }}
          </span>
        </div>
        <div class="table-actions">
          <button 
            @click.stop="toggleOccupancy(table)"
            :class="['btn', table.is_occupied ? 'btn-success' : 'btn-warning']"
          >
            {{ table.is_occupied ? 'Mark Available' : 'Mark Occupied' }}
          </button>
          <button 
            @click.stop="editTable(table)"
            class="btn btn-secondary"
          >
            Edit
          </button>
          <button 
            @click.stop="deleteTable(table.id)"
            class="btn btn-danger"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Table Modal -->
    <div v-if="showAddTable || editingTable" class="modal-overlay">
      <div class="modal">
        <h3>{{ editingTable ? 'Edit Table' : 'Add New Table' }}</h3>
        <form @submit.prevent="editingTable ? updateTable() : addTable()">
          <div class="form-group">
            <label>Table Number</label>
            <input 
              v-model="formData.number" 
              type="number" 
              min="1" 
              required
              class="form-control"
            >
          </div>
          <div class="form-group">
            <label>Capacity</label>
            <input 
              v-model="formData.capacity" 
              type="number" 
              min="1" 
              required
              class="form-control"
            >
          </div>
          <div class="form-group">
            <label>Location</label>
            <input 
              v-model="formData.location" 
              type="text" 
              required
              class="form-control"
            >
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ editingTable ? 'Update' : 'Add' }} Table
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import tableService from '@/services/tableService';

export default defineComponent({
  name: 'TablesList',
  setup() {
    const tables = ref<Array<{
      id: number;
      number: number;
      capacity: number;
      location: string;
      is_occupied: boolean;
    }>>([]);
    
    const loading = ref(true);
    const error = ref('');
    const showAddTable = ref(false);
    const editingTable = ref<typeof tables.value[0] | null>(null);
    
    const formData = ref({
      number: 0,
      capacity: 2,
      location: '',
    });

    const fetchTables = async () => {
      try {
        loading.value = true;
        tables.value = await tableService.getTables();
        error.value = '';
      } catch (err) {
        console.error('Error fetching tables:', err);
        error.value = 'Failed to load tables. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const addTable = async () => {
      try {
        await tableService.createTable({
          number: formData.value.number,
          capacity: formData.value.capacity,
          location: formData.value.location,
          is_occupied: false,
        });
        await fetchTables();
        closeModal();
      } catch (err) {
        console.error('Error adding table:', err);
        error.value = 'Failed to add table. Please try again.';
      }
    };

    const updateTable = async () => {
      if (!editingTable.value) return;
      
      try {
        await tableService.updateTable(editingTable.value.id, {
          number: formData.value.number,
          capacity: formData.value.capacity,
          location: formData.value.location,
        });
        await fetchTables();
        closeModal();
      } catch (err) {
        console.error('Error updating table:', err);
        error.value = 'Failed to update table. Please try again.';
      }
    };

    const deleteTable = async (id: number) => {
      if (!confirm('Are you sure you want to delete this table?')) return;
      
      try {
        await tableService.deleteTable(id);
        await fetchTables();
      } catch (err) {
        console.error('Error deleting table:', err);
        error.value = 'Failed to delete table. Please try again.';
      }
    };

    const toggleOccupancy = async (table: typeof tables.value[0]) => {
      try {
        await tableService.updateTableOccupancy(table.id, !table.is_occupied);
        await fetchTables();
      } catch (err) {
        console.error('Error updating table occupancy:', err);
        error.value = 'Failed to update table status. Please try again.';
      }
    };

    const selectTable = (table: typeof tables.value[0]) => {
      // Handle table selection (e.g., show orders for this table)
    };

    const editTable = (table: typeof tables.value[0]) => {
      editingTable.value = table;
      formData.value = {
        number: table.number,
        capacity: table.capacity,
        location: table.location,
      };
    };

    const closeModal = () => {
      showAddTable.value = false;
      editingTable.value = null;
      formData.value = {
        number: 0,
        capacity: 2,
        location: '',
      };
    };

    onMounted(() => {
      fetchTables();
    });

    return {
      tables,
      loading,
      error,
      showAddTable,
      editingTable,
      formData,
      addTable,
      updateTable,
      deleteTable,
      toggleOccupancy,
      selectTable,
      editTable,
      closeModal,
    };
  },
});
</script>

<style scoped>
.tables-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.table-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fff;
}

.table-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.table-card.occupied {
  border-left: 4px solid #dc3545;
}

.table-card:not(.occupied) {
  border-left: 4px solid #28a745;
}

.table-number {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.table-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 15px;
  color: #555;
}

.status-available {
  color: #28a745;
  font-weight: bold;
}

.status-occupied {
  color: #dc3545;
  font-weight: bold;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  font-size: 1.1rem;
}

.error {
  color: #dc3545;
}
</style>
