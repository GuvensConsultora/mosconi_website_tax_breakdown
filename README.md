# Website Sale — Desglose de impuestos y descuentos

## 1. Introducción

### Qué hace Odoo nativamente
Odoo eCommerce muestra un único precio en la tienda online (con impuestos incluidos, según la configuración fiscal del sitio). El usuario no ve el detalle de qué impuestos componen ese precio ni cuánto representa cada uno. Tampoco indica el porcentaje de ahorro cuando un producto tiene descuento.

### Limitación
En Argentina, con múltiples impuestos (IVA, percepciones IIBB, impuestos internos), el cliente necesita ver el desglose antes de comprar. Además, en catálogos con descuentos por lista de precios, no se comunica visualmente cuánto se ahorra en porcentaje.

### Qué hace este módulo
- Muestra debajo de cada precio el desglose: precio sin impuestos + cada impuesto por nombre y monto.
- **No muestra el "Total"** (redundante con el precio principal ya visible).
- Cuando hay precio tachado por descuento, calcula y muestra el porcentaje de ahorro (`−33%`).

Aplica tanto en el listado de productos (`/shop`) como en la ficha individual del producto.

---

## 2. Funcionamiento para el usuario final

### En el listado de productos (`/shop`)

Debajo del precio de cada tarjeta aparece:

| Campo | Ejemplo |
|-------|---------|
| Precio sin imp. | $ 1.000,00 |
| IVA 21% | $ 210,00 |
| Percepción IIBB 3% | $ 30,00 |

Si el producto tiene descuento activo, el precio original aparece tachado con el porcentaje de ahorro al lado:

```
~~$ 1.500,00~~  −33%   →   $ 1.000,00
```

### En la ficha del producto

Debajo del bloque de precio principal se muestra el mismo desglose de impuestos. Si hay descuento, el porcentaje aparece junto al precio tachado:

```
~~$ 1.500,00~~  −33%
$ 1.000,00
  Precio sin imp.: $ 826,45
  IVA 21%: $ 173,55
```

### Reglas de negocio
- Los impuestos mostrados son los configurados en el producto (`taxes_id`), filtrados por la compañía activa.
- El precio base usa la tarifa de precios (pricelist) activa del sitio web.
- La moneda se toma de la pricelist; si no existe, se usa la moneda de la compañía.
- El porcentaje de descuento solo aparece si el precio reducido es menor al precio original (nunca muestra `0%`).

---

## 3. Parametrización

No requiere configuración adicional. Funciona automáticamente al instalarlo.

### Requisitos previos
1. **Impuestos en productos:** *Ventas > Productos > [Producto] > Pestaña "Información General"* → campo *Impuestos del cliente*.
2. **Tarifa de precios activa:** *Sitio web > eCommerce > Tarifas de precios* → verificar moneda asignada.
3. **Descuentos activos** (para mostrar %): *Sitio web > Configuración > Vender a precio con descuento* o usar listas de precios con descuento.

### Instalación
1. Copiar `mosconi_website_tax_breakdown` en el directorio de addons.
2. Activar modo desarrollador.
3. *Aplicaciones > Actualizar lista de aplicaciones*.
4. Buscar "Website Sale - Desglose de impuestos y descuentos" e instalar.

---

## 4. Referencia técnica

### Arquitectura

```
mosconi_website_tax_breakdown/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── product_template.py        # Herencia product.template
└── views/
    └── website_sale_templates.xml  # Herencia templates QWeb
```

### Dependencias
- `website_sale`

### Modelo: `product.template` (herencia)

**Método `get_website_tax_breakdown(pricelist=None, partner=None)`**

Retorna el desglose fiscal del producto:

```python
{
    "price_excluded": float,   # Precio neto sin impuestos
    "price_included": float,   # Precio total con impuestos (no se muestra en UI)
    "taxes": [{"name": str, "amount": float, ...}],
    "currency": res.currency,  # Singleton obligatorio para widget monetary
}
```

Lógica:
1. Resuelve pricelist → currency → partner con fallbacks seguros (nunca lanza error en render público).
2. Obtiene la primera variante del producto.
3. Calcula precio con `pricelist._get_product_price()`.
4. Aplica `taxes.compute_all()` filtrado por compañía activa.

### Vistas QWeb (herencia)

| Template | Hereda de | XPath target | Posición |
|----------|-----------|--------------|----------|
| `product_item_price_tax_breakdown` | `website_sale.products_item` | `//div[contains(@class,'product_price')]` | inside — desglose impuestos |
| `product_item_price_tax_breakdown` | `website_sale.products_item` | `//*[@name='product_base_price']` | after — badge % descuento |
| `product_page_price_tax_breakdown` | `website_sale.product_price` | `//div[@name='product_price_container']` | after — desglose impuestos |
| `product_page_price_tax_breakdown` | `website_sale.product_price` | `//span[@name='product_list_price']` | after — badge % descuento |

**Decisiones técnicas:**
- La ficha hereda de `website_sale.product_price` (no `website_sale.product`) porque el bloque de precio vive en ese sub-template incluido via `t-call`. Los xpath de herencia QWeb operan solo sobre el arch del template padre directo.
- No se muestra "Total" en el desglose: el precio principal ya es el precio con impuestos; repetirlo genera confusión.
- El badge de descuento usa `round()` para evitar decimales (ej: `33.33...%` → `−33%`).
- La condición de descuento verifica `price_reduce > 0` para no mostrar `−100%` en productos gratis.

### Seguridad
Sin grupos ni permisos propios. El desglose es visible para todos los usuarios del sitio (público y registrados).
