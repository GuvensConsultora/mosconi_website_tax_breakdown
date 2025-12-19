from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_website_tax_breakdown(self, pricelist=None, partner=None):
        self.ensure_one()

        website = self.env["website"].get_current_website()

        # --- Pricelist fallback (puede venir None o vacío en ciertos renders) ---
        pricelist = pricelist or (website and website.pricelist_id) or self.env["product.pricelist"]
        pricelist = pricelist[:1]  # fuerza singleton o vacío

        # --- Currency fallback (SIEMPRE devolver una currency singleton) ---
        currency = (pricelist.currency_id if pricelist and pricelist.currency_id else self.env.company.currency_id)[:1]
        if not currency:
            currency = self.env["res.currency"].sudo().search([], limit=1)

        # --- Partner fallback ---
        partner = partner or (website and website.user_id.partner_id) or self.env.user.partner_id

        # --- Producto (usar variante para precios/impuestos en Odoo 18) ---
        product = (self.product_variant_id or self.product_variant_ids[:1])
        if not product:
            return {
                "price_excluded": 0.0,
                "price_included": 0.0,
                "taxes": [],
                "currency": currency,
            }

        # --- Precio (Odoo 18: NO existe get_product_price) ---
        if pricelist:
            price = pricelist._get_product_price(product, 1.0, partner)
        else:
            price = product.lst_price

        taxes = product.taxes_id.filtered(lambda t: t.company_id == self.env.company)

        res = taxes.compute_all(
            price,
            currency=currency,
            quantity=1.0,
            product=product,
            partner=partner,
        )

        return {
            "price_excluded": res["total_excluded"],
            "price_included": res["total_included"],
            "taxes": res["taxes"],
            "currency": currency,  # <- SIEMPRE singleton
        }
