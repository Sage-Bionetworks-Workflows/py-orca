from orca.services.synapse import SynapseOps


def test_that_synapse_projects_can_be_explored(syn_project_id):
    ops = SynapseOps()
    children = ops.client.getChildren(syn_project_id, includeTypes=["folder", "file"])
    children_list = list(children)
    assert len(children_list) > 0
