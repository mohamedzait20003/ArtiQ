"""
Roles Seeder
Seeds the default roles for the system
"""

import uuid
from lib import Seeder


class RolesSeeder(Seeder):
    """
    Seed the default roles for the system

    Creates the following roles:
    - Admin: Administrator role with full permissions
    - Manager: Manager role with management permissions
    - Visitor: Visitor role with read-only permissions
    """

    def run(self):
        """
        Create the default roles
        """
        print("Seeding default roles...")
 
        roles = [
            {
                "RoleID": str(uuid.uuid4()),
                "Name": "Admin",
                "Description": "Administrator role with full permissions",
                "PermissionIDs": []
            },
            {
                "RoleID": str(uuid.uuid4()),
                "Name": "Manager",
                "Description": "Manager role with management permissions",
                "PermissionIDs": []
            },
            {
                "RoleID": str(uuid.uuid4()),
                "Name": "Visitor",
                "Description": "Visitor role with read-only permissions",
                "PermissionIDs": []
            }
        ]

        # Create or update each role
        for role in roles:
            existing_role = self.db["Roles"].find_one({"Name": role["Name"]})
            if existing_role:
                print(f"  Role '{role['Name']}' already exists, skipping")
            else:
                self.create("Roles", role)
                print(f"  ✓ Created role: {role['Name']}")

        print("✓ Default roles seeded successfully!")
