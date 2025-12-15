"""
Managers Seeder
Seeds manager users for the system
"""

import os
import uuid
import bcrypt
from lib import Seeder


class ManagersSeeder(Seeder):
    """
    Seed manager users for the system

    Creates several manager users with Manager role:
    - manager1 / Manager123!
    - manager2 / Manager123!
    - manager3 / Manager123!
    """

    def run(self):
        """
        Create manager users
        """
        print("Seeding manager users...")

        # Get manager role (should be created by RolesSeeder)
        existing_role = self.db["Roles"].find_one({"Name": "Manager"})
        if not existing_role:
            raise ValueError(
                "Manager role not found. Please run RolesSeeder first."
            )

        manager_role_id = existing_role["RoleID"]

        # Get salt from environment variable
        salt_from_env = os.environ.get('PASSWORD_SALT')
        if not salt_from_env:
            raise ValueError(
                "PASSWORD_SALT not found in environment variables. "
                "Run 'python scripts/generate_salt.py' to generate a salt "
                "and add it to your .env file."
            )

        # Define manager users
        managers = [
            {
                "username": "manager1",
                "name": "Manager One",
                "email": "manager1@ece30861.com",
                "password": "Manager123!"
            },
            {
                "username": "manager2",
                "name": "Manager Two",
                "email": "manager2@ece30861.com",
                "password": "Manager123!"
            },
            {
                "username": "manager3",
                "name": "Manager Three",
                "email": "manager3@ece30861.com",
                "password": "Manager123!"
            }
        ]

        # Create each manager
        for manager_data in managers:
            # Hash the password using bcrypt with salt from environment
            hashed_password = bcrypt.hashpw(
                manager_data["password"].encode('utf-8'),
                salt_from_env.encode('utf-8')
            ).decode('utf-8')

            manager_user = {
                "ID": str(uuid.uuid4()),
                "Username": manager_data["username"],
                "Name": manager_data["name"],
                "Email": manager_data["email"],
                "Password": hashed_password,
                "RoleID": manager_role_id
            }

            # Update or create the manager user
            existing_user = self.db["Users"].find_one({
                "Username": manager_data["username"]
            })

            if existing_user:
                print(
                    f"  Manager '{manager_data['username']}' "
                    f"already exists, skipping"
                )
            else:
                self.create("Users", manager_user)
                print(
                    f"  ✓ Created manager: {manager_data['username']} "
                    f"({manager_data['email']})"
                )

        print(f"""
        ✓ Manager users seeded successfully!
        Total managers created: {len(managers)}
        Default password for all managers: Manager123!
        """)
