package authz_test

import data.authz

# Test data for evaluation benchmark endpoints (aligned with static-authz)
evaluation_test_data := {
    "roles": {
        "Viewer": {
            "permissions": ["evaluation.benchmarks.read", "evaluation.benchmarks.list"]
        },
        "Editor": {
            "includes": ["Viewer"],
            "permissions": ["evaluation.benchmarks.create", "evaluation.benchmarks.delete"]
        }
    },
    "endpoints": {
        "/apis/evaluation/v2/workspaces/{workspace}/benchmarks": {
            "get": {
                "permissions": ["evaluation.benchmarks.list"],
                "scopes": ["evaluation:read"]
            },
            "post": {
                "permissions": ["evaluation.benchmarks.create"],
                "scopes": ["evaluation:write"]
            }
        },
        "/apis/evaluation/v2/workspaces/{workspace}/benchmarks/{name}": {
            "get": {
                "permissions": ["evaluation.benchmarks.read"],
                "scopes": ["evaluation:read"]
            },
            "delete": {
                "permissions": ["evaluation.benchmarks.delete"],
                "scopes": ["evaluation:write"]
            }
        }
    },
    "workspaces": {
        "team-ml": {},
        "public-evals": {}
    },
    "principals": {
        "user@example.com": {
            "workspaces": {
                "team-ml": ["Editor"]
            }
        },
        # Wildcard principal grants Viewer access to public-evals for all authenticated users
        "*": {
            "workspaces": {
                "public-evals": ["Viewer"]
            }
        }
    }
}

# Test 1: GET benchmark with workspace in path
test_evaluation_config_get_with_workspace_no_check_header if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "GET",
        "path": "/apis/evaluation/v2/workspaces/team-ml/benchmarks/eval-config-123",
        "scopes": ["evaluation:read"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as evaluation_test_data.workspaces
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == true
    result.headers["X-NMP-Authorized"] == "true"
}

# Test 2: POST create benchmark (collection)
test_evaluation_config_put_with_workspace_no_check_header if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "POST",
        "path": "/apis/evaluation/v2/workspaces/team-ml/benchmarks",
        "scopes": ["evaluation:write"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as evaluation_test_data.workspaces
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == true
    result.headers["X-NMP-Authorized"] == "true"
}

# Test 3: DELETE benchmark with workspace in path
test_evaluation_config_delete_with_workspace_no_check_header if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "DELETE",
        "path": "/apis/evaluation/v2/workspaces/team-ml/benchmarks/eval-config-123",
        "scopes": ["evaluation:write"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as evaluation_test_data.workspaces
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == true
    result.headers["X-NMP-Authorized"] == "true"
}

# Test 4: GET benchmark list for a workspace
test_evaluation_config_list_without_workspace_has_check_header if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "GET",
        "path": "/apis/evaluation/v2/workspaces/team-ml/benchmarks",
        "scopes": ["evaluation:read"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as evaluation_test_data.workspaces
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == true
}

# Test 5: Verify workspace extraction from evaluation benchmark path
test_workspace_extraction_from_evaluation_config_path if {
    workspace := authz.extract_workspace_from_path("/apis/evaluation/v2/workspaces/team-ml/benchmarks/eval-config-123") with data.authz.endpoints as evaluation_test_data.endpoints

    workspace == "team-ml"
}

# Test 6: Access denied to benchmark in workspace without permission
test_evaluation_config_access_denied_without_permission if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "GET",
        "path": "/apis/evaluation/v2/workspaces/other-team/benchmarks/eval-config-123",
        "scopes": ["evaluation:read"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as {
        "team-ml": {},
        "other-team": {}
    }
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == false
    result.headers["X-NMP-Authorized"] == "false"
}

# Test 7: Access to public workspace evaluation benchmark
test_evaluation_config_access_public_workspace if {
    result := authz.allow with input as {
        "principal_id": "user@example.com",
        "method": "GET",
        "path": "/apis/evaluation/v2/workspaces/public-evals/benchmarks/eval-config-456",
        "scopes": ["evaluation:read"]
    }
    with data.authz.roles as evaluation_test_data.roles
    with data.authz.endpoints as evaluation_test_data.endpoints
    with data.authz.workspaces as evaluation_test_data.workspaces
    with data.authz.principals as evaluation_test_data.principals

    result.allowed == true
    result.headers["X-NMP-Authorized"] == "true"
}
