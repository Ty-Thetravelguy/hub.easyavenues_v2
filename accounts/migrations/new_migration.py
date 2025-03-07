from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_remove_customuser_username'),  # Update this to your last migration
        ('account', '0002_email_max_length'),  # This is allauth's migration
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Update the foreign key to point to your custom user table
            sql="""
            DROP TABLE IF EXISTS account_emailaddress;
            CREATE TABLE "account_emailaddress" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "email" varchar(254) NOT NULL UNIQUE,
                "verified" bool NOT NULL,
                "primary" bool NOT NULL,
                "user_id" integer NOT NULL REFERENCES "accounts_customuser" ("id") ON DELETE CASCADE
            );
            CREATE UNIQUE INDEX "account_emailaddress_user_id_primary_key" ON "account_emailaddress" ("user_id", "primary");
            CREATE UNIQUE INDEX "account_emailaddress_user_id_email_key" ON "account_emailaddress" ("user_id", "email");
            """,
            # Reverse SQL - If you need to roll back
            reverse_sql="""
            DROP TABLE IF EXISTS account_emailaddress;
            """
        )
    ] 