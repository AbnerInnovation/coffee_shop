<template>
    <!-- WhatsApp floating button -->
    <a
        href="https://wa.me/526623843359?text=Hola!%20Me%20interesa%20obtener%20mas%20informacion%20sobre%20Cloud%20Restaurant"
        target="_blank"
        rel="noopener noreferrer"
        class="fixed bottom-6 right-6 z-50 flex items-center justify-center w-14 h-14 bg-green-500 hover:bg-green-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
        aria-label="Contactar por WhatsApp"
    >
        <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
    </a>

    <section class="max-w-6xl mx-auto px-6 py-16">
        <div
            class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-50 to-white dark:from-slate-900 dark:to-slate-900 ring-1 ring-inset ring-indigo-100 dark:ring-indigo-900/40 mb-14">
            <div
                class="pointer-events-none absolute -top-10 -right-10 h-40 w-40 bg-indigo-200/40 dark:bg-indigo-900/30 rounded-full blur-3xl">
            </div>
            <div
                class="pointer-events-none absolute -bottom-10 -left-10 h-40 w-40 bg-sky-200/40 dark:bg-sky-900/30 rounded-full blur-3xl">
            </div>
            <header class="text-center px-6 py-12 md:py-16">
                <p class="text-xs tracking-widest text-indigo-600 font-semibold">Presentamos</p>
                <div class="mt-4 flex justify-center">
                    <img 
                        v-if="isDark" 
                        src="@/assets/logos/DarkModeLogo.png" 
                        alt="Cloud Restaurant Logo" 
                        class="h-16 md:h-20 w-auto"
                    />
                    <img 
                        v-else 
                        src="@/assets/logos/Logo.png" 
                        alt="Cloud Restaurant Logo" 
                        class="h-16 md:h-20 w-auto"
                    />
                </div>
                <h1 class="mt-4 text-2xl md:text-4xl font-extrabold leading-tight text-slate-900 dark:text-slate-100">
                    Software para restaurantes moderno y listo para crecer
                </h1>
                <p class="mt-4 text-gray-600 dark:text-slate-300 max-w-2xl mx-auto">
                    Optimiza mesas, pedidos, cocina y caja en minutos. Escalable de taquerías a cadenas. Añade módulos
                    cuando los necesites.
                </p>
            </header>
        </div>

        <div class="mb-16">
            <h2 class="text-center text-2xl md:text-3xl font-bold text-slate-900 dark:text-slate-100 mb-8">
                ¿Por qué elegir {{ brand }}?
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div v-for="highlight in highlights" :key="highlight.title"
                    class="flex items-start gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-800 transition-all duration-200">
                    <div class="flex-shrink-0 w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                        <span class="text-2xl">{{ highlight.icon }}</span>
                    </div>
                    <div>
                        <h3 class="font-semibold text-slate-900 dark:text-slate-100 mb-1">{{ highlight.title }}</h3>
                        <p class="text-sm text-slate-600 dark:text-slate-400">{{ highlight.description }}</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="mb-12">
            <h2 class="sr-only">Vistas previas</h2>
            <div class="space-y-16">
                <section
                    v-for="(s, i) in previewSlides"
                    :key="i"
                    class="grid md:grid-cols-2 gap-8 lg:gap-12 items-center"
                >
                    <div :class="[ 'relative', i % 2 === 1 ? 'md:order-2' : 'md:order-1' ]">
                        <img
                            :src="s.imageUrl"
                            :alt="s.title || 'Vista previa'"
                            class="w-full h-auto object-cover rounded-3xl shadow-2xl ring-1 ring-black/5 dark:ring-white/10"
                            loading="lazy"
                        />
                        <div class="pointer-events-none absolute -inset-4 rounded-[2rem] blur-3xl opacity-20 bg-gradient-to-br from-indigo-400/30 to-sky-400/20 dark:from-indigo-500/10 dark:to-sky-500/10"></div>
                    </div>
                    <div :class="[ i % 2 === 1 ? 'md:order-1' : 'md:order-2' ]">
                        <h3 class="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
                            {{ s.title }}
                        </h3>
                        <p class="mt-3 text-slate-600 dark:text-slate-300 text-base md:text-lg leading-relaxed">
                            {{ s.caption }}
                        </p>
                        <div class="mt-6 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent"></div>
                    </div>
                </section>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <PricingCard v-for="plan in plans" :key="plan.name" :title="plan.title" :subtitle="plan.subtitle"
                :price="plan.price" :features="plan.features" :highlight="plan.highlight" cta-label="Contratar"
                cta-route-name="Register" />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div v-for="addon in addons" :key="addon.title"
                class="p-6 border rounded-2xl bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:shadow-md transition">
                <h3 class="font-semibold text-slate-900 dark:text-slate-100">{{ addon.title }}</h3>
                <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ addon.description }}</p>
                <ul v-if="addon.items" class="mt-3 text-sm space-y-1">
                    <li v-for="(item, idx) in addon.items" :key="idx" class="text-slate-700 dark:text-slate-300">• {{
                        item }}</li>
                </ul>
                <div v-else class="mt-4 text-lg font-extrabold text-slate-900 dark:text-slate-100">{{ addon.price }}
                </div>
            </div>
        </div>

        <div v-if="false" class="mb-12">
            <h3 class="text-lg font-semibold mb-3">Paquetes recomendados</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div v-for="pack in packs" :key="pack.name"
                    class="p-5 border rounded-2xl bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:shadow-md transition">
                    <strong class="text-slate-900 dark:text-slate-100">{{ pack.name }}</strong>
                    <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ pack.description }}</p>
                    <div class="mt-2 font-semibold text-slate-900 dark:text-slate-100">{{ pack.price }}</div>
                </div>
            </div>
        </div>

        <div v-if="false"
            class="bg-gray-50 dark:bg-slate-900 p-6 rounded-2xl border border-gray-200 dark:border-slate-700 ring-1 ring-inset ring-gray-100 dark:ring-slate-800">
            <h3 class="font-semibold text-slate-900 dark:text-slate-100">Sucursales y descuentos</h3>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
                Cada sucursal se toma como un negocio aparte. Ofrecemos descuento por volumen a partir de 3 sucursales —
                ejemplo: 20% de descuento en la tarifa mensual de cada sucursal.
            </p>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
                A partir de 3 sucursales incluimos el "Superusuario" para el dueño sin costo adicional.
            </p>
        </div>

        <div class="mt-8">
            <h3 class="font-semibold mb-2 text-slate-900 dark:text-slate-100">Notas</h3>
            <ul class="text-sm text-gray-600 dark:text-slate-400 space-y-1">
                <li>• Todos los precios son en moneda local y pueden ajustarse según integraciones adicionales.</li>
                <li>• Soporte básico por WhatsApp incluido en todos los planes (primer mes gratis).</li>
                <li>• Contratos anuales pueden negociarse con descuentos adicionales.</li>
            </ul>
        </div>
    </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PricingCard from '@/components/marketing/PricingCard.vue'
