<template>
  <TransitionRoot as="div" :show="open" class="fixed inset-0 z-[10001]">
    <Dialog as="div" class="relative z-[10001] h-full" @close="$emit('close')">
      <TransitionChild as="div" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="div" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden bg-white mt-10 dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-20 w-screen max-w-screen sm:max-w-4xl sm:w-full sm:p-6 mx-0 sm:mx-0 rounded-none sm:rounded-lg border border-gray-200 dark:border-gray-800">
              <div class="flex items-center justify-between">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                  {{ isEditMode ? $t('app.views.orders.modals.new_order.title_edit_order', { id: orderToEdit?.id }) : $t('app.views.orders.modals.new_order.title') }}
                </DialogTitle>
                <button type="button"
                  class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="$emit('close')">
                  <span class="sr-only">{{$t('app.views.orders.modals.new_order.close')}}</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              <div class="mt-6 grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2">
                <!-- Left Column: Order Details -->
                <div class="space-y-3 sm:space-y-4">
                  <div>
                    <label for="order-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{$t('app.views.orders.modals.new_order.order_type')}}</label>
                    <select id="order-type" v-model="form.type"
                      class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm">
                      <option value="Dine-in">{{$t('app.views.orders.modals.new_order.dine_in')}}</option>
                      <option value="Takeaway">{{$t('app.views.orders.modals.new_order.takeaway')}}</option>
                      <option value="Delivery">{{$t('app.views.orders.modals.new_order.delivery')}}</option>
                    </select>
                  </div>

                  <div v-if="form.type === 'Dine-in'">
                    <label for="table" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{$t('app.views.orders.modals.new_order.table')}}</label>
                    <select id="table" v-model="form.tableId"
                      class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                      :disabled="loading.tables">
                      <option v-if="loading.tables" value="" disabled>{{$t('app.views.orders.modals.new_order.loading_tables')}}</option>
                      <option v-else-if="error.tables" value="" disabled>{{$t('app.views.orders.modals.new_order.error_tables')}}</option>
                      <option v-else-if="availableTables.length === 0" value="" disabled>{{$t('app.views.orders.modals.new_order.no_tables')}}</option>
                      <option v-else v-for="table in availableTables" :key="table.id" :value="table.id">
                        {{$t('app.views.orders.modals.new_order.table_option', { number: table.number, capacity: table.capacity })}}
                      </option>
                    </select>
                  </div>

                  <div v-else>
                    <label for="customer-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {{ form.type === 'Delivery' ? $t('app.views.orders.modals.new_order.delivery_address') : $t('app.views.orders.modals.new_order.customer_name') }}
                    </label>
                    <input id="customer-name" v-model="form.customerName" type="text"
                      class="mt-1 p-3 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      :placeholder="form.type === 'Delivery' ? $t('app.views.orders.modals.new_order.enter_delivery_address') : $t('app.views.orders.modals.new_order.enter_customer_name')" />
                  </div>

                  <div>
                    <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{$t('app.views.orders.modals.new_order.order_notes')}}</label>
                    <textarea id="notes" v-model="form.notes" rows="3"
                      class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      :placeholder="$t('app.views.orders.modals.new_order.notes_placeholder')" />
                  </div>
                </div>

                <!-- Right Column: Menu Items -->
                <div class="space-y-3 sm:space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{$t('app.views.orders.modals.new_order.menu_items')}}</label>
                    <div v-if="loading.menu" class="text-center py-4">
                      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.new_order.loading_menu')}}</p>
                    </div>
                    <div v-else-if="error.menu" class="text-center py-4 text-red-600">
                      <p>{{$t('app.views.orders.modals.new_order.error_menu')}}</p>
                    </div>
                    <div v-else class="space-y-3 max-h-[50vh] sm:max-h-none overflow-y-auto pr-1 -mr-1 sm:mr-0">
                      <!-- Category sections -->
                      <div v-for="category in categoryNames" :key="category" class="border-b border-gray-200 dark:border-gray-700 pb-3 mb-3 last:border-b-0 last:pb-0 last:mb-0">
                        <!-- Category Header -->
                        <button
                          @click="toggleCategory(category)"
                          class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors"
                          :class="{ 'bg-indigo-50 dark:bg-indigo-900/20': isCategoryExpanded(category) }"
                        >
                          <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {{ category }}
                            <span class="text-xs text-gray-500 ml-2">({{ menuItemsByCategory[category].length }})</span>
                          </h3>
                          <ChevronDownIcon
                            class="h-4 w-4 text-gray-500 transition-transform"
                            :class="{ 'rotate-180': !isCategoryExpanded(category) }"
                          />
                        </button>

                        <!-- Category Items -->
                        <div v-if="isCategoryExpanded(category)" class="mt-2 space-y-2 pl-2">
                          <div v-for="item in menuItemsByCategory[category]" :key="item.id"
                            class="flex items-center justify-between p-2 border rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                            @click="() => selectItem(item)">
                            <div class="flex-1 min-w-0">
                              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                {{ item.name }}
                                <span v-if="item.has_variants" class="text-xs text-gray-500 ml-1">{{$t('app.views.orders.modals.new_order.select_options_hint')}}</span>
                              </h4>
                              <div class="flex items-center gap-2">
                                <p 
                                  v-if="item.discount_price && item.discount_price > 0"
                                  class="text-sm text-gray-500 dark:text-gray-400 line-through"
                                >
                                  ${{ (item.price || 0).toFixed(2) }}
                                </p>
                                <p 
                                  class="text-sm font-medium"
                                  :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
                                >
                                  ${{ getEffectivePrice(item.price || 0, item.discount_price).toFixed(2) }}
                                </p>
                                <span 
                                  v-if="item.discount_price && item.discount_price > 0"
                                  class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200"
                                >
                                  {{ $t('app.forms.sale_badge') }}
                                </span>
                              </div>
                            </div>
                            <div class="flex items-center space-x-2">
                              <span class="text-sm text-gray-900 dark:text-gray-200">
                                {{ getItemQuantity(item.id) > 0 ? $t('app.views.orders.modals.new_order.in_order', { count: getItemQuantity(item.id) }) : $t('app.views.orders.modals.new_order.add') }}
                              </span>
                              <button type="button"
                                class="p-1 rounded-full text-indigo-600 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                @click.stop="selectItem(item)">
                                <PlusIcon class="h-5 w-5" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Selected Item Options -->
                <div class="mt-4 border-t border-gray-200 pt-4">
                  <div v-if="selectedItem">
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                      {{ selectedItem.name }}
                    </h4>

                    <!-- Variants / Options -->
                    <div v-if="selectedItem.variants?.length" class="space-y-2 mb-4">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{$t('app.views.orders.modals.new_order.options')}}</label>
                      <!-- Base item option when base price > 0 -->
                      <div v-if="(selectedItem.price || 0) > 0"
                        class="flex items-center p-2 border rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                        :class="{ 'bg-indigo-50 dark:bg-indigo-900 border-indigo-200 dark:border-indigo-600': !selectedVariant }"
                        @click="selectedVariant = null">
                        <div class="flex-1">
                          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{$t('app.views.orders.modals.new_order.base_item') || 'Base item'}}</p>
                          <div class="flex items-center gap-2">
                            <p v-if="selectedItem.discount_price && selectedItem.discount_price > 0" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                              ${{ (selectedItem.price || 0).toFixed(2) }}
                            </p>
                            <p class="text-sm font-medium" :class="selectedItem.discount_price && selectedItem.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                              ${{ getEffectivePrice(selectedItem.price || 0, selectedItem.discount_price).toFixed(2) }}
                            </p>
                            <span v-if="selectedItem.discount_price && selectedItem.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                              {{ $t('app.forms.sale_badge') }}
                            </span>
                          </div>
                        </div>
                        <div class="ml-2 flex items-center">
                          <input type="radio" :checked="!selectedVariant"
                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-700">
                        </div>
                      </div>
                      <!-- Variant options -->
                      <div v-for="variant in selectedItem.variants" :key="variant.id"
                        class="flex items-center p-2 border rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                        :class="{ 'bg-indigo-50 dark:bg-indigo-900 border-indigo-200 dark:border-indigo-600': selectedVariant?.id === variant.id }"
                        @click="selectedVariant = variant">
                        <div class="flex-1">
                          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ variant.name }}</p>
                          <div class="flex items-center gap-2">
                            <p v-if="variant.discount_price && variant.discount_price > 0" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                              ${{ variant.price.toFixed(2) }}
                            </p>
                            <p class="text-sm font-medium" :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                              ${{ getVariantPrice(selectedItem, variant).toFixed(2) }}
                            </p>
                            <span v-if="variant.discount_price && variant.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                              {{ $t('app.forms.sale_badge') }}
                            </span>
                          </div>
                        </div>
                        <div class="ml-2 flex items-center">
                          <input type="radio" :checked="selectedVariant?.id === variant.id"
                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-700">
                        </div>
                      </div>
                    </div>

                    <!-- Special Notes Builder -->
                    <div class="mt-4">
                      <SpecialNotesBuilder
                        v-if="selectedItem"
                        :ingredients="(selectedItem as any).ingredients || null"
                        v-model="itemSpecialNote"
                        :top-notes="topNotes"
                      />
                    </div>

                    <!-- Additional Notes (fallback) -->
                    <div v-if="!selectedItem || !(selectedItem as any).ingredients" class="mt-4">
                      <label for="item-notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{$t('app.views.orders.modals.new_order.special_instructions')}}</label>
                      <textarea id="item-notes" v-model="itemNotes" rows="2"
                        class="w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        :placeholder="$t('app.views.orders.modals.new_order.special_requests_placeholder')" />
                    </div>

                    <!-- Add to Order Button -->
                    <div class="mt-4 flex justify-end space-x-2">
                      <button type="button" class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-500 dark:hover:text-gray-300"
                        @click="selectedItem = null">
                        {{$t('app.views.orders.modals.new_order.cancel')}}
                      </button>
                      <button type="button"
                        class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        @click="addItemWithDetails">
                        {{$t('app.views.orders.modals.new_order.add_to_order')}}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Order Summary -->
                <div class="mt-6 border-t border-gray-200 pt-4">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">{{$t('app.views.orders.modals.new_order.order_summary')}}</h4>
                  <div class="space-y-3">
                    <div v-for="item in selectedItems" :key="item.id" class="flex justify-between items-start">
                      <div class="flex-1">
                        <div class="flex items-center gap-2">
                          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {{ item.name }}
                            <span v-if="item.variant_name" class="text-xs text-gray-500 ml-1">({{ item.variant_name }})</span>
                          </p>
                          <!-- Status badge for items in preparation or ready -->
                          <span v-if="isItemLocked(item)" 
                            class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                            :class="{
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200': item.status === 'preparing',
                              'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200': item.status === 'ready'
                            }">
                            {{ t(`app.status.${item.status}`) }}
                          </span>
                        </div>
                        <div v-if="item.category" class="mt-1">
                          <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                            {{ item.category }}
                          </span>
                        </div>
                        <p v-if="item.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ item.notes }}</p>
                        <p v-if="isItemLocked(item)" class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                          {{ t('app.views.orders.modals.new_order.item_locked') }}
                        </p>
                      </div>
                      <div class="flex items-center space-x-4 ml-4">
                        <div class="flex items-center space-x-2">
                          <button type="button" 
                            class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
                            :disabled="isItemLocked(item)"
                            @click.stop="decreaseQuantity(item)">
                            <MinusIcon class="h-4 w-4" />
                          </button>
                          <span class="text-sm text-gray-700 dark:text-gray-200 w-6 text-center">{{ item.quantity }}</span>
                          <button type="button" 
                            class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
                            :disabled="isItemLocked(item)"
                            @click.stop="increaseQuantity(item)">
                            <PlusIcon class="h-4 w-4" />
                          </button>
                        </div>
                        <span class="text-sm font-medium text-gray-900 dark:text-gray-100 w-16 text-right">
                          ${{ calculateItemTotal(item) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="mt-4 pt-4 border-t border-gray-200">
                    <div class="flex justify-between items-center">
                      <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{$t('app.views.orders.modals.new_order.total')}}</span>
                      <span class="text-lg font-bold text-gray-900 dark:text-white">
                        ${{(selectedItems.reduce((sum, item) => sum + (parseFloat(calculateItemTotal(item)) || 0),
                          0)).toFixed(2)}}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-5 sm:mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button type="button"
                  class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-3 sm:py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700"
                  @click="$emit('close')">
                  {{$t('app.views.orders.modals.new_order.cancel')}}
                </button>
                <button type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-3 sm:py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="selectedItems.length === 0 || (form.type === 'Dine-in' && !form.tableId) || (form.type !== 'Dine-in' && !form.customerName)"
                  @click="createOrder">
                  {{isEditMode ? $t('app.views.orders.modals.new_order.update_order') : $t('app.views.orders.modals.new_order.create_order')}}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>

    <!-- Item Selection Modal -->
    <TransitionRoot as="div" :show="showItemModal" class="fixed inset-0 z-[10002]">
      <Dialog as="div" class="relative z-[10002] h-full" @close="showItemModal = false">
        <TransitionChild as="div" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild as="div" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" class="w-full">
              <DialogPanel
                class="relative transform overflow-hidden bg-white dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 w-screen max-w-screen sm:w-full sm:max-w-md sm:p-6 rounded-none sm:rounded-lg border border-gray-200 dark:border-gray-800">
                <div>
                  <div class="mt-3 text-center sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                      {{ selectedItem?.name }}
                    </DialogTitle>
                    <div class="mt-4">
                      <p class="text-sm text-gray-500 dark:text-gray-400">{{ selectedItem?.description }}</p>

                      <!-- Variant Selection -->
                      <div v-if="selectedItem?.variants?.length" class="mt-4">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{$t('app.views.orders.modals.new_order.variants')}}</label>
                        <div class="space-y-2">
                          <!-- Base item option when base price > 0 -->
                          <div v-if="(selectedItem?.price || 0) > 0"
                            class="flex items-center p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                            :class="{ 'bg-indigo-50 border-indigo-500': !selectedVariant }"
                            @click="selectedVariant = null">
                            <div class="flex-1">
                              <div class="flex justify-between items-center">
                                <span class="font-medium">{{$t('app.views.orders.modals.new_order.base_item') || 'Base item'}}</span>
                                <div class="flex items-center gap-2">
                                  <span v-if="selectedItem?.discount_price && selectedItem.discount_price > 0" class="text-gray-500 line-through text-sm">
                                    ${{ (selectedItem?.price || 0).toFixed(2) }}
                                  </span>
                                  <span class="font-medium" :class="selectedItem?.discount_price && selectedItem.discount_price > 0 ? 'text-green-600' : 'text-gray-600'">
                                    ${{ getEffectivePrice(selectedItem?.price || 0, selectedItem?.discount_price).toFixed(2) }}
                                  </span>
                                  <span v-if="selectedItem?.discount_price && selectedItem.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800">
                                    {{ $t('app.forms.sale_badge') }}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                          <!-- Variant options -->
                          <div v-for="variant in selectedItem.variants" :key="variant.id"
                            class="flex items-center p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                            :class="{ 'bg-indigo-50 border-indigo-500': selectedVariant?.id === variant.id }"
                            @click="selectedVariant = variant">
                            <div class="flex-1">
                              <div class="flex justify-between items-center">
                                <span class="font-medium">{{ variant.name }}</span>
                                <div class="flex items-center gap-2">
                                  <span v-if="variant.discount_price && variant.discount_price > 0" class="text-gray-500 line-through text-sm">
                                    ${{ variant.price.toFixed(2) }}
                                  </span>
                                  <span class="font-medium" :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600' : 'text-gray-600'">
                                    ${{ getVariantPrice(selectedItem, variant).toFixed(2) }}
                                  </span>
                                  <span v-if="variant.discount_price && variant.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800">
                                    {{ $t('app.forms.sale_badge') }}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Special Instructions -->
                      <div class="mt-4">
                        <label for="item-notes" class="block text-sm font-medium text-gray-700 mb-1">
                          {{$t('app.views.orders.modals.new_order.special_instructions')}}
                        </label>
                        <textarea id="item-notes" v-model="itemNotes" rows="2"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          :placeholder="$t('app.views.orders.modals.new_order.item_description_placeholder')" />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="showItemModal = false">
                    {{$t('app.views.orders.modals.new_order.cancel')}}
                  </button>
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="addItemWithDetails">
                    {{$t('app.views.orders.modals.new_order.add_to_order')}}
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineExpose, nextTick, watch } from 'vue';
import orderService, { type CreateOrderData, type OrderItem, type Order as OrderType } from '@/services/orderService';
import menuService from '@/services/menuService';
import tableService from '@/services/tableService';
import specialNotesService from '@/services/specialNotesService';
import { useToast } from '@/composables/useToast';
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot
} from '@headlessui/vue';
import { XMarkIcon, PlusIcon, MinusIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import SpecialNotesBuilder from './SpecialNotesBuilder.vue';
import type { MenuItemIngredients } from '../menu/IngredientsManager.vue';

// Import types
import type { MenuItem as MenuItemType } from '@/types/menu';

// Local interfaces
interface MenuItemVariant {
  id: string | number;
  name: string;
  price: number;
  discount_price?: number;
  price_adjustment: number;
  is_available: boolean;
  is_default: boolean;
  menu_item_id: string | number;
  created_at?: string;
  updated_at?: string;
  // No index signature to avoid conflicts with other properties
  [key: string]: unknown;
}

interface ExtendedMenuItem extends Omit<MenuItemType, 'variants' | 'id' | 'price'> {
  id: number;
  has_variants: boolean;
  variants?: MenuItemVariant[];
  price: number;
  discount_price?: number;
  category?: { name: string } | string;
  ingredients?: MenuItemIngredients | null;
}

interface OrderItemWithDetails {
  id: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  category?: string;
  price: number;
  quantity: number;
  notes?: string;
  special_instructions?: string;
  unit_price?: number;
}

// Props and Emits
const props = defineProps<{
  open: boolean;
  tableId?: number | null;
  mode?: 'create' | 'edit';
  orderToEdit?: OrderType | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'order-created', order: any): void;
  (e: 'order-updated', order: any): void;
}>();

