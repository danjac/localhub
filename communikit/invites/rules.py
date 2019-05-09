import rules

from communikit.communities.rules import is_admin

rules.add_perm("invites.create_invite", is_admin)
