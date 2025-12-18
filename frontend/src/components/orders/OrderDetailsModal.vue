<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-[10001]" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div :class="backdropClasses" />
      </TransitionChild>

      <div class="fixed inset-0 z-[10001] overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-0 sm:p-4 text-center sm:items-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-none sm:rounded-lg bg-white dark:bg-gray-900 border-0 sm:border border-gray-200 dark:border-gray-800 px-4 pb-4 pt-4 sm:px-6 sm:pb-6 sm:pt-5 text-left shadow-xl transition-all w-full min-h-screen sm:min-h-0 sm:my-8 sm:max-w-2xl sm:p-6">
              <div>
                <!-- Header with close button -->
                <div class="flex items-start justify-between mb-3 sm:mb-4">
                  <DialogTitle as="h3" class="text-base sm:text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                    {{$t('app.views.orders.modals.details.order_title', { id: order.order_number || order.id })}}
                  </DialogTitle>
                  <button
                    type="button"
                    class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2 flex-shrink-0"
                    @click="$emit('close')"
                  >
                    <span class="sr-only">{{$t('app.views.orders.modals.details.close')}}</span>
                    <XMarkIcon class="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
                  </button>
                </div>

                <!-- Internal Toast Notification -->
                <Transition
                  enter-active-class="transition-all duration-300 ease-out"
                  enter-from-class="transform opacity-0 -translate-y-2"
                  enter-to-class="transform opacity-100 translate-y-0"
                  leave-active-class="transition-all duration-200 ease-in"
                  leave-from-class="transform opacity-100 translate-y-0"
                  leave-to-class="transform opacity-0 -translate-y-2"
                >
                  <div v-if="internalToast.show" class="mb-4 rounded-lg p-3 flex items-center justify-between shadow-md"
                    :class="{
                      'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800': internalToast.type === 'success',
                      'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800': internalToast.type === 'error',
                      'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800': internalToast.type === 'info',
                      'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800': internalToast.type === 'warning'
                    }"
                  >
                    <span class="text-sm font-medium"
                      :class="{
                        'text-green-800 dark:text-green-200': internalToast.type === 'success',
                        'text-red-800 dark:text-red-200': internalToast.type === 'error',
                        'text-blue-800 dark:text-blue-200': internalToast.type === 'info',
                        'text-yellow-800 dark:text-yellow-200': internalToast.type === 'warning'
                      }"
                    >
                      {{ internalToast.message }}
                    </span>
                    <button @click="internalToast.show = false" class="ml-3 flex-shrink-0"
                      :class="{
                        'text-green-600 hover:text-green-700 dark:text-green-400': internalToast.type === 'success',
                        'text-red-600 hover:text-red-700 dark:text-red-400': internalToast.type === 'error',
                        'text-blue-600 hover:text-blue-700 dark:text-blue-400': internalToast.type === 'info',
                        'text-yellow-600 hover:text-yellow-700 dark:text-yellow-400': internalToast.type === 'warning'
                      }"
                    >
                      <XMarkIcon class="h-5 w-5" />
                    </button>
                  </div>
                </Transition>
                
                <!-- Status badges -->
                <div class="flex flex-wrap gap-2 mb-4">
                  <span 
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                    :class="getStatusBadgeClass(order.status)"
                  >
                    {{ $t('app.status.' + order.status) }}
                  </span>
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                    :class="order.is_paid ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'"
                  >
                    {{ order.is_paid ? $t('app.views.orders.payment.paid') : $t('app.views.orders.payment.pending') }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.table')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ order.table_number || $t('app.views.orders.modals.details.takeaway') }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.order_time')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ formatDateTime(order.createdAt) }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.customer')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ order.customer_name || $t('app.views.orders.modals.details.no_name') }}</p>
                  </div>
                </div>
                
                <div class="mb-4">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">{{$t('app.views.orders.modals.details.order_items')}}</h4>
                  
                  <!-- If order has persons, show grouped by person -->
                  <div v-if="order.persons && order.persons.length > 0" class="space-y-4">
                    <div v-for="person in order.persons" :key="person.id" class="border-l-2 border-indigo-500 pl-3">
                      <h5 class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {{ person.name || $t('app.views.orders.modals.new_order.persons.person_label', { position: person.position }) }}
                      </h5>
                      
                      <div class="overflow-x-auto -mx-4 sm:mx-0">
                        <div class="inline-block min-w-full align-middle px-4 sm:px-0">
                          <div class="overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
                              <thead class="bg-gray-50 dark:bg-gray-800">
                                <tr>
                                  <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.item')}}</th>
                                  <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.qty')}}</th>
                                  <th scope="col" class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.price')}}</th>
                                  <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.total')}}</th>
                                </tr>
                              </thead>
                              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                                <tr v-for="item in person.items" :key="item.id">
                                  <td class="px-2 sm:px-4 py-2 sm:py-3 text-sm text-gray-900 dark:text-gray-100">
                                    <div class="font-medium text-gray-900 dark:text-gray-100 text-xs sm:text-sm">{{ item.menu_item?.name || 'Unknown' }}</div>
                                    <div v-if="item.variant" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                                      {{ item.variant.name }}
                                    </div>
                                    <div v-if="item.menu_item?.category" class="mt-1 flex items-center gap-1.5 flex-wrap">
                                      <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                                        {{ typeof item.menu_item.category === 'string' ? item.menu_item.category : item.menu_item.category.name }}
                                      </span>
                                      <!-- Kitchen visibility indicator -->
                                      <span v-if="getCategoryVisibility(item) === false" 
                                        class="inline-flex items-center gap-1 rounded-full bg-orange-100 dark:bg-orange-900/30 px-1.5 py-0.5 text-xs font-medium text-orange-700 dark:text-orange-300"
                                        :title="$t('app.views.orders.modals.details.not_visible_in_kitchen')"
                                      >
                                        <EyeSlashIcon class="h-3 w-3" />
                                        <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.not_in_kitchen')}}</span>
                                      </span>
                                      <span v-else-if="getCategoryVisibility(item) === true" 
                                        class="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-700 dark:text-green-300"
                                        :title="$t('app.views.orders.modals.details.visible_in_kitchen')"
                                      >
                                        <EyeIcon class="h-3 w-3" />
                                        <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.in_kitchen')}}</span>
                                      </span>
                                    </div>
                                    <div v-if="!isPosOnlyMode && item.special_instructions" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                      <span class="font-medium">{{$t('app.views.orders.modals.details.special_instructions')}}</span> {{ item.special_instructions }}
                                    </div>
                                    <div class="sm:hidden text-xs text-gray-500 dark:text-gray-400 mt-1">
                                      ${{ (item.unit_price || 0).toFixed(2) }} c/u
                                    </div>
                                  </td>
                                  <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right align-top">
                                    {{ item.quantity }}
                                  </td>
                                  <td class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right align-top">
                                    ${{ (item.unit_price || 0).toFixed(2) }}
                                  </td>
                                  <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 text-right align-top">
                                    ${{ ((item.unit_price || 0) * item.quantity).toFixed(2) }}
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Legacy view: show all items without grouping -->
                  <div v-else class="overflow-x-auto -mx-4 sm:mx-0">
                    <div class="inline-block min-w-full align-middle px-4 sm:px-0">
                      <div class="overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg">
                        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
                          <thead class="bg-gray-50 dark:bg-gray-800">
                            <tr>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.item')}}</th>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.qty')}}</th>
                              <th scope="col" class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.price')}}</th>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.total')}}</th>
                            </tr>
                          </thead>
                          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                            <tr v-for="item in order.items" :key="item.id">
                              <td class="px-2 sm:px-4 py-2 sm:py-3 text-sm text-gray-900 dark:text-gray-100">
                                <div class="font-medium text-gray-900 dark:text-gray-100 text-xs sm:text-sm">{{ item.name }}</div>
                                <div v-if="item.variant" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                                  {{ item.variant.name }}
                                </div>
                                <div v-if="item.menu_item?.category" class="mt-1 flex items-center gap-1.5 flex-wrap">
                                  <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                                    {{ typeof item.menu_item.category === 'string' ? item.menu_item.category : item.menu_item.category.name }}
                                  </span>
                                  <!-- Kitchen visibility indicator -->
                                  <span v-if="getCategoryVisibility(item) === false" 
                                    class="inline-flex items-center gap-1 rounded-full bg-orange-100 dark:bg-orange-900/30 px-1.5 py-0.5 text-xs font-medium text-orange-700 dark:text-orange-300"
                                    :title="$t('app.views.orders.modals.details.not_visible_in_kitchen')"
                                  >
                                    <EyeSlashIcon class="h-3 w-3" />
                                    <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.not_in_kitchen')}}</span>
                                  </span>
                                  <span v-else-if="getCategoryVisibility(item) === true" 
                                    class="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-700 dark:text-green-300"
                                    :title="$t('app.views.orders.modals.details.visible_in_kitchen')"
                                  >
                                    <EyeIcon class="h-3 w-3" />
                                    <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.in_kitchen')}}</span>
                                  </span>
                                </div>
                                <div v-if="!isPosOnlyMode && item.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  <span class="font-medium">{{$t('app.views.orders.modals.details.note')}}</span> {{ item.notes }}
                                </div>
                                <div v-if="!isPosOnlyMode && item.special_instructions" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  <span class="font-medium">{{$t('app.views.orders.modals.details.special_instructions')}}</span> {{ item.special_instructions }}
                                </div>
                                <!-- Show extras if any -->
                                <div v-if="item.extras && item.extras.length > 0" class="mt-1 space-y-0.5">
                                  <p v-for="(extra, idx) in item.extras" :key="idx" class="text-xs text-indigo-600 dark:text-indigo-400">
                                    + {{ extra.name }} ({{ extra.quantity }}x ${{ extra.price.toFixed(2) }})
                                  </p>
                                </div>
                                <!-- Show price on mobile (hidden on desktop) -->
                                <div class="sm:hidden text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  ${{ (item.unit_price || 0).toFixed(2) }} c/u
                                </div>
                              </td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right align-top">
                                {{ item.quantity }}
                              </td>
                              <td class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-right align-top">
                            <div class="flex items-center justify-end gap-2">
                              <!-- Show original price if unit_price is less than menu item price (discount was applied) -->
                              <span v-if="item.menu_item?.price && item.unit_price < item.menu_item.price" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                                ${{ (item.menu_item.price || 0).toFixed(2) }}
                              </span>
                              <span :class="item.menu_item?.price && item.unit_price < item.menu_item.price ? 'text-green-600 dark:text-green-400 font-medium' : 'text-gray-500 dark:text-gray-400'">
                                ${{ (item.unit_price || 0).toFixed(2) }}
                              </span>
                              <span v-if="item.menu_item?.price && item.unit_price < item.menu_item.price" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                                {{ $t('app.forms.sale_badge') }}
                              </span>
                            </div>
                          </td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 text-right align-top">
                                ${{ calculateItemTotal(item).toFixed(2) }}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Totals Section -->
                <div class="overflow-x-auto -mx-4 sm:mx-0">
                  <div class="inline-block min-w-full align-middle px-4 sm:px-0">
                    <div class="overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg">
                      <table class="min-w-full">
                          <tfoot>
                            <tr v-if="totalSavings > 0">
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-2 text-xs sm:text-sm text-green-600 dark:text-green-400 text-right">
                                {{$t('app.forms.total_savings')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-2 text-xs sm:text-sm font-medium text-green-600 dark:text-green-400 text-right">
                                -${{ totalSavings.toFixed(2) }}
                              </td>
                            </tr>
                            <tr>
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-1 text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100 text-right">
                                {{$t('app.views.orders.modals.details.subtotal')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-1 text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100 text-right">
                                ${{ (order.subtotal || 0).toFixed(2) }}
                              </td>
                            </tr>
                            <tr v-if="(order.tax || 0) > 0">
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-1 text-sm sm:text-base text-gray-600 dark:text-gray-300 text-right font-medium">
                                {{$t('app.views.orders.modals.details.tax', { rate: ((order.taxRate || 0) * 100).toFixed(1) })}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-1 text-sm sm:text-base text-gray-600 dark:text-gray-300 text-right font-medium">
                                ${{ (order.tax || 0).toFixed(2) }}
                              </td>
                            </tr>
                            <tr>
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-2 sm:py-3 text-base sm:text-lg font-bold text-gray-900 dark:text-white text-right">
                                {{$t('app.views.orders.modals.details.total')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 text-base sm:text-lg font-bold text-gray-900 dark:text-white text-right">
                                ${{ (order.total || 0).toFixed(2) }}
                              </td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    </div>
                  </div>
                
                <div v-if="order.notes" class="mb-4">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{{$t('app.views.orders.modals.details.order_notes')}}</h4>
                  <p class="text-sm text-gray-900 dark:text-gray-100">{{ order.notes }}</p>
                </div>
                
                <!-- Payment Method Selection -->
                <div v-if="!order.is_paid && order.status !== 'cancelled' && showPaymentMethodSelector && canProcessPayments" class="mb-4 p-3 sm:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">{{$t('app.views.orders.payment.select_method') || 'Select Payment Method'}}</h4>
                  <div class="grid grid-cols-2 gap-2 sm:gap-3">
                    <button
                      v-for="method in paymentMethods"
                      :key="method.value"
                      type="button"
                      class="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 sm:py-3 rounded-md border-2 transition-all text-xs sm:text-sm"
                      :class="selectedPaymentMethod === method.value 
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300' 
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-indigo-300 dark:hover:border-indigo-600'"
                      @click="selectedPaymentMethod = method.value"
                    >
                      <component :is="method.icon" class="h-4 w-4 sm:h-5 sm:w-5" />
                      <span class="font-medium text-xs sm:text-sm">{{ method.label }}</span>
                    </button>
                  </div>
                  
                  <!-- Cash Change Calculator -->
                  <div v-if="selectedPaymentMethod === 'cash'" class="mt-4 space-y-3">
                    <div class="bg-white dark:bg-gray-900 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {{$t('app.views.orders.payment.amount_received') || 'Monto Recibido'}}
                      </label>
                      <div class="relative">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">$</span>
                        <input
                          v-model.number="cashReceived"
                          type="number"
                          step="0.01"
                          min="0"
                          class="block w-full pl-7 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
                          :placeholder="(order.total || 0).toFixed(2)"
                          @input="calculateChange"
                        />
                      </div>
                    </div>
                    
                    <!-- Total and Change Display -->
                    <div class="grid grid-cols-2 gap-3">
                      <div class="bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-lg border border-indigo-200 dark:border-indigo-800">
                        <p class="text-xs text-indigo-600 dark:text-indigo-400 font-medium mb-1">{{$t('app.views.orders.payment.total_to_pay') || 'Total a Pagar'}}</p>
                        <p class="text-lg font-bold text-indigo-900 dark:text-indigo-100">${{ (order.total || 0).toFixed(2) }}</p>
                      </div>
                      <div class="p-3 rounded-lg border" :class="changeAmount >= 0 ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'">
                        <p class="text-xs font-medium mb-1" :class="changeAmount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                          {{ changeAmount >= 0 ? ($t('app.views.orders.payment.change') || 'Cambio') : ($t('app.views.orders.payment.insufficient') || 'Falta') }}
                        </p>
                        <p class="text-lg font-bold" :class="changeAmount >= 0 ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'">
                          ${{ Math.abs(changeAmount).toFixed(2) }}
                        </p>
                      </div>
                    </div>
                    
                    <!-- Insufficient amount warning -->
                    <div v-if="changeAmount < 0" class="flex items-start gap-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <svg class="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p class="text-xs text-red-700 dark:text-red-300">
                        {{$t('app.views.orders.payment.insufficient_warning') || 'El monto recibido es insuficiente para completar el pago'}}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div class="flex flex-col gap-2 sm:flex sm:flex-row sm:justify-center sm:gap-3 mt-6">
                  <!-- Print Pre-Bill Button (only for unpaid orders) -->
                  <button
                    v-if="!order.is_paid && order.status !== 'cancelled'"
                    type="button"
                    class="inline-flex w-full sm:w-auto justify-center items-center gap-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 sm:px-4 text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    @click="handlePrintPreBill"
                    :disabled="isPrintingPreBill"
                  >
                    <svg v-if="!isPrintingPreBill" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <svg v-else class="animate-spin h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ $t('app.views.orders.modals.details.print_pre_bill') || 'Imprimir Cuenta' }}
                  </button>

                  <!-- Complete Payment Button -->
                  <button
                    v-if="!order.is_paid && order.status !== 'cancelled' && canProcessPayments"
                    type="button"
                    class="inline-flex w-full sm:w-auto justify-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 sm:px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    @click="showPaymentMethodSelector ? completePayment() : showPaymentMethodSelector = true"
                  >
                    {{showPaymentMethodSelector ? $t('app.views.orders.payment.confirm_payment') || 'Confirm Payment' : $t('app.views.orders.modals.details.complete_payment') || 'Complete Payment'}}
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, BanknotesIcon, CreditCardIcon, DevicePhoneMobileIcon, EllipsisHorizontalIcon, EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import orderService from '@/services/orderService'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { useTheme } from '@/composables/useTheme'
import { usePermissions } from '@/composables/usePermissions'
import { useCustomerPrint } from '@/composables/useCustomerPrint'
import { useOperationMode } from '@/composables/useOperationMode';

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  },
  order: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      status: '',
      customerName: '',
      table: '',
      type: 'Dine-in',
      createdAt: new Date(),
      items: [],
      subtotal: 0,
      tax: 0,
      taxRate: 0.1,
      total: 0,
      notes: ''
    })
  }
});

const emit = defineEmits(['close', 'status-update', 'paymentCompleted', 'openCashRegister', 'edit-order']);

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();
const { t } = useI18n();
const { canProcessPayments } = usePermissions();
const { printPreBill, printCustomerReceipt } = useCustomerPrint();
const { isPosOnlyMode } = useOperationMode();
const isMounted = ref(false);
const isPrintingPreBill = ref(false);

// Internal toast notification state
const internalToast = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'info' | 'warning'
});