// Form data
const form = ref({
  type: 'Dine-in',
  tableId: null as number | string | null,
  customerName: '',
  notes: '',
  items: [] as Array<{
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
  }>
});

const selectedItem = ref<ExtendedMenuItem | null>(null);
const selectedVariant = ref<MenuItemVariant | null>(null);
const itemNotes = ref('');
const itemSpecialNote = ref('');
const topNotes = ref<string[]>([]);
const showItemModal = ref(false);
const isEditMode = computed(() => { 
  return (props.mode || 'create') === 'edit' && !!props.orderToEdit});

const { showError, showSuccess, showToast } = useToast();
const { t } = useI18n();
const menuItems = ref<ExtendedMenuItem[]>([]);
const availableTables = ref<any[]>([]);
const loading = ref({
  menu: false,
  tables: false
});

const error = ref({
  menu: null as string | null,
  tables: null as string | null
});

const expandedCategories = ref<Set<string>>(new Set());

// Helper to initialize a fresh form state
function getInitialForm() {
  return {
    type: 'Dine-in',
    tableId: null as number | string | null,
    customerName: '',
    notes: '',
    items: [] as Array<{
      menu_item_id: number;
      variant_id?: number | null;
      quantity: number;
      notes?: string;
      special_instructions?: string;
      unit_price?: number;
    }>
  };
}

