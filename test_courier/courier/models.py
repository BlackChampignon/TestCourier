from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.BigIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(models.Model):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('courier', 'Courier'),
        ('store', 'Store'),
    ]

    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    def __str__(self):
        return self.name


class ToBeDelivered(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.BigIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Delivery(models.Model):
    courier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courier_deliveries', null=True)
    store = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_deliveries')
    time_created = models.DateTimeField(auto_now_add=True)
    time_delivered = models.DateTimeField(blank=True, null=True)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery #{self.id}"

    def get_total_amount(self):
        total = 0
        product_deliveries = ProductDelivery.objects.filter(delivery=self)
        for pd in product_deliveries:
            total += pd.items.price * pd.items.quantity
        return total


class ProductDelivery(models.Model):
    items = models.ForeignKey(ToBeDelivered, on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.items} in {self.delivery}"