import { useTheme } from '@/composables/useTheme'

const brand = 'Cloud Restaurant'
const { isDark } = useTheme()

const highlights = [
        {
        icon: '⚡',
        title: 'Rápido, sencillo y moderno',
        description: 'Interfaz intuitiva y ágil diseñada para que tu equipo la domine en minutos.'
    },
    {
        icon: '☁️',
        title: 'Información almacenada en la nube',
        description: 'Tus datos seguros y accesibles en cualquier momento sin preocuparte por respaldos manuales.'
    },
    {
        icon: '📱',
        title: 'Compatible con móvil, tablet, PC',
        description: 'Accede desde cualquier dispositivo con total flexibilidad y comodidad.'
    },
    {
        icon: '🌐',
        title: 'Información disponible 24/7',
        description: 'Consulta tu negocio desde cualquier lugar del mundo, en cualquier momento.'
    },
    {
        icon: '🤝',
        title: 'Atención personalizada',
        description: 'Soporte dedicado para resolver tus dudas y ayudarte a crecer.'
    },
    {
        icon: '🛠️',
        title: 'Desarrollo de funciones extra',
        description: 'Solicita funcionalidades personalizadas adaptadas a las necesidades de tu negocio.'
    }
]

const plans = [
    {
        name: 'basic',
        title: 'Básico',
        subtitle: 'Ideal para negocios pequeños',
        price: '$600 / mes',
        features: [
            '1 usuario administrador',
            '1 usuario mesero',
            'Módulos: Mesas, Pedidos, Menú, Caja, Cocina',
            'Reportes básicos',
        ],
    },
    {
        name: 'pro',
        title: 'Pro',
        subtitle: 'Restaurantes familiares y con crecimiento',
        price: '$900 / mes',
        highlight: true,
        features: [
            '1 usuario administrador',
            '3 usuarios mesero',
            '1 usuario cajero',
            '1 usuario cocina',
            'Módulos básicos + reportes de ventas diarios',
        ],
    },
    {
        name: 'business',
        title: 'Business',
        subtitle: 'Restaurantes con mayor operación',
        price: '$1,300 / mes',
        features: [
            '2 usuarios administrador',
            '6 usuarios mesero',
            '2 usuarios cocina',
            '2 usuarios cajero',
            'Soporte mensual (1h)',
        ],
    },
    {
        name: 'enterprise',
        title: 'Enterprise',
        subtitle: 'Cadenas, franquicias y operaciones grandes',
        price: '$1,800 / mes',
        features: [
            '1 usuario dueño',
            '3 usuarios admin',
            '9 usuarios mesero',
            '3 usuarios cocina',
            '3 usuarios cajero',
            'Superusuario con visión multi-sucursal',
        ],
    },
]