// Reset all local state of the modal
function resetForm() {
  // Reset base fields
  form.value = getInitialForm();
  selectedItem.value = null;
  selectedVariant.value = null;
  itemNotes.value = '';
  showItemModal.value = false;

  // Rebuild zero-quantity items list from current menu cache if available
  if (menuItems.value.length > 0) {
    form.value.items = menuItems.value.map(item => ({
      menu_item_id: Number(item.id),
      variant_id: null,
      quantity: 0,
      notes: '',
      special_instructions: '',
      unit_price: item.price
    }));
  }
}

// Group menu items by category
const menuItemsByCategory = computed(() => {
  const groups: Record<string, ExtendedMenuItem[]> = {};
  menuItems.value.forEach(item => {
    const categoryName = (item.category && typeof item.category === 'object' && item.category.name) ? item.category.name : 'Uncategorized';
    if (!groups[categoryName]) {
      groups[categoryName] = [];
    }
    groups[categoryName].push(item);
  });
  return groups;
});

// Get sorted category names
const categoryNames = computed(() => {
  return Object.keys(menuItemsByCategory.value).sort();
});

// Toggle category expansion
function toggleCategory(category: string) {
  if (expandedCategories.value.has(category)) {
    expandedCategories.value.delete(category);
  } else {
    expandedCategories.value.add(category);
  }
}

