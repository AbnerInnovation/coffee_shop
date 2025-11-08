import { ref, computed } from 'vue';

export interface MenuItem {
  id: number;
  name: string;
  price: number;
  discount_price?: number;
  has_variants: boolean;
  category?: { name: string } | string;
  variants?: any[];
}

export function useMenuCategories(menuItems: any) {
  const expandedCategories = ref<Set<string>>(new Set());

  // Group menu items by category
  const menuItemsByCategory = computed(() => {
    const groups: Record<string, any[]> = {};
    menuItems.value.forEach((item: any) => {
      const categoryName = (item.category && typeof item.category === 'object' && item.category.name) 
        ? item.category.name 
        : 'Uncategorized';
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
  const toggleCategory = (category: string) => {
    if (expandedCategories.value.has(category)) {
      expandedCategories.value.delete(category);
    } else {
      expandedCategories.value.add(category);
    }
  };

  // Check if category is expanded
  const isCategoryExpanded = (category: string): boolean => {
    return expandedCategories.value.has(category);
  };

  // Expand all categories
  const expandAllCategories = () => {
    expandedCategories.value = new Set(categoryNames.value);
  };

  // Collapse all categories
  const collapseAllCategories = () => {
    expandedCategories.value.clear();
  };

  return {
    expandedCategories,
    menuItemsByCategory,
    categoryNames,
    toggleCategory,
    isCategoryExpanded,
    expandAllCategories,
    collapseAllCategories
  };
}
