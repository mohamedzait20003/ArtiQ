"""
Default Admin User Seeder
Seeds the default admin user for authentication as specified in the API spec
"""

import uuid
import bcrypt
from include import Seeder


class DefaultAdminSeeder(Seeder):
    """
    Seed the default admin user for authentication

    Creates the user:
    - Username: ece30861defaultadminuser
    - Password: correcthorsebatterystaple123(!__+@**(A'"`;DROP TABLE artifacts;
    - Name: ece30861defaultadminuser
    - is_admin: true
    """

    def run(self):
        """
        Create the default admin user
        """
        print("Seeding default admin user...")

        # Get admin role (should be created by RolesSeeder)
        existing_role = self.db["Roles"].find_one({"Name": "Admin"})
        if not existing_role:
            raise ValueError(
                "Admin role not found. Please run RolesSeeder first."
            )

        admin_role_id = existing_role["RoleID"]

        # Create default admin user
        user_id = str(uuid.uuid4())
        username = "ece30861defaultadminuser"
        password = (
            "correcthorsebatterystaple123(!__+@**(A'\"`; DROP TABLE artifacts;"
        )

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        default_admin_user = {
            "ID": user_id,
            "Username": username,
            "Name": username,
            "Email": f"{username}@ece30861.com",
            "Password": hashed_password,
            "RoleID": admin_role_id
        }

        # Update or create the default admin user
        self.update_or_create(
            collection="Users",
            filter_query={"Username": username},
            document=default_admin_user
        )

        print(f"""
        ✓ Default admin user seeded successfully!
        Username: {username}
        Password: {password}
        Role: Admin
        ID: {user_id}
        """)