// Check if category is expanded
function isCategoryExpanded(category: string): boolean {
  return expandedCategories.value.has(category);
}

// Expand all categories initially
function expandAllCategories() {
  expandedCategories.value = new Set(categoryNames.value);
}

// Collapse all categories
function collapseAllCategories() {
  expandedCategories.value.clear();
}
const fetchMenuItems = async () => {
  try {
    loading.value.menu = true;
    const response = await menuService.getMenuItems();

    menuItems.value = response.map((item: any) => {
      // Process variants with proper typing and defaults
      const variants: MenuItemVariant[] = (item.variants || []).map((variant: any) => {
        // Create a new object with all required fields
        const variantData: MenuItemVariant = {
          id: variant.id || 0,
          name: variant.name || '',
          price: typeof variant.price === 'string' ? parseFloat(variant.price) : (variant.price || 0),
          discount_price: variant.discount_price ? (typeof variant.discount_price === 'string' ? parseFloat(variant.discount_price) : variant.discount_price) : undefined,
          price_adjustment: 'price_adjustment' in variant ? Number(variant.price_adjustment) || 0 : 0,
          is_available: 'is_available' in variant ? Boolean(variant.is_available) : true,
          is_default: 'is_default' in variant ? Boolean(variant.is_default) : false,
          menu_item_id: variant.menu_item_id || item.id || 0,
          // Include any additional properties from the original variant
          ...variant
        };
        return variantData;
      });

      // Process the main menu item with proper type safety
      const menuItem: ExtendedMenuItem = {
        id: Number(item.id) || 0,
        name: item.name || '',
        description: item.description || '',
        price: typeof item.price === 'string' ? parseFloat(item.price) : (item.price || 0),
        discount_price: item.discount_price ? (typeof item.discount_price === 'string' ? parseFloat(item.discount_price) : item.discount_price) : undefined,
        category: item.category || { name: 'Uncategorized' },
        is_available: item.is_available !== false,
        has_variants: variants.length > 0,
        variants: variants.length > 0 ? variants : undefined,
        ingredients: item.ingredients || null
      };

      return menuItem;
    });

    // Auto-expand all categories after loading menu items
    collapseAllCategories();
  } catch (err) {
    console.error('Error fetching menu items:', err);
    error.value.menu = t('app.views.orders.modals.new_order.error_menu');
    showError(t('app.views.orders.modals.new_order.error_menu'));
  } finally {
    loading.value.menu = false;
  }
};

