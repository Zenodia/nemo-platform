# Members

Types:

```python
from nemo_platform.types.members import (
    WorkspaceMember,
    WorkspaceMemberListResponse,
    WorkspaceMemberParam,
    WorkspaceMemberUpdate,
)
```

Methods:

- <code title="post /apis/entities/v2/workspaces/{workspace}/members">client.members.<a href="./src/nemo_platform/resources/members/members.py">create</a>(\*, workspace, \*\*<a href="src/nemo_platform/types/members/member_create_params.py">params</a>) -> <a href="./src/nemo_platform/types/members/workspace_member.py">WorkspaceMember</a></code>
- <code title="put /apis/entities/v2/workspaces/{workspace}/members/{principal_id}">client.members.<a href="./src/nemo_platform/resources/members/members.py">update</a>(principal_id, \*, workspace, \*\*<a href="src/nemo_platform/types/members/member_update_params.py">params</a>) -> <a href="./src/nemo_platform/types/members/workspace_member.py">WorkspaceMember</a></code>
- <code title="get /apis/entities/v2/workspaces/{workspace}/members">client.members.<a href="./src/nemo_platform/resources/members/members.py">list</a>(\*, workspace) -> <a href="./src/nemo_platform/types/members/workspace_member_list_response.py">WorkspaceMemberListResponse</a></code>
- <code title="delete /apis/entities/v2/workspaces/{workspace}/members/{principal_id}">client.members.<a href="./src/nemo_platform/resources/members/members.py">delete</a>(principal_id, \*, workspace, \*\*<a href="src/nemo_platform/types/members/member_delete_params.py">params</a>) -> <a href="./src/nemo_platform/types/shared/delete_response.py">DeleteResponse</a></code>
