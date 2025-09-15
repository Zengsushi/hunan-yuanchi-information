# Generated manually for adding monitoring_enabled field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='iprecord',
            name='monitoring_enabled',
            field=models.BooleanField(default=False, help_text='是否启用对此IP的监控', verbose_name='启用监控'),
        ),
    ]