// Fetch available tables
const fetchAvailableTables = async () => {
  try {
    loading.value.tables = true;
    const tables = await tableService.getTables();
    availableTables.value = tables.map(table => ({
      id: table.id,
      number: table.number.toString().padStart(2, '0'),
      capacity: table.capacity,
      status: table.is_occupied ? 'Occupied' : 'Available'
    }));
    // After fetching the list, if opened from a table card, select that table by default
    if (props.tableId) {
      form.value.type = 'Dine-in';
      form.value.tableId = props.tableId;
    }
  } catch (err) {
    console.error('Error fetching tables:', err);
    error.value.tables = t('app.views.orders.modals.new_order.error_tables');
    showError(t('app.views.orders.modals.new_order.error_tables'));
  } finally {
    loading.value.tables = false;
  }
};

// Hydrate form from existing order in edit mode
function loadOrderIntoForm(order: OrderType) {
  console.log('🔄 Loading order into form:', order);
  
  // Set order type
  form.value.type = order.table_id ? 'Dine-in' : 'Takeaway';
  form.value.tableId = order.table_id ?? null;
  form.value.customerName = order.customer_name || '';
  form.value.notes = order.notes || '';
  
  // Build items list
  form.value.items = (order.items || []).map((it) => ({
    menu_item_id: it.menu_item_id,
    variant_id: it.variant_id ?? null,
    quantity: it.quantity,
    notes: it.special_instructions || undefined,
    special_instructions: it.special_instructions || undefined,
    unit_price: it.unit_price || it.menu_item?.price || 0,
    status: it.status || 'pending', // Guardar el status del item
  }));
  
  console.log('✅ Form loaded with items:', form.value.items.length, 'items');
  console.log('📋 Form state:', {
    type: form.value.type,
    tableId: form.value.tableId,
    notes: form.value.notes,
    itemsCount: form.value.items.length
  });
}

