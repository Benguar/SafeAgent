package safeagent.engine

import data.block
import future.keywords.if
import future.keywords.contains


default block_prompt := false
default avg_weight := 0
default violation_ids := []
deny contains info if {
    some rule in block
    regex.match(rule.pattern, input.prompt)
    info := {
        "id": rule.id,
        "weight": rule.weight
    }
}
block_prompt := true if {
    count(deny) > 0  
}
total_weight := sum([w | some d in deny; w := d.weight])
total_violations := count(deny)
violation_ids := [id | some d in deny; id := d.id]

avg_weight := total_weight / total_violations if {
    total_violations > 0
}


block_response := {
    "block_prompt": block_prompt,
    "weight": avg_weight,
    "violation_ids": violation_ids
}