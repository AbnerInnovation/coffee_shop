-- backend/db/seed_menu.sql
-- Seed menu data for coffee-shop-admin
-- Schema aligned with backend/app/models/menu.py and backend/app/models/base.py

START TRANSACTION;

-- Categories upsert (name is UNIQUE per models)
INSERT INTO categories (name, description, created_at, updated_at)
VALUES 
  ('BAGUETTES', 'Baguettes del menú', NOW(), NOW())
ON DUPLICATE KEY UPDATE
  description = VALUES(description),
  updated_at = NOW();

-- Capture category ids
SET @cat_baguettes_id = (SELECT id FROM categories WHERE name = 'BAGUETTES' LIMIT 1);

-- BAGUETTES
-- 1) BAGUETTE
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'BAGUETTE',
  'Nuestro pan artesanal, acompañado de pechuga con queso chihuahua como costra. Lechuga Italiana, tomate y cebolla asada. Salsa a elegir.',
  78.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @baguette_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@baguette_id, 'Con papas', 118.00, 1, NOW(), NOW());

-- 2) BAGUETTE GUACAMOLE
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'BAGUETTE GUACAMOLE',
  'Nuestro pan artesanal, acompañado pechuga con queso chihuahua como costra. Lechuga Italiana, tomate y cebolla asada, queso amarillo y guacamole.',
  80.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @baguette_guac_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@baguette_guac_id, 'Con papas', 120.00, 1, NOW(), NOW());

-- 3) BAGUETTE CHAMPIÑONES
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'BAGUETTE CHAMPIÑONES',
  'Nuestro pan artesanal de la casa, mayonesa al gusto, pechuga, champiñones con costra de queso chihuahua, y lechuga.',
  85.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @baguette_champ_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@baguette_champ_id, 'Con papas', 125.00, 1, NOW(), NOW());

-- 4) CUERNITO
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'CUERNITO',
  'Cuernito dulce, pechuga, mayonesa al gusto, costra de queso chihuahua, lechuga y tomate.',
  60.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @cuernito_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@cuernito_id, 'Con papas', 75.00, 1, NOW(), NOW());

-- SALSAS como item con variantes (precio 0)
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'SALSAS',
  'Opciones de salsa',
  0.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @salsas_item_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@salsas_item_id, 'Italiano', 0.00, 1, NOW(), NOW()),
  (@salsas_item_id, 'Chipotle', 0.00, 1, NOW(), NOW()),
  (@salsas_item_id, 'BBQ', 0.00, 1, NOW(), NOW());

-- EXTRAS como item con variantes ($30 c/u)
INSERT INTO menu_items (name, description, price, category_id, is_available, image_url, created_at, updated_at)
VALUES (
  'EXTRAS',
  'Extras para agregar',
  0.00,
  @cat_baguettes_id,
  1,
  NULL,
  NOW(),
  NOW()
);
SET @extras_item_id = LAST_INSERT_ID();
INSERT INTO menu_item_variants (menu_item_id, name, price, is_available, created_at, updated_at)
VALUES
  (@extras_item_id, 'Guacamole', 30.00, 1, NOW(), NOW()),
  (@extras_item_id, 'Champiñon', 30.00, 1, NOW(), NOW()),
  (@extras_item_id, 'Queso', 30.00, 1, NOW(), NOW()),
  (@extras_item_id, 'Pechuga', 30.00, 1, NOW(), NOW());

COMMIT;