// Function to show internal toast
const showInternalToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success', duration = 3000) => {
  internalToast.value = { show: true, message, type };
  setTimeout(() => {
    internalToast.value.show = false;
  }, duration);
};

// Watch for confirmation dialog state
const { isOpen: isConfirmOpen } = useConfirm();

// Computed property for backdrop classes
const backdropClasses = computed(() => [
  'fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity',
  isConfirmOpen.value ? 'pointer-events-none' : ''
]);

onMounted(() => {
  isMounted.value = true;
});

const handleClose = () => {
  if (isMounted.value) {
    emit('close');
  }
};

// Helper function to get category visibility
const getCategoryVisibility = (item: any): boolean | null => {
  if (!item.menu_item?.category) return null;
  
  // If category is an object with visible_in_kitchen property
  if (typeof item.menu_item.category === 'object' && item.menu_item.category !== null) {
    return item.menu_item.category.visible_in_kitchen ?? true;
  }
  
  // If category is just a string, we don't have visibility info
  return null;
};

// Calculate item total including extras
const calculateItemTotal = (item: any): number => {
  let total = item.quantity * (item.price || item.unit_price || 0);
  
  // Add extras to total
  if (item.extras && item.extras.length > 0) {
    const extrasTotal = item.extras.reduce((sum: number, extra: any) => {
      return sum + (extra.price * extra.quantity);
    }, 0);
    total += extrasTotal;
  }
  
  return total;
};