// Computed properties
const selectedItems = computed<OrderItemWithDetails[]>(() => {
  return form.value.items
    .filter(item => item.quantity > 0)
    .map(item => {
      const menuItem = menuItems.value.find(mi => Number(mi.id) === Number(item.menu_item_id));
      const variant = menuItem?.variants?.find(v => Number(v.id) === Number(item.variant_id));
      const basePrice = typeof menuItem?.price === 'string' ? parseFloat(menuItem.price) : (menuItem?.price || 0);
      const adjustment = variant?.price_adjustment || 0;
      const price = variant ? basePrice + adjustment : basePrice;

      const categoryName = menuItem?.category && typeof menuItem.category === 'object' && menuItem.category.name
        ? menuItem.category.name
        : typeof menuItem?.category === 'string'
        ? menuItem.category
        : undefined;

      return {
        id: Number(item.menu_item_id) * 1000 + (item.variant_id ? Number(item.variant_id) : 0), // Generate a unique ID
        menu_item_id: Number(item.menu_item_id),
        variant_id: item.variant_id ? Number(item.variant_id) : null,
        name: menuItem?.name || 'Unknown Item',
        variant_name: variant?.name,
        category: categoryName,
        price,
        quantity: item.quantity,
        notes: item.notes,
        special_instructions: item.special_instructions,
        unit_price: item.unit_price
      };
    });
});

// Calculate item total with proper type safety and null checks
const calculateItemTotal = (item: OrderItemWithDetails) => {
  const price = item.unit_price !== undefined && item.unit_price !== null ?
    (typeof item.unit_price === 'string' ? parseFloat(item.unit_price) : item.unit_price) :
    (item.price !== undefined && item.price !== null ?
      (typeof item.price === 'string' ? parseFloat(item.price) : item.price) : 0);
  return (price * (item.quantity || 0)).toFixed(2);
};

// Add item with variant and notes
function addItemWithDetails() {
  if (!selectedItem.value) return;

  const variant = selectedVariant.value as MenuItemVariant | null;
  
  // Determine the correct unit price: prefer variant.price if present
  const itemPrice = getVariantPrice(selectedItem.value, variant);

  // Ensure we have valid IDs
  const menuItemId = Number(selectedItem.value.id || 0);
  const variantId = variant ? Number(variant.id) : null;

  // Find existing item with the same menu item and variant
  const existingItemIndex = form.value.items.findIndex(item => {
    const sameMenuItem = item.menu_item_id === menuItemId;
    const sameVariant = variantId !== null ?
      item.variant_id === variantId :
      item.variant_id === null || item.variant_id === undefined;
    return sameMenuItem && sameVariant;
  });

  // Use itemSpecialNote if available, otherwise fallback to itemNotes
  const finalNote = itemSpecialNote.value || itemNotes.value;

  if (existingItemIndex !== -1) {
    // Update existing item
    const existingItem = form.value.items[existingItemIndex];
    existingItem.quantity += 1;
    existingItem.unit_price = itemPrice; // Update the unit_price in case discount changed
    if (finalNote) {
      existingItem.notes = finalNote;
    }
  } else {
    // Add new item
    form.value.items.push({
      menu_item_id: menuItemId,
      variant_id: variantId,
      quantity: 1,
      unit_price: itemPrice,
      notes: finalNote || '',
      special_instructions: ''
    });
  }

  // Reset the form
  showItemModal.value = false;
  itemNotes.value = '';
  itemSpecialNote.value = '';
}

function increaseQuantity(item: OrderItemWithDetails) {
  const existingItem = form.value.items.find(i =>
    i.menu_item_id === item.menu_item_id &&
    ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
  );

  if (existingItem) {
    existingItem.quantity += 1;
  }
}

function decreaseQuantity(item: OrderItemWithDetails) {
  const existingItemIndex = form.value.items.findIndex(i =>
    i.menu_item_id === item.menu_item_id &&
    ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
  );

  if (existingItemIndex !== -1) {
    const existingItem = form.value.items[existingItemIndex];
    if (existingItem.quantity > 1) {
      existingItem.quantity -= 1;
    } else {
      form.value.items.splice(existingItemIndex, 1);
    }
  }
}

function getItemQuantity(menuItemId: number | string, variantId?: number | string | null): number {
  const item = form.value.items.find(item => {
    const matchesMenuItem = Number(item.menu_item_id) === Number(menuItemId);
    const matchesVariant = variantId !== undefined ?
      Number(item.variant_id) === Number(variantId) :
      !item.variant_id;
    return matchesMenuItem && matchesVariant;
  });
  return item ? item.quantity : 0;
}

