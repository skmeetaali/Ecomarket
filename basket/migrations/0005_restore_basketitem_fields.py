
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "basket",
            "0004_remove_basketitem_unique_product_per_basket_and_more",
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="basketitem",
                    name="basket",
                    field=models.ForeignKey(
                        to="basket.consolidatedbasket",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                    ),
                ),
                migrations.AddField(
                    model_name="basketitem",
                    name="product",
                    field=models.ForeignKey(
                        to="products.product",
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
                migrations.AddField(
                    model_name="basketitem",
                    name="quantity",
                    field=models.PositiveIntegerField(default=1),
                ),
                migrations.AddField(
                    model_name="basketitem",
                    name="price_at_addition",
                    field=models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                    ),
                ),
                migrations.AddField(
                    model_name="basketitem",
                    name="expected_delivery_date",
                    field=models.DateField(),
                ),
                migrations.AddField(
                    model_name="basketitem",
                    name="added_at",
                    field=models.DateTimeField(auto_now_add=True),
                ),
                migrations.AddConstraint(
                    model_name="basketitem",
                    constraint=models.UniqueConstraint(
                        fields=("basket", "product"),
                        name="unique_product_per_basket",
                    ),
                ),
            ],
        ),
    ]
