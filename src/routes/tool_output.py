from fastapi import APIRouter,status,HTTPException,Request,BackgroundTasks
from src.schemas.classes import ToolInput
from src.db.modules import log_tool_output
from policy.module import policy
import asyncio
router = APIRouter()

#how to track the id in memory
z = {
  "role": "tool",
  "tool_call_id": "call_vctR_hungary_092",
  "name": "search_pinecone_db",
  "content": "Source 1 | Fidesz Supermajority: In the 2022 Hungarian parliamentary elections, Prime Minister Viktor Orbán's Fidesz party, in alliance with the KDNP, secured a sweeping victory, retaining their two-thirds supermajority in the National Assembly. Despite facing a united opposition front for the first time, Fidesz captured over 54% of the popular vote. Orbán framed the election as a choice between peace and drawing Hungary into the neighboring Ukraine conflict, a message that resonated strongly with rural voters and solidified his mandate for a fourth consecutive term.\n\n Source 2 | Opposition Defeat: The United for Hungary coalition, led by conservative rural mayor Péter Márki-Zay, suffered a heavy defeat despite early polling suggesting a tight race. The six-party alliance, spanning from left-wing to right-wing factions, only managed to secure roughly 34% of the vote. Márki-Zay conceded the election shortly after the preliminary results were announced, citing an uneven playing field dominated by state-aligned media and gerrymandered voting districts that heavily favored the ruling incumbent party.\n\n Source 3 | OSCE Observer Report: Following the election, the Organization for Security and Co-operation in Europe (OSCE) released a monitoring report concluding that while the Hungarian elections were well-managed and offered real choices, the process was marred by an unequal playing field. The observer mission highlighted pervasive overlapping of government and ruling party messaging, biased media coverage, and opaque campaign financing, all of which provided an undue advantage to Fidesz and restricted the opposition's ability to compete fairly."
}
# print(z["content"])
#use System directive 
@router.post("", status_code=status.HTTP_200_OK)
async def tool_output(output: ToolInput,request: Request,background_task: BackgroundTasks):
    sanitize_policy = request.app.state.sanitize_policy
    bloom_filter = request.app.state.bloom_filter
    content = policy(output.content)
    content.normalize_prompt
    async with asyncio.TaskGroup() as tg:
      sanitize_task = tg.create_task(asyncio.to_thread(content.sanitize_prompt, sanitize_policy=sanitize_policy, bloom_filter=bloom_filter))
    regex_sanitize,regex_decision,sanitized_document,sanitized_words  = sanitize_task.result()
    final_content = "<RAG Document>"+sanitized_document+"</RAG Document>"
    if regex_decision == "SANITIZE" or len(sanitized_words) > 0:
       decision = "SANITIZE"
    else:
       decision = "ALLOW"
    output.content = final_content
    background_task.add_task(log_tool_output,output,decision,sanitized_words)
    return final_content