async function createOrder() {
  try {
    // Filter out items with zero quantity before creating the order
    const validItems = form.value.items.filter(item => item.quantity > 0);

    if (validItems.length === 0) {
      showError(t('app.views.orders.modals.new_order.errors.add_one_item'));
      return;
    }

    if (isEditMode.value && props.orderToEdit) {
      const orderId = props.orderToEdit.id;

      // 1) Update order-level fields (notes, table_id) if changed
      const updates: any = {};
      const newTableId = form.value.type === 'Dine-in' ? (form.value.tableId as number | null) : null;
      if (newTableId !== props.orderToEdit.table_id) updates.table_id = newTableId;
      if (form.value.notes !== (props.orderToEdit.notes || '')) updates.notes = form.value.notes || null;
      if (Object.keys(updates).length > 0) {
        await orderService.updateOrder(orderId, updates);
      }

      // Build a lookup for existing items by composite key menu_item_id|variant_id
      const existingMap = new Map<string, OrderItem>();
      for (const it of props.orderToEdit.items) {
        const key = `${it.menu_item_id}|${it.variant_id ?? ''}`;
        existingMap.set(key, it);
      }

      // Track which existing items remain to detect deletions
      const seenExistingKeys = new Set<string>();

      // Upserts: update existing items or add new ones
      for (const item of validItems) {
        const key = `${item.menu_item_id}|${item.variant_id ?? ''}`;
        const existing = existingMap.get(key);
        if (existing) {
          const patch: any = {};
          if (existing.quantity !== item.quantity) patch.quantity = item.quantity;
          const desiredUnitPrice = item.unit_price ?? existing.unit_price ?? 0;
          if ((existing.unit_price ?? 0) !== desiredUnitPrice) patch.unit_price = desiredUnitPrice;
          const si = item.notes ?? null;
          if ((existing.special_instructions ?? null) !== si) patch.special_instructions = si;
          const desiredVariantId = item.variant_id ?? null;
          if ((existing.variant_id ?? null) !== desiredVariantId) patch.variant_id = desiredVariantId;
          if (Object.keys(patch).length > 0) {
            await orderService.updateOrderItem(orderId, existing.id, patch);
          }
          seenExistingKeys.add(key);
        } else {
          await orderService.addOrderItem(orderId, {
            menu_item_id: item.menu_item_id,
            variant_id: item.variant_id ?? null,
            quantity: item.quantity,
            special_instructions: item.notes ?? null,
            unit_price: item.unit_price ?? 0,
          });
        }
      }

      // Deletions: remove items no longer present in the form
      for (const [key, ex] of existingMap.entries()) {
        if (!validItems.some(it => `${it.menu_item_id}|${(it.variant_id ?? '')}` === key)) {
          await orderService.deleteOrderItem(orderId, ex.id);
        }
      }

      // Emit updated order and close
      const updated = await orderService.getOrder(orderId);
      emit('order-updated', updated);
      emit('close');
    } else {
      // Create mode
      // Validate required fields depending on order type
      if (form.value.type === 'Dine-in' && !form.value.tableId) {
        showError(t('app.views.orders.modals.new_order.error_tables'));
        return;
      }
      if (form.value.type !== 'Dine-in' && !form.value.customerName) {
        showError(t('app.views.orders.modals.new_order.errors.add_one_item'));
        return;
      }

      const orderPayload: CreateOrderData = {
        table_id: form.value.type === 'Dine-in' ? (form.value.tableId as number | null) : null,
        customer_name: form.value.type !== 'Dine-in' ? (form.value.customerName || null) : null,
        notes: form.value.notes || null,
        items: validItems.map(it => ({
          menu_item_id: Number(it.menu_item_id),
          variant_id: it.variant_id ? Number(it.variant_id) : null,
          quantity: it.quantity,
          special_instructions: it.notes ?? null,
          unit_price: it.unit_price ?? 0,
        })),
      };

      const created = await orderService.createOrder(orderPayload);
      
      // Record special note usage for analytics (non-blocking)
      validItems.forEach(item => {
        if (item.notes) {
          specialNotesService.recordSpecialNoteUsage(item.notes).catch(err => {
            console.error('Failed to record note usage:', err);
          });
        }
      });
      
      emit('order-created', created);
      emit('close');
      showSuccess(t('app.views.orders.messages.order_created_success') as string);
    }
  } catch (error) {
    console.error('Error creating order:', error);
    showError(t('app.views.orders.modals.new_order.errors.create_failed'));
  }
}

async function selectItem(menuItem: ExtendedMenuItem) {
  selectedItem.value = { ...menuItem };
  // If the base item has a price > 0, allow selecting the base without a variant by default.
  if ((menuItem.price || 0) > 0) {
    selectedVariant.value = null;
  } else if (Array.isArray(menuItem.variants) && menuItem.variants.length > 0) {
    // For items with no base price (e.g., only variant-priced items), preselect the first variant.
    selectedVariant.value = menuItem.variants[0] || null;
  } else {
    // If the item has no variants and no base price, do not preselect anything.
    selectedVariant.value = null;
  }
  itemNotes.value = '';
  itemSpecialNote.value = '';

  // Scroll to the bottom to show the options after the next DOM update
  await nextTick();
  const modal = document.querySelector('.fixed.inset-0.overflow-y-auto');
  if (modal) {
    modal.scrollTo({
      top: modal.scrollHeight,
      behavior: 'smooth'
    });
  }
}

