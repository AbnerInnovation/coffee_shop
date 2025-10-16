<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-[10001]" @close="closeModal">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-[10001] overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel
              class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
            >
              <div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                    {{ isEditing ? $t('app.views.tables.modal.edit_title') : $t('app.views.tables.modal.add_title') }}
                  </DialogTitle>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label for="tableNumber" class="block text-sm font-medium text-gray-700 text-left">
                        {{$t('app.views.tables.modal.fields.table_number')}}
                      </label>
                      <input
                        type="text"
                        id="tableNumber"
                        v-model="formData.number"
                        class="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        :placeholder="$t('app.views.tables.modal.fields.table_number_placeholder')"
                      />
                    </div>
                    <div>
                      <label for="capacity" class="block text-sm font-medium text-gray-700 text-left">
                        {{$t('app.views.tables.modal.fields.capacity')}}
                      </label>
                      <select
                        id="capacity"
                        v-model="formData.capacity"
                        class="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        <option v-for="n in 10" :key="n" :value="n">{{ n }} {{ n === 1 ? $t('app.views.tables.modal.fields.person') : $t('app.views.tables.modal.fields.people') }}</option>
                      </select>
                    </div>
                    <div>
                      <label for="location" class="block text-sm font-medium text-gray-700 text-left">
                        {{$t('app.views.tables.modal.fields.location_optional')}}
                      </label>
                      <input
                        type="text"
                        id="location"
                        v-model="formData.location"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        :placeholder="$t('app.views.tables.modal.fields.location_placeholder')"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2"
                  @click="saveTable"
                >
                  {{ isEditing ? $t('app.views.tables.modal.actions.submit_update') : $t('app.views.tables.modal.actions.submit_add') }}
                </button>
                <button
                  type="button"
                  class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  @click="closeModal"
                >
                  {{$t('app.views.tables.modal.actions.cancel')}}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  table: {
    type: Object,
    default: () => ({}),
  },
  isEditing: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'save']);

interface TableForm {
  id: string;
  number: string;
  capacity: number;
  location: string;
}

const formData = ref<TableForm>({
  id: '',
  number: '',
  capacity: 2,
  location: '',
});

watch(
  () => props.table as any,
  (newTable) => {
    const src = (newTable || {}) as Partial<TableForm> & Record<string, any>;
    formData.value = {
      id: typeof src.id === 'string' ? src.id : '',
      number: typeof src.number === 'string' ? src.number : '',
      capacity: typeof src.capacity === 'number' ? src.capacity : 2,
      location: typeof src.location === 'string' ? src.location : '',
    };
  },
  { immediate: true }
);

const closeModal = () => {
  emit('close');
};

const saveTable = () => {
  emit('save', { ...formData.value });
  closeModal();
};
</script>
