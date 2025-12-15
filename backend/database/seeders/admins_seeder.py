"""
Admins Seeder
Seeds additional admin users for the system
"""

import os
import uuid
import bcrypt
from lib import Seeder


class AdminsSeeder(Seeder):
    """
    Seed additional admin users for the system

    Creates several admin users with Admin role:
    - admin1 / Admin123!
    - admin2 / Admin123!
    - admin3 / Admin123!
    """

    def run(self):
        """
        Create additional admin users
        """
        print("Seeding additional admin users...")

        # Get admin role (should be created by RolesSeeder)
        existing_role = self.db["Roles"].find_one({"Name": "Admin"})
        if not existing_role:
            raise ValueError(
                "Admin role not found. Please run RolesSeeder first."
            )

        admin_role_id = existing_role["RoleID"]

        # Get salt from environment variable
        salt_from_env = os.environ.get('PASSWORD_SALT')
        if not salt_from_env:
            raise ValueError(
                "PASSWORD_SALT not found in environment variables. "
                "Run 'python scripts/generate_salt.py' to generate a salt "
                "and add it to your .env file."
            )

        # Define admin users
        admins = [
            {
                "username": "admin1",
                "name": "Admin One",
                "email": "admin1@ece30861.com",
                "password": "Admin123!"
            },
            {
                "username": "admin2",
                "name": "Admin Two",
                "email": "admin2@ece30861.com",
                "password": "Admin123!"
            },
            {
                "username": "admin3",
                "name": "Admin Three",
                "email": "admin3@ece30861.com",
                "password": "Admin123!"
            }
        ]

        # Create each admin
        for admin_data in admins:
            # Hash the password using bcrypt with salt from environment
            hashed_password = bcrypt.hashpw(
                admin_data["password"].encode('utf-8'),
                salt_from_env.encode('utf-8')
            ).decode('utf-8')

            admin_user = {
                "ID": str(uuid.uuid4()),
                "Username": admin_data["username"],
                "Name": admin_data["name"],
                "Email": admin_data["email"],
                "Password": hashed_password,
                "RoleID": admin_role_id
            }

            # Update or create the admin user
            existing_user = self.db["Users"].find_one({
                "Username": admin_data["username"]
            })

            if existing_user:
                print(
                    f"  Admin '{admin_data['username']}' "
                    f"already exists, skipping"
                )
            else:
                self.create("Users", admin_user)
                print(
                    f"  ✓ Created admin: {admin_data['username']} "
                    f"({admin_data['email']})"
                )

        print(f"""
        ✓ Additional admin users seeded successfully!
        Total admins created: {len(admins)}
        Default password for all admins: Admin123!
        """)
