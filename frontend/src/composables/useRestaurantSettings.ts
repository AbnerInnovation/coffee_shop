import { ref, type Ref } from 'vue'
import { useToast } from 'vue-toastification'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

export interface RestaurantSettings {
  kitchen_print_enabled: boolean
  kitchen_print_paper_width: number
  allow_dine_in_without_table: boolean
}

export interface ISettingsService {
  updateSetting(key: keyof RestaurantSettings, value: any): Promise<void>
  loadSettings(): Promise<Partial<RestaurantSettings>>
}

class RestaurantSettingsService implements ISettingsService {
  async updateSetting(key: keyof RestaurantSettings, value: any): Promise<void> {
    await api.patch('/restaurants/current', { [key]: value })
  }

  async loadSettings(): Promise<Partial<RestaurantSettings>> {
    const authStore = useAuthStore()
    await authStore.loadRestaurant()
    return authStore.restaurant || {}
  }
}

export function useRestaurantSettings(settingsService: ISettingsService = new RestaurantSettingsService()) {
  const toast = useToast()
  const { t } = useI18n()
  const authStore = useAuthStore()

  // Reactive state
  const kitchenPrintEnabled = ref(true)
  const paperWidth = ref(80)
  const allowDineInWithoutTable = ref(false)
  const savingSettings = ref(false)
  const loadingSettings = ref(false)

  // Settings management methods
  const updateSetting = async <K extends keyof RestaurantSettings>(
    key: K,
    value: RestaurantSettings[K],
    successMessage: string
  ): Promise<void> => {
    try {
      savingSettings.value = true

      // Update backend
      await settingsService.updateSetting(key, value)

      // Update local state
      switch (key) {
        case 'kitchen_print_enabled':
          kitchenPrintEnabled.value = value as boolean
          break
        case 'kitchen_print_paper_width':
          paperWidth.value = value as number
          break
        case 'allow_dine_in_without_table':
          allowDineInWithoutTable.value = value as boolean
          break
      }

      // Update auth store
      if (authStore.restaurant) {
        authStore.restaurant[key] = value
      }

      // Show success toast
      toast.success(successMessage)
    } catch (error) {
      console.error(`Error updating ${key} setting:`, error)
      toast.error(t('app.subscription.settings.error'))
    } finally {
      savingSettings.value = false
    }
  }

  // Specific toggle methods with proper typing
  const toggleKitchenPrint = (): Promise<void> => {
    const newValue = !kitchenPrintEnabled.value
    const message = newValue 
      ? t('app.subscription.settings.kitchen_print.enabled')
      : t('app.subscription.settings.kitchen_print.disabled')
    
    return updateSetting('kitchen_print_enabled', newValue, message)
  }

  const setPaperWidth = (width: number): Promise<void> => {
    const message = t('app.subscription.settings.paper_width.updated', { width: `${width}mm` })
    return updateSetting('kitchen_print_paper_width', width, message)
  }

  const toggleDineInWithoutTable = (): Promise<void> => {
    const newValue = !allowDineInWithoutTable.value
    const message = newValue 
      ? t('app.subscription.settings.dine_in_without_table.enabled')
      : t('app.subscription.settings.dine_in_without_table.disabled')
    
    return updateSetting('allow_dine_in_without_table', newValue, message)
  }

  // Load settings from backend
  const loadSettings = async (): Promise<void> => {
    try {
      loadingSettings.value = true
      const settings = await settingsService.loadSettings()
      
      kitchenPrintEnabled.value = settings.kitchen_print_enabled ?? true
      paperWidth.value = settings.kitchen_print_paper_width ?? 80
      allowDineInWithoutTable.value = settings.allow_dine_in_without_table ?? false
    } catch (error) {
      console.error('Error loading restaurant settings:', error)
      toast.error(t('app.subscription.settings.error'))
    } finally {
      loadingSettings.value = false
    }
  }

  return {
    // State
    kitchenPrintEnabled: kitchenPrintEnabled as Ref<boolean>,
    paperWidth: paperWidth as Ref<number>,
    allowDineInWithoutTable: allowDineInWithoutTable as Ref<boolean>,
    savingSettings: savingSettings as Ref<boolean>,
    loadingSettings: loadingSettings as Ref<boolean>,
    
    // Methods
    toggleKitchenPrint,
    setPaperWidth,
    toggleDineInWithoutTable,
    loadSettings,
    
    // Service injection (for testing)
    settingsService
  }
}
