/**
 * Composable para datos estáticos del landing page
 */
export function useLandingData() {
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
      name: 'starter',
      title: 'Starter',
      subtitle: 'Food trucks y cafeterías pequeñas',
      price: '$399 / mes',
      features: [
        '1 admin + 1 mesero + 1 cajero + 1 cocina',
        'Hasta 10 mesas',
        '20 productos en menú',
        'Módulo de Cocina incluido 🎁',
        'Módulo de Ingredientes incluido 🎁',
        'Reportes básicos (7 días)',
      ],
    },
    {
      name: 'basic',
      title: 'Básico',
      subtitle: 'Taquerías y restaurantes pequeños',
      price: '$699 / mes',
      features: [
        '1 admin + 3 meseros + 1 cocina',
        'Hasta 20 mesas',
        '150 productos en menú',
        'Módulo de Ingredientes incluido 🎁',
        'Reportes básicos (15 días)',
      ],
    },
    {
      name: 'pro',
      title: 'Pro',
      subtitle: 'Restaurantes familiares en crecimiento',
      price: '$999 / mes',
      highlight: true,
      features: [
        '1 admin + 4 meseros + 2 cajeros + 2 cocina',
        'Hasta 35 mesas',
        '400 productos en menú',
        'Ingredientes + Reportes Avanzados incluidos 🎁'
      ],
    },
    {
      name: 'business',
      title: 'Business',
      subtitle: 'Restaurantes establecidos',
      price: '$1,499 / mes',
      features: [
        '2 admin + 8 meseros + 3 cajeros + 3 cocina',
        'Hasta 60 mesas',
        '800 productos en menú',
        'Todos los módulos incluidos 🎁',
      ],
    },
    {
      name: 'enterprise',
      title: 'Enterprise',
      subtitle: 'Cadenas y franquicias',
      price: '$2,199 / mes',
      features: [
        '1 dueño + 4 admin + 15 meseros + 5 cajeros + 5 cocina',
        'Hasta 150 mesas',
        'Productos ilimitados',
        'Multi-sucursal + Gerente de cuenta',
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
      title: 'Módulos Extra',
      description: 'Agrega funcionalidades adicionales',
      items: [
        'Inventario: $199/mes',
        'Reportes Avanzados: $149/mes',
      ],
    },
    {
      title: 'Recursos Adicionales',
      description: 'Incrementa los límites de tu plan',
      items: [
        'Usuario Extra: $79/mes',
        '10 Mesas Extra: $39/mes',
        '100 Productos Extra: $79/mes',
      ],
    },
    {
      title: 'Servicios One-Time',
      description: 'Pago único',
      items: [
        'Capacitación Small: $900',
        'Capacitación Medium: $1,300',
        'Capacitación Large: $1,800',
        'Carga de Menú: $300',
        'Diseño Personalizado: desde $400/mes',
      ],
    },
  ]

  const trialFeatures = [
    { icon: '✓', text: '35 mesas' },
    { icon: '✓', text: '400 productos' },
    { icon: '✓', text: 'Reportes avanzados' }
  ]

  const trialLimitations = [
    { label: 'Duración', value: '14 días calendario desde el registro' },
    { label: 'Límites', value: '35 mesas, 400 productos, 9 usuarios totales' },
    { label: 'Funciones', value: 'Acceso completo a Plan Pro (ingredientes, reportes avanzados, cocina)' },
    { label: 'Datos', value: 'Se conservan al actualizar a plan de pago' },
    { label: 'Sin compromiso', value: 'No se requiere tarjeta de crédito' }
  ]

  const additionalInfo = [
    'Todos los precios son en MXN y pueden ajustarse según integraciones adicionales',
    'Soporte básico por WhatsApp incluido en todos los planes',
    'Pago anual: 25% de descuento (3 meses gratis)',
    'Descuentos por volumen disponibles para 3+ sucursales (15-35% off)',
    'Upgrade/downgrade disponible en cualquier momento'
  ]

  return {
    highlights,
    plans,
    previewSlides,
    addons,
    trialFeatures,
    trialLimitations,
    additionalInfo
  }
}