// Calculate total savings from discounts
const totalSavings = computed(() => {
  if (!props.order.items) return 0;
  
  return props.order.items.reduce((total, item) => {
    // Check if unit_price is less than menu item price (discount was applied)
    if (item.menu_item?.price && item.unit_price && item.unit_price < item.menu_item.price) {
      const savings = (item.menu_item.price - item.unit_price) * item.quantity;
      return total + savings;
    }
    return total;
  }, 0);
});

// Calculate totals if needed
const orderWithTotals = computed(() => {
  // If total_amount is already calculated, use it
  if (props.order.total_amount > 0) return props.order;

  // Otherwise calculate from items
  const subtotal = props.order.items.reduce((sum, item) => {
    return sum + (item.quantity * item.unit_price);
  }, 0);

  // Assuming 10% tax for example
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  return {
    ...props.order,
    subtotal,
    tax,
    total_amount: total
  };
});

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

function formatDateTime(date) {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function updateStatus(newStatus) {
  emit('status-update', {
    orderId: props.order.id,
    status: newStatus
  });
  emit('close');
}

async function cancelOrder() {
  const confirmed = await confirm(
    'Cancel Order',
    'Are you sure you want to cancel this order? This action cannot be undone.',
    'Yes, cancel order',
    'No, keep it',
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  );

  if (confirmed) {
    updateStatus('Cancelled');
  }
}

const showPaymentMethodSelector = ref(false)
const selectedPaymentMethod = ref<'cash' | 'card' | 'digital' | 'other'>('cash')
const cashReceived = ref<number>(0)
const changeAmount = ref<number>(0)

const paymentMethods = [
  { value: 'cash' as const, label: t('app.views.cashRegister.cash') || 'Cash', icon: BanknotesIcon },
  { value: 'card' as const, label: t('app.views.cashRegister.card') || 'Card', icon: CreditCardIcon },
  { value: 'digital' as const, label: t('app.views.cashRegister.digital') || 'Digital', icon: DevicePhoneMobileIcon },
  { value: 'other' as const, label: t('app.views.cashRegister.other') || 'Other', icon: EllipsisHorizontalIcon }
]

// Calculate change when cash amount changes
function calculateChange() {
  const total = props.order.total || 0;
  const received = cashReceived.value || 0;
  changeAmount.value = received - total;
}

// Handle print pre-bill
async function handlePrintPreBill() {
  isPrintingPreBill.value = true;
  try {
    // Build order object with correct structure for printing
    // This ensures items are properly associated with persons
    const orderForPrint = {
      ...props.order,
      // If order has persons but items don't have person_id, reconstruct the structure
      items: props.order.items || [],
      persons: props.order.persons || []
    };
    
    // If there are persons but items don't have person_id, try to match them
    if (orderForPrint.persons.length > 0) {
      const itemsWithPersonId = orderForPrint.items.filter((item: any) => item.person_id);
      
      // If no items have person_id, we need to use the persons' items instead
      if (itemsWithPersonId.length === 0 && orderForPrint.persons.some((p: any) => p.items && p.items.length > 0)) {
        // Flatten items from persons
        orderForPrint.items = orderForPrint.persons.flatMap((person: any) => 
          (person.items || []).map((item: any) => ({
            ...item,
            person_id: person.id
          }))
        );
      }
    }
    
    await printPreBill(orderForPrint);
  } catch (error) {
    showInternalToast(
      t('app.views.orders.modals.details.pre_bill_print_error') || 'Error al imprimir la pre-cuenta',
      'error'
    );
  } finally {
    isPrintingPreBill.value = false;
  }
}

async function completePayment() {
  // Validate cash payment has sufficient amount
  if (selectedPaymentMethod.value === 'cash') {
    if (!cashReceived.value || cashReceived.value <= 0) {
      showInternalToast(
        t('app.views.orders.payment.enter_amount') || 'Por favor ingresa el monto recibido',
        'warning',
        3000
      );
      return;
    }
    
    if (changeAmount.value < 0) {
      showInternalToast(
        t('app.views.orders.payment.insufficient_amount') || 'El monto recibido es insuficiente',
        'error',
        3000
      );
      return;
    }
  }
  
  try {
    // Save payment info before resetting
    const paymentInfo = {
      method: selectedPaymentMethod.value,
      amountPaid: selectedPaymentMethod.value === 'cash' ? cashReceived.value : props.order.total,
      change: selectedPaymentMethod.value === 'cash' ? changeAmount.value : 0
    };
    
    await orderService.markOrderPaid(props.order.id, selectedPaymentMethod.value, props.order.status);
    showInternalToast(t('app.views.orders.payment.success') || 'Pago completado exitosamente', 'success');
    showPaymentMethodSelector.value = false;
    
    // Auto-print customer receipt after payment if enabled
    try {
      // Create updated order object with payment info
      const paidOrder = {
        ...props.order,
        is_paid: true,
        payment_method: paymentInfo.method,
        amount_paid: paymentInfo.amountPaid,
        change_amount: paymentInfo.change
      };
      
      await printCustomerReceipt(paidOrder);
    } catch (printError) {
      // Don't block the payment flow if printing fails
      showInternalToast(
        t('app.views.orders.modals.details.receipt_print_warning') || 'Pago completado pero no se pudo imprimir el recibo',
        'warning',
        4000
      );
    }
    
    // Reset cash fields after printing
    cashReceived.value = 0;
    changeAmount.value = 0;
    
    // Close modal immediately to prevent showing stale data
    emit('close');
    
    // Emit payment completed event after closing
    emit('paymentCompleted', props.order);
  } catch (e: any) {
    console.error('Failed to complete payment:', e);

    // Get error message from response
    const errorMessage = e.response?.data?.error?.message || e.response?.data?.detail || '';
    
    // Handle specific cash register session error with friendly message
    if (errorMessage.includes('No open cash register session') || errorMessage.includes('cash register session')) {
      showInternalToast(
        'No hay una sesión de caja abierta. Por favor abre una sesión de caja antes de procesar pagos.',
        'warning',
        5000
      );
    } else {
      // Show generic error for other payment failures
      const friendlyMessage = errorMessage || t('app.views.cashRegister.paymentFailedGeneric') || 'Error al procesar el pago';
      showInternalToast(friendlyMessage, 'error', 5000);
    }
  }
}
</script>
