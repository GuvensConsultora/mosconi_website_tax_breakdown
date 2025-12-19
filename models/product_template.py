from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_website_tax_breakdown(self, pricelist, partner):
        self.ensure_one()

        currency = pricelist.currency_id
        price = pricelist.get_product_price(self, 1.0, partner)

        taxes = self.taxes_id.filtered(
            lambda t: t.company_id == self.env.company
        )

        res = taxes.compute_all(
            price,
            currency=currency,
            quantity=1.0,
            product=self,
            partner=partner,
        )

        return {
            "price_excluded": res["total_excluded"],
            "price_included": res["total_included"],
            "taxes": res["taxes"],
        }
