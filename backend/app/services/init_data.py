"""
Initialize default data for the platform.
Run this script to seed the database with admin user, default roles, and permissions.

Usage:
    python -m app.services.init_data
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker, init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.application import Application


async def init_permissions(session) -> dict:
    """Create default permission tree. Returns dict of code -> Permission."""
    permissions_data = [
        # App-level permissions
        {"parent_id": None, "name": "CMDB", "code": "app:cmdb", "type": "app", "path": None, "icon": "database", "sort_order": 1},
        {"parent_id": None, "name": "Agent Platform", "code": "app:agent", "type": "app", "path": None, "icon": "robot", "sort_order": 2},
        {"parent_id": None, "name": "Monitoring", "code": "app:monitor", "type": "app", "path": None, "icon": "monitor", "sort_order": 3},

        # Menu-level permissions - System Management
        {"parent_id": None, "name": "System Management", "code": "menu:system", "type": "menu", "path": "/system", "icon": "setting", "sort_order": 100},
        {"parent_id": None, "name": "User Management", "code": "menu:user", "type": "menu", "path": "/system/users", "icon": "user", "sort_order": 101},
        {"parent_id": None, "name": "Role Management", "code": "menu:role", "type": "menu", "path": "/system/roles", "icon": "team", "sort_order": 102},
        {"parent_id": None, "name": "Permission Management", "code": "menu:permission", "type": "menu", "path": "/system/permissions", "icon": "lock", "sort_order": 103},
        {"parent_id": None, "name": "Application Management", "code": "menu:application", "type": "menu", "path": "/system/applications", "icon": "appstore", "sort_order": 104},
        {"parent_id": None, "name": "Audit Log", "code": "menu:audit", "type": "menu", "path": "/system/audit", "icon": "file-search", "sort_order": 105},

        # Button-level permissions - User
        {"parent_id": None, "name": "Create User", "code": "btn:user:create", "type": "button", "path": None, "icon": None, "sort_order": 201},
        {"parent_id": None, "name": "Edit User", "code": "btn:user:edit", "type": "button", "path": None, "icon": None, "sort_order": 202},
        {"parent_id": None, "name": "Delete User", "code": "btn:user:delete", "type": "button", "path": None, "icon": None, "sort_order": 203},

        # Button-level permissions - Role
        {"parent_id": None, "name": "Create Role", "code": "btn:role:create", "type": "button", "path": None, "icon": None, "sort_order": 301},
        {"parent_id": None, "name": "Edit Role", "code": "btn:role:edit", "type": "button", "path": None, "icon": None, "sort_order": 302},
        {"parent_id": None, "name": "Delete Role", "code": "btn:role:delete", "type": "button", "path": None, "icon": None, "sort_order": 303},
        {"parent_id": None, "name": "Assign Permissions", "code": "btn:role:assign_perm", "type": "button", "path": None, "icon": None, "sort_order": 304},

        # Button-level permissions - Permission
        {"parent_id": None, "name": "Create Permission", "code": "btn:permission:create", "type": "button", "path": None, "icon": None, "sort_order": 401},
        {"parent_id": None, "name": "Edit Permission", "code": "btn:permission:edit", "type": "button", "path": None, "icon": None, "sort_order": 402},
        {"parent_id": None, "name": "Delete Permission", "code": "btn:permission:delete", "type": "button", "path": None, "icon": None, "sort_order": 403},

        # Button-level permissions - Application
        {"parent_id": None, "name": "Create Application", "code": "btn:application:create", "type": "button", "path": None, "icon": None, "sort_order": 501},
        {"parent_id": None, "name": "Edit Application", "code": "btn:application:edit", "type": "button", "path": None, "icon": None, "sort_order": 502},
        {"parent_id": None, "name": "Delete Application", "code": "btn:application:delete", "type": "button", "path": None, "icon": None, "sort_order": 503},
    ]

    code_to_perm = {}
    for perm_data in permissions_data:
        # Check if exists
        result = await session.execute(
            select(Permission).where(Permission.code == perm_data["code"])
        )
        perm = result.scalar_one_or_none()
        if not perm:
            perm = Permission(**perm_data)
            session.add(perm)
            await session.flush()
        code_to_perm[perm.code] = perm

    # Set parent relationships
    menu_parent_map = {
        "menu:user": "menu:system",
        "menu:role": "menu:system",
        "menu:permission": "menu:system",
        "menu:application": "menu:system",
        "menu:audit": "menu:system",
        "btn:user:create": "menu:user",
        "btn:user:edit": "menu:user",
        "btn:user:delete": "menu:user",
        "btn:role:create": "menu:role",
        "btn:role:edit": "menu:role",
        "btn:role:delete": "menu:role",
        "btn:role:assign_perm": "menu:role",
        "btn:permission:create": "menu:permission",
        "btn:permission:edit": "menu:permission",
        "btn:permission:delete": "menu:permission",
        "btn:application:create": "menu:application",
        "btn:application:edit": "menu:application",
        "btn:application:delete": "menu:application",
    }

    for child_code, parent_code in menu_parent_map.items():
        if child_code in code_to_perm and parent_code in code_to_perm:
            code_to_perm[child_code].parent_id = code_to_perm[parent_code].id

    await session.flush()
    return code_to_perm


async def init_roles(session, permissions: dict) -> dict:
    """Create default roles."""
    roles_data = [
        {
            "name": "Super Admin",
            "code": "admin",
            "description": "Full access to all resources",
        },
        {
            "name": "Operator",
            "code": "operator",
            "description": "Can manage applications and view audit logs",
        },
        {
            "name": "Viewer",
            "code": "viewer",
            "description": "Read-only access to portal resources",
        },
    ]

    code_to_role = {}
    for role_data in roles_data:
        result = await session.execute(
            select(Role).where(Role.code == role_data["code"])
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(**role_data)
            session.add(role)
            await session.flush()
        code_to_role[role.code] = role

    # Assign permissions to operator role
    operator_role = code_to_role.get("operator")
    if operator_role:
        result = await session.execute(
            select(Role).options(selectinload(Role.permissions)).where(Role.id == operator_role.id)
        )
        operator_role = result.scalar_one()
        if not operator_role.permissions:
            operator_perms = [
                permissions[code] for code in [
                    "app:cmdb", "app:agent", "app:monitor",
                    "menu:system", "menu:application", "menu:audit",
                    "btn:application:create", "btn:application:edit",
                ] if code in permissions
            ]
            operator_role.permissions = operator_perms

    # Assign permissions to viewer role
    viewer_role = code_to_role.get("viewer")
    if viewer_role:
        result = await session.execute(
            select(Role).options(selectinload(Role.permissions)).where(Role.id == viewer_role.id)
        )
        viewer_role = result.scalar_one()
        if not viewer_role.permissions:
            viewer_perms = [
                permissions[code] for code in [
                    "app:cmdb", "app:agent",
                    "menu:system", "menu:user", "menu:role", "menu:permission",
                ] if code in permissions
            ]
            viewer_role.permissions = viewer_perms

    await session.flush()
    return code_to_role


async def init_admin_user(session, roles: dict):
    """Create default admin user."""
    result = await session.execute(
        select(User).where(User.username == "admin")
    )
    admin = result.scalar_one_or_none()

    if not admin:
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            nickname="Administrator",
            email="admin@yw.ops.com",
            status=1,
        )
        session.add(admin)
        await session.flush()

        # Assign admin role
        admin_role = roles.get("admin")
        if admin_role:
            result = await session.execute(
                select(User).options(selectinload(User.roles)).where(User.id == admin.id)
            )
            admin = result.scalar_one()
            admin.roles = [admin_role]
            await session.flush()

        print(f"[INIT] Created admin user (username: admin, password: admin123)")
    else:
        print(f"[INIT] Admin user already exists, skipping.")


async def main():
    """Run all initialization steps."""
    print("[INIT] Starting database initialization...")

    # Create tables
    await init_db()
    print("[INIT] Database tables created/verified.")

    async with async_session_maker() as session:
        try:
            permissions = await init_permissions(session)
            print(f"[INIT] Initialized {len(permissions)} permissions.")

            roles = await init_roles(session, permissions)
            print(f"[INIT] Initialized {len(roles)} roles.")

            await init_admin_user(session, roles)

            await session.commit()
            print("[INIT] Database initialization completed successfully!")
        except Exception as e:
            await session.rollback()
            print(f"[INIT ERROR] {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