// Define public API type
type PublicApi = {
  selectItem: (menuItem: ExtendedMenuItem) => void;
  addItemWithDetails: () => void;
  increaseQuantity: (item: OrderItemWithDetails) => void;
  decreaseQuantity: (item: OrderItemWithDetails) => void;
  getItemQuantity: (menuItemId: number | string, variantId?: number | string | null) => number;
  createOrder: () => Promise<void>;
  calculateItemTotal: (item: OrderItemWithDetails) => string;
};

// Create public API object with explicit type assertion
const publicApi: PublicApi = {
  selectItem,
  addItemWithDetails,
  increaseQuantity,
  decreaseQuantity,
  getItemQuantity,
  createOrder,
  calculateItemTotal
};

// Expose the public API
defineExpose(publicApi);

// Load top special notes
async function loadTopNotes() {
  try {
    const notes = await specialNotesService.getTopSpecialNotes(3);
    topNotes.value = notes.map(n => n.note_text);
  } catch (error) {
    console.error('Error loading top notes:', error);
    // Non-critical, continue without top notes
  }
}

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchMenuItems(),
    fetchAvailableTables(),
    loadTopNotes()
  ]);

  // Initialize form items after menu is loaded
  if (menuItems.value.length > 0) {
    form.value.items = menuItems.value.map(item => ({
      menu_item_id: Number(item.id),
      variant_id: null,
      quantity: 0,
      notes: '',
      special_instructions: '',
      unit_price: item.price
    }));
  }

  // If opened directly in edit mode with an order, hydrate immediately so items/totals render
  console.log('🚀 onMounted - Edit mode check:', {
    isEditMode: isEditMode.value,
    hasOrderToEdit: !!props.orderToEdit,
    mode: props.mode,
    orderId: props.orderToEdit?.id
  });
  
  if (isEditMode.value && props.orderToEdit) {
    loadOrderIntoForm(props.orderToEdit);
  }
});

// If the full order data arrives after the modal is already open, hydrate then
watch(() => props.orderToEdit, (newOrder) => {
  console.log('👀 Watch orderToEdit changed:', {
    isEditMode: isEditMode.value,
    hasOrder: !!newOrder,
    isOpen: props.open,
    orderId: newOrder?.id
  });
  
  if (isEditMode.value && newOrder && props.open) {
    loadOrderIntoForm(newOrder);
  }
});

// Keep modal state clean when toggling open prop
watch(() => props.open, (isOpen, wasOpen) => {
  if (!isOpen && wasOpen) {
    // Modal just closed -> ensure everything is reset
    resetForm();
  } else if (isOpen && !wasOpen) {
    // Modal just opened -> if items empty but menu loaded, initialize items
    if (form.value.items.length === 0 && menuItems.value.length > 0) {
      form.value.items = menuItems.value.map(item => ({
        menu_item_id: Number(item.id),
        variant_id: null,
        quantity: 0,
        notes: '',
        special_instructions: '',
        unit_price: item.price
      }));
    }
    // After tables list is already loaded, select the matching table id from the card
    if (props.tableId) {
      form.value.type = 'Dine-in';
      form.value.tableId = props.tableId;
    }
    if (isEditMode.value && props.orderToEdit) {
      loadOrderIntoForm(props.orderToEdit);
    }
  }
});

// Helper: get effective price (discount_price if set and > 0, otherwise regular price)
function getEffectivePrice(price: number, discount_price?: number): number {
  if (discount_price && discount_price > 0) {
    return discount_price;
  }
  return price;
}

// Helper: check if item is locked (cannot be edited because it's in preparation or ready)
function isItemLocked(item: OrderItemWithDetails): boolean {
  // In edit mode, items that are preparing or ready cannot be removed/modified
  if (!isEditMode.value) return false;
  
  const status = (item as any).status;
  return status === 'preparing' || status === 'ready' || status === 'delivered';
}

// Helper: compute variant price (prefer absolute variant.price; fallback to base + adjustment)
function getVariantPrice(item: ExtendedMenuItem, variant: MenuItemVariant | null): number {
  const basePrice = typeof item.price === 'string' ? parseFloat(item.price) : (item.price || 0);
  
  // If variant has an absolute price (not price_adjustment)
  if (variant && typeof (variant as any).price === 'number' && !Number.isNaN((variant as any).price)) {
    const variantPrice = (variant as any).price as number;
    // Use variant's discount_price if available
    return getEffectivePrice(variantPrice, variant.discount_price);
  }
  
  // For base item or variant with price_adjustment
  // First, get the effective base price (with discount if available)
  const effectiveBasePrice = getEffectivePrice(basePrice, item.discount_price);
  
  // Then add any variant adjustment
  const adjustment = variant?.price_adjustment || 0;
  return effectiveBasePrice + adjustment;
}

</script>
