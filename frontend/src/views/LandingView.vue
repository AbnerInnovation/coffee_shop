<template>
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
                <h1 class="mt-2 text-3xl md:text-5xl font-extrabold leading-tight text-slate-900 dark:text-slate-100">
                    {{ brand }} — software para restaurantes moderno y listo para crecer
                </h1>
                <p class="mt-4 text-gray-600 dark:text-slate-300 max-w-2xl mx-auto">
                    Optimiza mesas, pedidos, cocina y caja en minutos. Escalable de taquerías a cadenas. Añade módulos
                    cuando los necesites.
                </p>
                <div class="mt-6 flex items-center justify-center gap-3">
                    <RouterLink :to="{ name: 'Register' }"
                        class="inline-flex items-center justify-center rounded-lg px-5 py-2.5 bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-slate-900">
                        Probar gratis
                    </RouterLink>
                    <RouterLink :to="{ name: 'Login' }"
                        class="inline-flex items-center justify-center rounded-lg px-5 py-2.5 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-slate-200 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:hover:bg-slate-800 transition shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-slate-900">
                        Iniciar sesión
                    </RouterLink>
                </div>
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

const brand = 'Cloud Restaurant'

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