const previewSlides = [
    {
        imageUrl: new URL('../assets/marketing/screenshots/tables.png', import.meta.url).toString(),
        title: 'Mesas en tiempo real',
        caption: 'Visualiza ocupación y estado de cada mesa al instante.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/menu.png', import.meta.url).toString(),
        title: 'Gestión de Menú',
        caption: 'Crea categorías, productos y modificadores fácilmente.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/orders.png', import.meta.url).toString(),
        title: 'Toma de pedidos',
        caption: 'Agiliza pedidos por mesa, para llevar o delivery.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/orders2.png', import.meta.url).toString(),
        title: 'Toma de pedidos',
        caption: 'Agiliza pedidos por mesa, para llevar o delivery.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/kitchen.png', import.meta.url).toString(),
        title: 'Pantalla de Cocina',
        caption: 'Prioriza y controla la preparación de platillos.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/cash.png', import.meta.url).toString(),
        title: 'Caja y cobros',
        caption: 'Cierra cuentas con múltiples métodos de pago.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/dashboard.png', import.meta.url).toString(),
        title: 'Dashboard',
        caption: 'Información general de la operación diaria'
    }

]

const addons = [
    {
        title: 'Capacitación',
        description: 'Sesiones en vivo y materiales.',
        items: [
            'Small: $900 (sesión de setup)',
            'Medium: $1,300',
            'Large: $1,800',
        ],
    },
    {
        title: 'Carga inicial de menú',
        description: 'Importación y configuración inicial.',
        price: '$300 (una vez)',
    },
    {
        title: 'Módulos extra (mensual)',
        description: '',
        items: [
            'Reportes avanzados: $200 / mes',
            'Inventario: $300 / mes',
            'Usuarios extra: $100 / usuario / mes',
            'Diseño personalizado: $400 / mes (o $700 setup + $100/mes mantenimiento)',
        ],
    },
]

const packs = [
    { name: 'Analítica', description: 'Reportes avanzados + exportes', price: '$300 / mes' },
    { name: 'Gestión', description: 'Inventario + reportes avanzados', price: '$400 / mes' },
    { name: 'Full Pro', description: 'Todos los extras + diseño', price: '$600 / mes' },
]
</script>
