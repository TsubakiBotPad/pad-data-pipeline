How to process new ESBranches:

1) Add the ES definition in enemy_skill_info.py
    1a) Check the error log to see where the parameter is, if it is in 'branch_value' don't worry, otherwise make a new variable in the definition
2) Add a new variable in Context (enemy_skillset_processor.py) and ESCondition (enemy_skill_info.py)
3)loop_through_innter (enemy_skillset_processsor.py):
    a) add new return (probably List[int])
    b) define new branch array (see erase_attribute_branches)
    c) update the returns to return this array
    d) a new if isinstance(b, newESBranch), look at branchcombo/brancheraseattr for examples
4)loop_through (enemy_skillset_processsor.py):
    a) handle the new return from loop_through_inner
    b) look at how ESBranchCombo is being handled and just copy it
5)In enemy_skill_info edit ESCondition description and add new condition text (look at previous)

Following instructions are for updating debug_util. This might one day be unneeded?
6) Update "message Condition" in enemy_skills.proto (google protobuf3)
7) In debug_utils.py, go to format_condition and add to the atrocity
8) Go to behavior_to_proto in enemy_skill_proto.py and add to where you see item_condition.something
