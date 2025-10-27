<template>
  <MainLayout>
    <PageHeader
      :title="t('app.views.cashRegister.title') || 'Cash Register'"
      :subtitle="t('app.views.cashRegister.subtitle') || 'Manage cash register sessions and transactions'"
    />
    
    <!-- Tabs -->
    <div class="mt-6 mb-6 sm:mb-8 overflow-x-auto">
      <nav class="flex space-x-4 sm:space-x-8 min-w-max">
        <button @click="activeTab = 'current'"
          :class="activeTab === 'current' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
          {{ t('app.views.cashRegister.currentSession') || 'Current Session' }}
        </button>
        <button @click="activeTab = 'reports'"
          :class="activeTab === 'reports' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
          {{ t('app.views.cashRegister.reports') || 'Reports' }}
        </button>
      </nav>
    </div>

    <!-- Current Session Tab -->
    <div v-if="activeTab === 'current'">
      <div v-if="currentSession" class="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-4">
          <div class="flex items-center gap-3">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              <span class="font-medium">{{ t('app.views.cashRegister.sessionNumber') || 'Session' }} #{{ currentSession.session_number }}</span>
              <span class="mx-2">•</span>
              <span class="font-medium">{{ t('app.views.cashRegister.openedAt') || 'Opened' }}:</span>
              <span class="ml-2">{{ sessionDuration }}</span>
            </div>
          </div>
          <div class="flex flex-col sm:flex-row gap-2">
            <BaseButton @click="openExpenseModal" variant="warning" full-width class="sm:w-auto">
              <template #icon>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
                </svg>
              </template>
              {{ t('app.views.cashRegister.addExpense') || 'Add Expense' }}
            </BaseButton>
            <BaseButton @click="openCutModal" variant="info" full-width class="sm:w-auto">
              <template #icon>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
                </svg>
              </template>
              {{ t('app.views.cashRegister.cut') || 'Cut' }}
            </BaseButton>
            <BaseButton @click="openCloseModal" variant="danger" full-width class="sm:w-auto">
              <template #icon>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </template>
              {{ t('app.views.cashRegister.close') || 'Close' }}
            </BaseButton>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div class="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg border border-green-200 dark:border-green-800">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
                {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
              </h3>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">
              ${{ currentSession.initial_balance?.toFixed(2) || '0.00' }}
            </p>
          </div>
          <div class="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {{ t('app.views.cashRegister.currentBalance') || 'Current Balance' }}
              </h3>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600 dark:text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              ${{ currentBalance.toFixed(2) }}
            </p>
          </div>
          <div class="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-purple-800 dark:text-purple-200">
                {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
              </h3>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600 dark:text-purple-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {{ transactions.length }}
            </p>
          </div>
          <div class="bg-amber-50 dark:bg-amber-900/30 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-amber-800 dark:text-amber-200">
                {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
              </h3>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-amber-600 dark:text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" />
              </svg>
            </div>
            <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">
              ${{ sessionExpenses.toFixed(2) }}
            </p>
          </div>
        </div>
        <LastCutDisplay :lastCut="lastCut" :isLoading="lastCutLoading" />
      </div>

      <!-- No Session Message -->
      <div v-else class="mb-8 text-center">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 sm:p-8">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 sm:h-16 sm:w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-base sm:text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {{ t('app.views.cashRegister.noActiveSession') || 'No Active Session' }}
          </h3>
          <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-4">
            {{ t('app.views.cashRegister.openSessionToStart') || 'Open a session to start managing cash register operations.' }}
          </p>
          <BaseButton @click="openOpenModal" variant="primary" size="lg" full-width class="sm:w-auto">
            {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
          </BaseButton>
        </div>
      </div>

      <!-- Transactions List -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
          </h2>
        </div>
        <div v-if="transactions.length === 0" class="p-6 text-center">
          <p class="text-gray-500 dark:text-gray-400">
            {{ t('app.views.cashRegister.noTransactions') || 'No transactions yet.' }}
          </p>
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div v-for="transaction in transactions" :key="transaction.id" class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
            <div class="flex justify-between items-center gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ translateDescription(transaction.description) }}
                  </p>
                  <span v-if="transaction.payment_method" 
                    class="px-2 py-0.5 text-xs font-medium rounded-full"
                    :class="getPaymentMethodBadgeClass(transaction.payment_method)">
                    {{ translatePaymentMethod(transaction.payment_method) }}
                  </span>
                  <span v-if="transaction.category"
                    class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    {{ transaction.category }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(transaction.created_at) }}
                </p>
              </div>
              <div class="text-right flex items-center gap-3">
                <div>
                  <p class="text-lg font-semibold"
                    :class="transaction.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                    {{ transaction.amount >= 0 ? '+' : '-' }}${{ Math.abs(transaction.amount)?.toFixed(2) || '0.00' }}
                  </p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ translateTransactionType(transaction.transaction_type) }}
                  </p>
                </div>
                <button 
                  v-if="false"
                  @click="confirmDeleteTransaction(transaction)"
                  class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                  :title="t('app.actions.delete') || 'Delete'">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Tab -->
    <div v-if="activeTab === 'reports'">
      <ReportsView />
    </div>

    <!-- Open Session Modal -->
  <div v-if="openModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
      </h3>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
      </label>
      <input v-model="initialBalance" type="number" step="0.01"
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="primary" size="sm" @click="openSession">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>

  <!-- Close Session Modal -->
  <div v-if="closeModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.closeSession') || 'Close Session' }}
      </h3>
      
      <!-- Toggle for denomination counting -->
      <div class="mb-4">
        <label class="flex items-center cursor-pointer">
          <input type="checkbox" v-model="useDenominationCounting" 
            class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-200">
            {{ t('app.views.cashRegister.useDenominationCounting') || 'Count denominations' }}
          </span>
        </label>
      </div>

      <!-- Denomination Counter -->
      <div v-if="useDenominationCounting" class="mb-4">
        <DenominationCounter v-model="denominations" @update:total="actualBalance = $event" />
      </div>

      <!-- Manual balance input (shown when not using denomination counting) -->
      <div v-else class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
          {{ t('app.views.cashRegister.actualBalance') || 'Actual Balance' }}
        </label>
        <input v-model="actualBalance" type="number" step="0.01"
          class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      </div>

      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {{ t('app.views.cashRegister.notes') || 'Notes' }}
      </label>
      <textarea v-model="closeNotes" rows="3"
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="danger" size="sm" @click="closeSession">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>

  <!-- Expense Modal -->
  <div v-if="expenseModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.addExpense') || 'Add Expense' }}
      </h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseAmount') || 'Amount' }}
          </label>
          <input v-model="expenseAmount" type="number" step="0.01" min="0"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseDescription') || 'Description' }}
          </label>
          <input v-model="expenseDescription" type="text"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseCategory') || 'Category (Optional)' }}
          </label>
          <select v-model="expenseCategory"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500">
            <option value="">{{ t('app.views.cashRegister.selectCategory') || 'Select a category' }}</option>
            <option value="supplies">{{ t('app.views.cashRegister.categorySupplies') || 'Supplies' }}</option>
            <option value="utilities">{{ t('app.views.cashRegister.categoryUtilities') || 'Utilities' }}</option>
            <option value="maintenance">{{ t('app.views.cashRegister.categoryMaintenance') || 'Maintenance' }}</option>
            <option value="inventory">{{ t('app.views.cashRegister.categoryInventory') || 'Inventory' }}</option>
            <option value="other">{{ t('app.views.cashRegister.categoryOther') || 'Other' }}</option>
          </select>
        </div>
      </div>
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="warning" size="sm" @click="addExpense">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>

  <!-- Cut Modal -->
  <div v-if="cutModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.cutSession') || 'Cut Session' }}
      </h3>
      <div class="space-y-4">
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.summary') || 'Summary' }}
          </h4>
          <div class="mt-2 space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
              </span>
              <span class="font-medium">${{ cutReport.total_sales?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
              </span>
              <span class="font-medium">${{ cutReport.total_refunds?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
              </span>
              <span class="font-medium">${{ cutReport.total_tips?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
              </span>
              <span class="font-medium text-red-600 dark:text-red-400">${{ cutReport.total_expenses?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="flex justify-between font-bold">
              <span class="text-gray-900 dark:text-gray-100">
                {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
              </span>
              <span>${{ cutReport.net_cash_flow?.toFixed(2) || '0.00' }}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.paymentBreakdown') || 'Payment Breakdown' }}
          </h4>
          <div class="mt-2 space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.cashPayments') || 'Cash Payments' }}
              </label>
              <input v-model="cashPayments" type="number" step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.cardPayments') || 'Card Payments' }}
              </label>
              <input v-model="cardPayments" type="number" step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.digitalPayments') || 'Digital Payments' }}
              </label>
              <input v-model="digitalPayments" type="number" step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.otherPayments') || 'Other Payments' }}
              </label>
              <input v-model="otherPayments" type="number" step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
        </div>
      </div>
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="info" size="sm" @click="performCut">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div v-if="deleteConfirmModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.deleteTransaction') || 'Delete Transaction' }}
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-2">
        {{ t('app.views.cashRegister.confirmDeleteTransaction') || 'Are you sure you want to delete this transaction?' }}
      </p>
      <div v-if="transactionToDelete" class="bg-gray-50 dark:bg-gray-800 p-3 rounded-md mb-6">
        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ transactionToDelete.description }}
        </p>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ transactionToDelete.amount >= 0 ? '+' : '-' }}${{ Math.abs(transactionToDelete.amount)?.toFixed(2) || '0.00' }}
        </p>
      </div>
      <div class="flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="cancelDelete">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="danger" size="sm" @click="deleteTransaction">
          {{ t('app.actions.delete') || 'Delete' }}
        </BaseButton>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
          {{ t('app.views.cashRegister.expenseCategory') || 'Category (Optional)' }}
        </label>
        <select v-model="expenseCategory"
          class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500">
          <option value="">{{ t('app.views.cashRegister.selectCategory') || 'Select a category' }}</option>
          <option value="supplies">{{ t('app.views.cashRegister.categorySupplies') || 'Supplies' }}</option>
          <option value="utilities">{{ t('app.views.cashRegister.categoryUtilities') || 'Utilities' }}</option>
          <option value="maintenance">{{ t('app.views.cashRegister.categoryMaintenance') || 'Maintenance' }}</option>
          <option value="inventory">{{ t('app.views.cashRegister.categoryInventory') || 'Inventory' }}</option>
          <option value="other">{{ t('app.views.cashRegister.categoryOther') || 'Other' }}</option>
        </select>
      </div>
    </div>
    <div class="mt-6 flex justify-end space-x-3">
      <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
        {{ t('app.actions.cancel') || 'Cancel' }}
      </BaseButton>
      <BaseButton type="button" variant="warning" size="sm" @click="addExpense">
        {{ t('app.actions.save') || 'Save' }}
      </BaseButton>
    </div>
  </div>

<!-- Cut Modal -->
<div v-if="cutModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
  <div class="w-full rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
      {{ t('app.views.cashRegister.cutSession') || 'Cut Session' }}
    </h3>
    <div class="space-y-4">
      <div>
        <h4 class="font-medium text-gray-900 dark:text-gray-100">
          {{ t('app.views.cashRegister.summary') || 'Summary' }}
        </h4>
        <div class="mt-2 space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">
              {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
            </span>
            <span class="font-medium">${{ cutReport.total_sales?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">
              {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
            </span>
            <span class="font-medium">${{ cutReport.total_refunds?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">
              {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
            </span>
            <span class="font-medium">${{ cutReport.total_tips?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">
              {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
            </span>
            <span class="font-medium text-red-600 dark:text-red-400">${{ cutReport.total_expenses?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="flex justify-between font-bold">
            <span class="text-gray-900 dark:text-gray-100">
              {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
            </span>
            <span>${{ cutReport.net_cash_flow?.toFixed(2) || '0.00' }}</span>
          </div>
        </div>
      </div>

      <div>
        <h4 class="font-medium text-gray-900 dark:text-gray-100">
          {{ t('app.views.cashRegister.paymentBreakdown') || 'Payment Breakdown' }}
        </h4>
        <div class="mt-2 space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
              {{ t('app.views.cashRegister.cashPayments') || 'Cash Payments' }}
            </label>
            <input v-model="cashPayments" type="number" step="0.01"
              class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
              {{ t('app.views.cashRegister.cardPayments') || 'Card Payments' }}
            </label>
            <input v-model="cardPayments" type="number" step="0.01"
              class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
              {{ t('app.views.cashRegister.digitalPayments') || 'Digital Payments' }}
            </label>
            <input v-model="digitalPayments" type="number" step="0.01"
              class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
              {{ t('app.views.cashRegister.otherPayments') || 'Other Payments' }}
            </label>
            <input v-model="otherPayments" type="number" step="0.01"
              class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>
      </div>
    </div>
    <div class="mt-6 flex justify-end space-x-3">
      <BaseButton type="button" variant="secondary" size="sm" @click="closeModals">
        {{ t('app.actions.cancel') || 'Cancel' }}
      </BaseButton>
      <BaseButton type="button" variant="info" size="sm" @click="performCut">
        {{ t('app.actions.save') || 'Save' }}
      </BaseButton>
    </div>
  </div>
</div>

<!-- Delete Confirmation Modal -->
<div v-if="deleteConfirmModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
  <div class="w-full rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
      {{ t('app.views.cashRegister.deleteTransaction') || 'Delete Transaction' }}
    </h3>
    <p class="text-gray-600 dark:text-gray-400 mb-2">
      {{ t('app.views.cashRegister.confirmDeleteTransaction') || 'Are you sure you want to delete this transaction?' }}
    </p>
    <div v-if="transactionToDelete" class="bg-gray-50 dark:bg-gray-800 p-3 rounded-md mb-6">
      <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
        {{ transactionToDelete.description }}
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ transactionToDelete.amount >= 0 ? '+' : '-' }}${{ Math.abs(transactionToDelete.amount)?.toFixed(2) || '0.00' }}
      </p>
    </div>
    <div class="flex justify-end space-x-3">
      <BaseButton type="button" variant="secondary" size="sm" @click="cancelDelete">
        {{ t('app.actions.cancel') || 'Cancel' }}
      </BaseButton>
      <BaseButton type="button" variant="danger" size="sm" @click="deleteTransaction">
        {{ t('app.actions.delete') || 'Delete' }}
      </BaseButton>
    </div>
  </div>
</div>
</MainLayout>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import cashRegisterService from '@/services/cashRegisterService';
import { useToast } from '@/composables/useToast'
import LastCutDisplay from '@/components/LastCutDisplay.vue'
import ReportsView from '@/components/ReportsView.vue'
import DenominationCounter from '@/components/DenominationCounter.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const { t } = useI18n()
const toast = useToast()

const activeTab = ref('current')
const isRefreshing = ref(false)
const openModalOpen = ref(false)
const closeModalOpen = ref(false)
const cutModalOpen = ref(false)
const expenseModalOpen = ref(false)
const currentSession = ref<any>(null)
const transactions = ref<any[]>([])
const currentBalance = ref(0)
const initialBalance = ref(0)
const currentTime = ref(new Date())

// Computed properties
const sessionDuration = computed(() => {
  if (!currentSession.value?.opened_at) return '0h 0m'
  
  const openedAt = new Date(currentSession.value.opened_at)
  const now = currentTime.value
  const diffMs = now.getTime() - openedAt.getTime()
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  return `${hours}h ${minutes}m`
})

const sessionExpenses = computed(() => {
  return transactions.value
    .filter(t => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0)
})
const actualBalance = ref(0)
const closeNotes = ref('')
const cashPayments = ref(0)
const cardPayments = ref(0)
const digitalPayments = ref(0)
const otherPayments = ref(0)
const cutReport = ref({
  total_sales: 0,
  total_refunds: 0,
  total_tips: 0,
  total_expenses: 0,
  total_transactions: 0,
  net_cash_flow: 0
})

const lastCut = ref<any>(null)
const lastCutLoading = ref(false)
const expenseAmount = ref(0)
const expenseDescription = ref('')
const expenseCategory = ref('')

// Denomination counting (Mexican Pesos)
const useDenominationCounting = ref(false)
const denominations = ref({
  bills_1000: 0,
  bills_500: 0,
  bills_200: 0,
  bills_100: 0,
  bills_50: 0,
  bills_20: 0,
  coins_20: 0,
  coins_10: 0,
  coins_5: 0,
  coins_2: 0,
  coins_1: 0,
  coins_50_cent: 0
})

const openOpenModal = () => {
  openModalOpen.value = true
}

const openCloseModal = () => {
  closeModalOpen.value = true
}

const openExpenseModal = () => {
  expenseModalOpen.value = true
}

const openCutModal = async () => {
  cutModalOpen.value = true

  // Pre-populate cut report with current session data
  if (currentSession.value) {
    try {
      // Get current transactions to calculate initial values
      const transactionsResponse = await cashRegisterService.getTransactions(currentSession.value.id)
      const transactions = Array.isArray(transactionsResponse) ? transactionsResponse : transactionsResponse.data || []

      // Calculate totals from transactions
      const totalSales = transactions
        .filter(t => t.transaction_type === 'sale')
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const totalRefunds = transactions
        .filter(t => t.transaction_type === 'refund' || t.transaction_type === 'cancellation')
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const totalTips = transactions
        .filter(t => t.transaction_type === 'tip')
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const totalExpenses = transactions
        .filter(t => t.transaction_type === 'expense')
        .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0)

      const netCashFlow = totalSales - totalRefunds + totalTips - totalExpenses

      // Update cut report with real data
      cutReport.value = {
        total_sales: totalSales,
        total_refunds: totalRefunds,
        total_tips: totalTips,
        total_expenses: totalExpenses,
        total_transactions: transactions.length,
        net_cash_flow: netCashFlow
      }

      // Auto-fill payment methods based on transaction payment methods
      const cashTotal = transactions
        .filter(t => t.payment_method?.toUpperCase() === 'CASH' && t.amount > 0)
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const cardTotal = transactions
        .filter(t => t.payment_method?.toUpperCase() === 'CARD' && t.amount > 0)
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const digitalTotal = transactions
        .filter(t => t.payment_method?.toUpperCase() === 'DIGITAL' && t.amount > 0)
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      const otherTotal = transactions
        .filter(t => t.payment_method?.toUpperCase() === 'OTHER' && t.amount > 0)
        .reduce((sum, t) => sum + (t.amount || 0), 0)

      // Set the payment breakdown fields
      cashPayments.value = cashTotal
      cardPayments.value = cardTotal
      digitalPayments.value = digitalTotal
      otherPayments.value = otherTotal
    } catch (error) {
      console.error('Error loading cut report data:', error)
    }
  }
}

const closeModals = () => {
  openModalOpen.value = false
  closeModalOpen.value = false
  cutModalOpen.value = false
  expenseModalOpen.value = false
  initialBalance.value = 0
  actualBalance.value = 0
  closeNotes.value = ''
  cashPayments.value = 0
  cardPayments.value = 0
  digitalPayments.value = 0
  otherPayments.value = 0
  expenseAmount.value = 0
  expenseDescription.value = ''
  expenseCategory.value = ''
  useDenominationCounting.value = false
  denominations.value = {
    bills_1000: 0,
    bills_500: 0,
    bills_200: 0,
    bills_100: 0,
    bills_50: 0,
    bills_20: 0,
    coins_20: 0,
    coins_10: 0,
    coins_5: 0,
    coins_2: 0,
    coins_1: 0,
    coins_50_cent: 0
  }
}

const openSession = async () => {
  if (!initialBalance.value) {
    toast.showToast(t('app.views.cashRegister.initialBalanceRequired') || 'Initial balance is required', 'error')
    return
  }

  try {
    const session = await cashRegisterService.openSession(Number(initialBalance.value))
    currentSession.value = session
    closeModals()
    loadTransactions()
    toast.showToast(t('app.views.cashRegister.sessionOpened') || 'Session opened successfully', 'success')
    loadCurrentSession()
  } catch (error: any) {
    console.error('Error opening session:', error)
    toast.showToast(error.response?.data?.detail || 'Failed to open session', 'error')
  }
}

const closeSession = async () => {
  if (!actualBalance.value) {
    toast.showToast(t('app.views.cashRegister.finalBalanceRequired') || 'Final balance is required', 'error')
    return
  }

  try {
    let session
    if (useDenominationCounting.value) {
      // Use denomination counting endpoint
      session = await cashRegisterService.closeSessionWithDenominations(
        currentSession.value.id,
        Number(actualBalance.value),
        closeNotes.value || undefined,
        denominations.value
      )
    } else {
      // Use regular close endpoint
      session = await cashRegisterService.closeSession(
        currentSession.value.id,
        Number(actualBalance.value),
        closeNotes.value || undefined
      )
    }
    currentSession.value = session
    closeModals()
    toast.showToast(t('app.views.cashRegister.sessionClosed') || 'Session closed successfully', 'success')
    currentSession.value = null
    transactions.value = []
    currentBalance.value = 0
    loadCurrentSession()
  } catch (error: any) {
    console.error('Error closing session:', error)
    toast.showToast(error.response?.data?.detail || 'Failed to close session', 'error')
  }
}

const addExpense = async () => {
  if (!expenseAmount.value || expenseAmount.value <= 0) {
    toast.showToast(t('app.views.cashRegister.expenseAmountRequired') || 'Expense amount is required', 'error')
    return
  }

  if (!expenseDescription.value || expenseDescription.value.trim() === '') {
    toast.showToast(t('app.views.cashRegister.expenseDescriptionRequired') || 'Expense description is required', 'error')
    return
  }

  if (!currentSession.value) {
    toast.showToast(t('app.views.cashRegister.noActiveSession') || 'No active session', 'error')
    return
  }

  try {
    await cashRegisterService.addExpense(currentSession.value.id, {
      amount: Number(expenseAmount.value),
      description: expenseDescription.value,
      category: expenseCategory.value || undefined
    })

    toast.showToast(t('app.views.cashRegister.expenseAdded') || 'Expense added successfully', 'success')
    closeModals()
    loadCurrentSession()
  } catch (error: any) {
    console.error('Error adding expense:', error)
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.expenseFailed') || 'Failed to add expense', 'error')
  }
}

const transactionToDelete = ref<any>(null)
const deleteConfirmModalOpen = ref(false)

const confirmDeleteTransaction = (transaction: any) => {
  transactionToDelete.value = transaction
  deleteConfirmModalOpen.value = true
}

const deleteTransaction = async () => {
  if (!transactionToDelete.value) return

  try {
    await cashRegisterService.deleteTransaction(transactionToDelete.value.id)
    toast.showToast(t('app.views.cashRegister.transactionDeleted') || 'Transaction deleted successfully', 'success')
    deleteConfirmModalOpen.value = false
    transactionToDelete.value = null
    loadCurrentSession()
  } catch (error: any) {
    console.error('Error deleting transaction:', error)
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.transactionDeleteFailed') || 'Failed to delete transaction', 'error')
  }
}

const cancelDelete = () => {
  deleteConfirmModalOpen.value = false
  transactionToDelete.value = null
}

const performCut = async () => {
  if (!currentSession.value) return

  try {
    const paymentBreakdown = {
      cash: Number(cashPayments.value),
      card: Number(cardPayments.value),
      digital: Number(digitalPayments.value),
      other: Number(otherPayments.value)
    }

    const result = await cashRegisterService.cutSession(currentSession.value.id, paymentBreakdown)
    const resultData = result.data || result

    // Update cut report with real data from backend
    cutReport.value = {
      total_sales: resultData.total_sales || 0,
      total_refunds: resultData.total_refunds || 0,
      total_tips: resultData.total_tips || 0,
      total_expenses: resultData.total_expenses || 0,
      total_transactions: resultData.total_transactions || 0,
      net_cash_flow: resultData.net_cash_flow || 0
    }

    toast.showToast(t('app.views.cashRegister.cutSuccessful') || 'Cut performed successfully', 'success')
    loadCurrentSession()
    closeModals()
  } catch (error: any) {
    console.error('Error performing cut:', error)
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.cutFailed') || 'Failed to perform cut', 'error')
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'No date'
  try {
    return new Date(dateString).toLocaleString()
  } catch (error) {
    console.error('Error formatting date:', dateString, error)
    return 'Invalid date'
  }
}

const translateDescription = (description: string) => {
  // Translate "Payment for order #X" pattern
  const orderPaymentMatch = description.match(/Payment for order #(\d+)/i)
  if (orderPaymentMatch) {
    return t('app.views.cashRegister.paymentForOrder', { orderNumber: orderPaymentMatch[1] })
  }
  return description
}

const translateTransactionType = (type: string) => {
  const typeMap: Record<string, string> = {
    'sale': t('app.views.cashRegister.typeSale'),
    'refund': t('app.views.cashRegister.typeRefund'),
    'cancellation': t('app.views.cashRegister.typeCancellation'),
    'tip': t('app.views.cashRegister.typeTip'),
    'manual_add': t('app.views.cashRegister.typeManualAdd'),
    'manual_withdraw': t('app.views.cashRegister.typeManualWithdraw'),
    'expense': t('app.views.cashRegister.typeExpense')
  }
  return typeMap[type] || type
}

const translatePaymentMethod = (method: string) => {
  const methodMap: Record<string, string> = {
    'cash': t('app.views.cashRegister.cash') || 'Cash',
    'card': t('app.views.cashRegister.card') || 'Card',
    'digital': t('app.views.cashRegister.digital') || 'Digital',
    'other': t('app.views.cashRegister.other') || 'Other'
  }
  return methodMap[method?.toLowerCase()] || method
}

const getPaymentMethodBadgeClass = (paymentMethod: string) => {
  const method = paymentMethod?.toUpperCase()
  switch (method) {
    case 'CASH':
      return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800'
    case 'CARD':
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800'
    case 'DIGITAL':
      return 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800'
    case 'OTHER':
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600'
    default:
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
  }
}

const loadCurrentSession = async () => {
  try {
    isRefreshing.value = true
    const session = await cashRegisterService.getCurrentSession()
    currentSession.value = session || null
    if (currentSession.value) {
      loadTransactions()
      loadLastCut() // Load last cut information
    }
  } catch (error) {
    console.error('Error loading current session:', error)
  } finally {
    isRefreshing.value = false
  }
}

const loadTransactions = async () => {
  if (!currentSession.value) return

  try {
    // Get transactions for current session
    const transactionsResponse = await cashRegisterService.getTransactions(currentSession.value.id)
    const transactionsData = Array.isArray(transactionsResponse) ? transactionsResponse : transactionsResponse.data || []
    transactions.value = transactionsData

    // Calculate current balance
    const totalTransactions = transactions.value.reduce((sum, t) => sum + (t.amount || 0), 0)
    currentBalance.value = (currentSession.value.initial_balance || 0) + totalTransactions
  } catch (error) {
    console.error('Error loading transactions:', error)
    transactions.value = []
    currentBalance.value = currentSession.value.initial_balance || 0
  }
}

const loadLastCut = async () => {
  if (!currentSession.value) {
    lastCut.value = null
    return
  }

  try {
    lastCutLoading.value = true
    const cutData = await cashRegisterService.getLastCut(currentSession.value.id)
    lastCut.value = cutData || null
  } catch (error) {
    console.error('Error loading last cut:', error)
    lastCut.value = null
  } finally {
    lastCutLoading.value = false
  }
}

onMounted(() => {
  loadCurrentSession()

  // Update timer every minute
  const timerInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 60000) // Update every minute

  // Listen for order payment completion events
  const handlePaymentCompleted = () => {
    loadCurrentSession()
  }

  window.addEventListener('orderPaymentCompleted', handlePaymentCompleted)

  // Store the event listener for cleanup
  onUnmounted(() => {
    clearInterval(timerInterval)
    window.removeEventListener('orderPaymentCompleted', handlePaymentCompleted)
  })
})
</script>
