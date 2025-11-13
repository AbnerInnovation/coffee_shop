<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-[10001]">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 text-left align-middle shadow-xl transition-all"
            >
              <!-- Header -->
              <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-8 text-white">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3">
                    <div class="flex h-12 w-12 items-center justify-center rounded-full bg-white/20 backdrop-blur-sm">
                      <CheckCircleIcon class="h-7 w-7 text-white" />
                    </div>
                    <div>
                      <DialogTitle as="h3" class="text-2xl font-bold">
                        🎉 ¡Restaurante Creado Exitosamente!
                      </DialogTitle>
                      <p class="mt-1 text-indigo-100">
                        {{ restaurantData?.restaurant?.name }}
                      </p>
                    </div>
                  </div>
                  <button
                    @click="closeModal"
                    class="rounded-lg p-2 hover:bg-white/10 transition-colors"
                  >
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>
              </div>

              <!-- Content -->
              <div class="px-6 py-6 max-h-[60vh] overflow-y-auto">
                <!-- Tabs -->
                <div class="border-b border-gray-200 dark:border-gray-700 mb-6">
                  <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                    <button
                      @click="activeTab = 'details'"
                      :class="[
                        activeTab === 'details'
                          ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
                      ]"
                    >
                      📋 Detalles
                    </button>
                    <button
                      @click="activeTab = 'credentials'"
                      :class="[
                        activeTab === 'credentials'
                          ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
                      ]"
                    >
                      🔐 Credenciales
                    </button>
                    <button
                      @click="activeTab = 'steps'"
                      :class="[
                        activeTab === 'steps'
                          ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
                      ]"
                    >
                      📝 Primeros Pasos
                    </button>
                  </nav>
                </div>

                <!-- Tab Content -->
                <div v-if="activeTab === 'details'" class="space-y-6">
                  <!-- Restaurant Info -->
                  <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
                    <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      📋 Información del Restaurante
                    </h4>
                    <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Nombre</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white font-semibold">
                          {{ restaurantData?.restaurant?.name }}
                        </dd>
                      </div>
                      <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Subdomain</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white font-mono">
                          {{ restaurantData?.restaurant?.subdomain }}
                        </dd>
                      </div>
                      <div class="sm:col-span-2">
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">URL de Acceso</dt>
                        <dd class="mt-1 flex items-center space-x-2">
                          <a
                            :href="restaurantData?.restaurant_url"
                            target="_blank"
                            class="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 font-mono underline"
                          >
                            {{ restaurantData?.restaurant_url }}
                          </a>
                          <button
                            @click="copyToClipboard(restaurantData?.restaurant_url, 'URL')"
                            class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
                          >
                            <ClipboardDocumentIcon class="h-4 w-4 text-gray-500" />
                          </button>
                        </dd>
                      </div>
                    </dl>
                  </div>

                  <!-- Trial Info -->
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
                    <h4 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
                      🎁 Período de Prueba
                    </h4>
                    <dl class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <div>
                        <dt class="text-sm font-medium text-green-700 dark:text-green-300">Duración</dt>
                        <dd class="mt-1 text-sm text-green-900 dark:text-green-100 font-semibold">
                          {{ restaurantData?.trial_days }} días
                        </dd>
                      </div>
                      <div>
                        <dt class="text-sm font-medium text-green-700 dark:text-green-300">Vence el</dt>
                        <dd class="mt-1 text-sm text-green-900 dark:text-green-100 font-semibold">
                          {{ formatDate(restaurantData?.trial_expires) }}
                        </dd>
                      </div>
                      <div>
                        <dt class="text-sm font-medium text-green-700 dark:text-green-300">Plan Incluido</dt>
                        <dd class="mt-1 text-sm text-green-900 dark:text-green-100 font-semibold">
                          Funcionalidades Pro
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>

                <div v-if="activeTab === 'credentials'" class="space-y-6">
                  <!-- Credentials -->
                  <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-6 border border-amber-200 dark:border-amber-800">
                    <div class="flex items-start space-x-3 mb-4">
                      <ExclamationTriangleIcon class="h-6 w-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 class="text-lg font-semibold text-amber-900 dark:text-amber-100">
                          ⚠️ Información Importante
                        </h4>
                        <p class="mt-1 text-sm text-amber-700 dark:text-amber-300">
                          Guarda estas credenciales en un lugar seguro. La contraseña no se mostrará nuevamente.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 space-y-4">
                    <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      🔐 Credenciales de Administrador
                    </h4>
                    
                    <!-- Email -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        📧 Email
                      </label>
                      <div class="flex items-center space-x-2">
                        <input
                          type="text"
                          :value="restaurantData?.admin_email"
                          readonly
                          class="flex-1 rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                        />
                        <button
                          @click="copyToClipboard(restaurantData?.admin_email, 'Email')"
                          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
                        >
                          <ClipboardDocumentIcon class="h-5 w-5 text-gray-700 dark:text-gray-300" />
                        </button>
                      </div>
                    </div>

                    <!-- Password -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        🔑 Contraseña
                      </label>
                      <div class="flex items-center space-x-2">
                        <input
                          :type="showPassword ? 'text' : 'password'"
                          :value="restaurantData?.admin_password"
                          readonly
                          class="flex-1 rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                        />
                        <button
                          @click="showPassword = !showPassword"
                          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
                        >
                          <EyeIcon v-if="!showPassword" class="h-5 w-5 text-gray-700 dark:text-gray-300" />
                          <EyeSlashIcon v-else class="h-5 w-5 text-gray-700 dark:text-gray-300" />
                        </button>
                        <button
                          @click="copyToClipboard(restaurantData?.admin_password, 'Contraseña')"
                          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
                        >
                          <ClipboardDocumentIcon class="h-5 w-5 text-gray-700 dark:text-gray-300" />
                        </button>
                      </div>
                    </div>

                    <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                      <p class="text-sm text-red-700 dark:text-red-300 font-medium">
                        🔒 Recuerda cambiar la contraseña en el primer inicio de sesión
                      </p>
                    </div>
                  </div>
                </div>

                <div v-if="activeTab === 'steps'" class="space-y-4">
                  <!-- Steps -->
                  <div class="space-y-4">
                    <div
                      v-for="(step, index) in steps"
                      :key="index"
                      class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">
                          {{ index + 1 }}
                        </div>
                        <div class="flex-1">
                          <h5 class="font-semibold text-gray-900 dark:text-white">
                            {{ step.title }}
                          </h5>
                          <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                            {{ step.description }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Tips -->
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
                    <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
                      💡 Consejos
                    </h4>
                    <ul class="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                      <li class="flex items-start space-x-2">
                        <span>•</span>
                        <span>Explora todas las secciones para familiarizarte con el sistema</span>
                      </li>
                      <li class="flex items-start space-x-2">
                        <span>•</span>
                        <span>Revisa tu suscripción en la sección "Suscripción"</span>
                      </li>
                      <li class="flex items-start space-x-2">
                        <span>•</span>
                        <span>Antes de que expire tu prueba, elige un plan que se ajuste a tus necesidades</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div class="flex items-center space-x-2">
                  <button
                    @click="copyShareableMessage"
                    class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <ClipboardDocumentIcon class="h-5 w-5 mr-2" />
                    Copiar Mensaje
                  </button>
                  <button
                    @click="shareViaWhatsApp"
                    class="inline-flex items-center px-4 py-2 border border-green-300 dark:border-green-600 rounded-lg shadow-sm text-sm font-medium text-green-700 dark:text-green-300 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
                  >
                    <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                    </svg>
                    WhatsApp
                  </button>
                </div>
                <button
                  @click="closeModal"
                  class="inline-flex items-center justify-center px-6 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                >
                  Cerrar
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
import { ref, computed } from 'vue';
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import {
  CheckCircleIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/vue/24/outline';

interface RestaurantCreationData {
  restaurant: {
    id: number;
    name: string;
    subdomain: string;
    [key: string]: any;
  };
  admin_email: string;
  admin_password: string;
  restaurant_url: string;
  trial_days: number;
  trial_expires: string;
  welcome_message: string;
  shareable_message: string;
}

interface Props {
  isOpen: boolean;
  restaurantData: RestaurantCreationData | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const activeTab = ref<'details' | 'credentials' | 'steps'>('details');
const showPassword = ref(false);

const steps = [
  {
    title: '🌐 Accede al sistema',
    description: 'Ingresa a la URL proporcionada y usa las credenciales de administrador',
  },
  {
    title: '🔒 Cambia tu contraseña',
    description: 'Ve a tu perfil y selecciona "Cambiar Contraseña" para mayor seguridad',
  },
  {
    title: '⚙️ Configura tu restaurante',
    description: 'Completa la información: dirección, teléfono, logo, zona horaria y moneda',
  },
  {
    title: '🍽️ Crea tu menú',
    description: 'Agrega categorías y productos con precios y descripciones',
  },
  {
    title: '🪑 Configura tus mesas',
    description: 'Crea las mesas de tu restaurante con números y capacidades',
  },
  {
    title: '👥 Crea usuarios adicionales',
    description: 'Agrega meseros, cajeros y personal de cocina según tus necesidades',
  },
  {
    title: '🚀 Comienza a tomar pedidos',
    description: 'Usa las vistas de Mesas, Cocina y Caja para gestionar tu restaurante',
  },
];

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

const copyToClipboard = async (text: string | undefined, label: string) => {
  if (!text) return;
  
  try {
    await navigator.clipboard.writeText(text);
    // TODO: Mostrar toast de éxito
    if (import.meta.env.DEV) {
      console.log(`${label} copiado al portapapeles`);
    }
  } catch (err) {
    console.error('Error al copiar:', err);
  }
};

const copyShareableMessage = async () => {
  if (!props.restaurantData?.shareable_message) return;
  
  try {
    await navigator.clipboard.writeText(props.restaurantData.shareable_message);
    // TODO: Mostrar toast de éxito
    if (import.meta.env.DEV) {
      console.log('Mensaje copiado al portapapeles');
    }
  } catch (err) {
    console.error('Error al copiar:', err);
  }
};

const shareViaWhatsApp = () => {
  if (!props.restaurantData?.shareable_message) return;
  
  const text = encodeURIComponent(props.restaurantData.shareable_message);
  window.open(`https://wa.me/?text=${text}`, '_blank');
};

const closeModal = () => {
  emit('close');
};
</script>
