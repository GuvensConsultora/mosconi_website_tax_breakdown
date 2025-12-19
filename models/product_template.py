from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_website_tax_breakdown(self, pricelist=None, partner=None):
        self.ensure_one()

        # 1️⃣ Resolver pricelist de forma segura
        if not pricelist:
            website = self.env["website"].get_current_website()
            pricelist = website.pricelist_id

        currency = pricelist.currency_id

        # 2️⃣ Resolver partner de forma segura
        if not partner:
            partner = self.env.user.partner_id

        # 3️⃣ Precio real según pricelist
        price = pricelist._get_product_price(self, 1.0, partner)

        # 4️⃣ Impuestos de la compañía actual
        taxes = self.taxes_id.filtered(
            lambda t: t.company_id == self.env.company
        )

        # 5️⃣ Cálculo fiscal REAL
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
