<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ title }}
      </h2>
    </div>

    <div v-if="printers.length === 0" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
      {{ t('app.views.printers.no_printers') }}
    </div>

    <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="printer in printers"
        :key="printer.id"
        class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <h3 class="text-base font-medium text-gray-900 dark:text-white">
                {{ printer.name }}
              </h3>
              
              <!-- Status Badges -->
              <span
                v-if="printer.is_default"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200"
              >
                {{ t('app.views.printers.default') }}
              </span>
              
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  printer.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                ]"
              >
                {{ printer.is_active ? t('app.views.printers.active') : t('app.views.printers.inactive') }}
              </span>
            </div>

            <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span class="flex items-center">
                <span class="font-medium">{{ t('app.views.printers.connection') }}:</span>
                <span class="ml-1">{{ printer.connection_type }}</span>
              </span>
              
              <span v-if="printer.ip_address" class="flex items-center">
                <span class="font-medium">{{ t('app.views.printers.ip') }}:</span>
                <span class="ml-1">{{ printer.ip_address }}:{{ printer.port }}</span>
              </span>
              
              <span class="flex items-center">
                <span class="font-medium">{{ t('app.views.printers.paper') }}:</span>
                <span class="ml-1">{{ printer.paper_width }}mm</span>
              </span>
              
              <span class="flex items-center">
                <span class="font-medium">{{ t('app.views.printers.copies') }}:</span>
                <span class="ml-1">{{ printer.print_copies }}</span>
              </span>
            </div>

            <div v-if="printer.printer_type !== 'cashier' && printer.category_ids.length > 0" class="mt-2">
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ t('app.views.printers.categories') }}: {{ printer.category_ids.length }}
              </span>
            </div>
          </div>

          <!-- Actions Dropdown -->
          <div @click.stop>
            <DropdownMenu
              :id="`printer-${printer.id}`"
              button-label="Printer actions"
              width="md"
            >
              <!-- Assign Categories - Only for Kitchen and Bar printers -->
              <DropdownMenuItem
                v-if="printer.printer_type !== 'cashier'"
                :icon="TagIcon"
                variant="info"
                @click="$emit('assignCategories', printer)"
              >
                {{ t('app.views.printers.assign_categories') }}
              </DropdownMenuItem>

              <!-- Set as Default -->
              <DropdownMenuItem
                v-if="!printer.is_default"
                :icon="StarIcon"
                variant="primary"
                @click="$emit('setDefault', printer)"
              >
                {{ t('app.views.printers.set_as_default') }}
              </DropdownMenuItem>

              <!-- Toggle Active/Inactive -->
              <DropdownMenuItem
                :icon="printer.is_active ? XCircleIcon : CheckCircleIcon"
                :variant="printer.is_active ? 'warning' : 'success'"
                @click="$emit('toggleActive', printer)"
              >
                {{ printer.is_active ? t('app.views.printers.deactivate') : t('app.views.printers.activate') }}
              </DropdownMenuItem>

              <DropdownMenuDivider />

              <!-- Edit -->
              <DropdownMenuItem
                :icon="PencilIcon"
                variant="default"
                @click="$emit('edit', printer)"
              >
                {{ t('app.actions.edit') }}
              </DropdownMenuItem>

              <!-- Delete -->
              <DropdownMenuItem
                :icon="TrashIcon"
                variant="danger"
                @click="$emit('delete', printer)"
              >
                {{ t('app.actions.delete') }}
              </DropdownMenuItem>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  StarIcon,
  TagIcon
} from '@heroicons/vue/24/outline';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import type { Printer, PrinterType } from '@/services/printerService';

const { t } = useI18n();

defineProps<{
  title: string;
  printers: Printer[];
  type: PrinterType;
}>();

defineEmits<{
  edit: [printer: Printer];
  delete: [printer: Printer];
  toggleActive: [printer: Printer];
  setDefault: [printer: Printer];
  assignCategories: [printer: Printer];
}>();
</script>
