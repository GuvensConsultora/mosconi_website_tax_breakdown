# Website Sale - Desglose completo de impuestos

## 1. Introducción

### Qué hace Odoo nativamente
Odoo eCommerce muestra un único precio en la tienda online (con o sin impuestos, según configuración fiscal). El usuario no ve el detalle de qué impuestos componen ese precio ni cuánto representa cada uno.

### Limitación
En Argentina (y otros países con múltiples impuestos como IVA, percepciones IIBB, impuestos internos), el cliente necesita ver el desglose antes de comprar. Sin esta información, el precio final puede generar confusión o desconfianza.

### Qué hace este módulo
Agrega debajo de cada precio — tanto en el listado de productos (`/shop`) como en la ficha individual del producto — un desglose que muestra:
- Precio sin impuestos
- Cada impuesto aplicado con su monto
- Total final con impuestos incluidos

---

## 2. Funcionamiento para el usuario final

### En el listado de productos (`/shop`)
Debajo del precio de cada producto aparece un bloque con:

| Campo | Ejemplo |
|-------|---------|
| Precio sin impuestos | $ 1.000,00 |
| IVA 21% | $ 210,00 |
| Percepción IIBB 3% | $ 30,00 |
| **Total** | **$ 1.240,00** |

### En la ficha del producto
Al ingresar al detalle de un producto, debajo del precio principal se muestra el mismo desglose con el formato:

- **Precio sin impuestos:** monto neto
- **Impuestos:** suma total de impuestos
- Detalle línea por línea de cada impuesto
- **Total:** precio final con impuestos

### Reglas de negocio
- Los impuestos mostrados son los configurados en el producto (`taxes_id`), filtrados por la compañía actual.
- El precio base se calcula usando la tarifa de precios (pricelist) activa del sitio web.
- La moneda se toma de la pricelist; si no existe, se usa la moneda de la compañía.

---

## 3. Parametrización

No requiere configuración adicional. El módulo funciona automáticamente al instalarlo.

### Requisitos previos
1. **Impuestos configurados en productos:** Ir a *Ventas > Productos > [Producto] > Pestaña "Información General"* y verificar que el campo *Impuestos del cliente* tenga los impuestos correspondientes (IVA, percepciones, etc.).
2. **Tarifa de precios activa:** Ir a *Sitio web > eCommerce > Tarifas de precios* y verificar que la tarifa del sitio web tenga una moneda asignada.

### Instalación
1. Copiar el módulo `mosconi_website_tax_breakdown` en el directorio de addons.
2. Activar modo desarrollador.
3. Ir a *Aplicaciones > Actualizar lista de aplicaciones*.
4. Buscar "Website Sale - Desglose completo de impuestos" e instalar.

---

## 4. Referencia técnica

### Arquitectura

```
mosconi_website_tax_breakdown/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── product_template.py      # Herencia de product.template
└── views/
    └── website_sale_templates.xml # Herencia de vistas QWeb
```

### Dependencias
- `website_sale`

### Modelo: `product.template` (herencia)

**Método `get_website_tax_breakdown(pricelist=None, partner=None)`**

Retorna un diccionario con el desglose fiscal del producto:

```python
{
    "price_excluded": float,   # Precio neto sin impuestos
    "price_included": float,   # Precio total con impuestos
    "taxes": [                 # Lista de impuestos aplicados
        {"name": str, "amount": float, ...}
    ],
    "currency": res.currency,  # Singleton de moneda
}
```

Lógica:
1. Resuelve pricelist → currency → partner con fallbacks seguros.
2. Obtiene la primera variante del producto.
3. Calcula precio usando `pricelist._get_product_price()`.
4. Aplica `taxes.compute_all()` filtrado por compañía actual.

### Vistas QWeb (herencia)

| Template | Hereda de | XPath | Ubicación |
|----------|-----------|-------|-----------|
| `product_item_price_tax_breakdown` | `website_sale.products_item` | `//div[contains(@class,'product_price')]` | Listado `/shop` |
| `product_page_price_tax_breakdown` | `website_sale.product_price` | `//h3[hasclass('css_editable_mode_hidden')]` | Ficha producto |

**Decisión técnica:** La ficha de producto hereda de `website_sale.product_price` (no de `website_sale.product`) porque el elemento de precio (`<span itemprop="price">`) vive en ese template, que se incluye via `t-call`. Los xpath de herencia QWeb solo operan sobre el arch del template padre directo.

### Seguridad
No define grupos ni permisos propios. El desglose es visible para todos los usuarios del sitio web (público y registrados).
