import rules

from communikit.communities.rules import is_member

rules.add_perm("content.create_post", is_member)
