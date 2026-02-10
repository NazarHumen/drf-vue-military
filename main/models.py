from django.db import models


class Feedback(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "відгук"
        verbose_name_plural = "відгуки"
        db_table = "user_feedback"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
