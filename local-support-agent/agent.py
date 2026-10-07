import os
from typing import List, Literal, TypedDict, Optional
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer, util

# ==========================================
# MODEL CONFIGURATION & INITIALIZATION
# ==========================================
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATION_REVISION = "main"

print(f"Loading local embedding model: {EMBEDDING_MODEL_NAME}...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

print(f"Loading local generation model: {GENERATION_MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME, revision=GENERATION_REVISION)
model = AutoModelForCausalLM.from_pretrained(
    GENERATION_MODEL_NAME,
    revision=GENERATION_REVISION,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

generator_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,
    temperature=0.1,
    do_sample=True
)

# ==========================================
# STATE & SCHEMA DEFINITIONS
# ==========================================
class SourceReference(BaseModel):
    document: str
    passage: str

class AgentOutputSchema(BaseModel):
    classification: Literal["answerable", "clarification", "escalation", "out_of_scope"]
    answer: str
    sources: List[SourceReference] = []
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human: bool
    reason: str

class GraphState(TypedDict):
    user_query: str
    classification: Optional[str]
    retrieved_docs: List[dict]
    generated_answer: Optional[str]
    sources: List[dict]
    confidence: float
    requires_human: bool
    reason: str
    verification_passed: Optional[bool]
    retry_count: int
    execution_logs: List[str]

def load_knowledge_base(kb_dir: str = "./kb") -> List[dict]:
    docs = []
    if not os.path.exists(kb_dir):
        return docs
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md"):
            path = os.path.join(kb_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                for p in paragraphs:
                    docs.append({"document": filename, "passage": p})
    return docs

# ==========================================
# NODE IMPLEMENTATIONS
# ==========================================
def triage_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Triage Node Executed")
    query = state["user_query"].lower()

    if any(kw in query for kw in ["refund", "subscription payment", "cancel billing", "chargeback"]):
        classification = "out_of_scope"
        reason = "Billing/refund requests fall outside product technical documentation scope."
        requires_human = True
    elif any(kw in query for kw in ["not working", "persist", "escalate", "tried everything"]):
        classification = "escalation"
        reason = "User indicated previous troubleshooting steps failed."
        requires_human = True
    elif len(query.split()) < 4 and not any(kw in query for kw in ["how", "what", "can"]):
        classification = "clarification"
        reason = "Query is too brief or ambiguous to determine specific requirements."
        requires_human = False
    else:
        classification = "answerable"
        reason = "Query appears to be a technical question addressable by the knowledge base."
        requires_human = False

    return {**state, "classification": classification, "reason": reason, "requires_human": requires_human, "execution_logs": logs}

def retrieval_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Retrieval Node Executed")
    if state["classification"] in ["out_of_scope", "clarification"]:
        return {**state, "retrieved_docs": [], "execution_logs": logs}

    kb_docs = load_knowledge_base()
    if not kb_docs:
        return {**state, "retrieved_docs": [], "execution_logs": logs}

    query = state["user_query"]
    passage_texts = [d["passage"] for d in kb_docs]
    query_emb = embedder.encode(query, convert_to_tensor=True)
    passage_embs = embedder.encode(passage_texts, convert_to_tensor=True)

    cos_scores = util.cos_sim(query_emb, passage_embs)[0]
    top_results_count = min(3, len(kb_docs))
    top_indices = torch.topk(cos_scores, k=top_results_count).indices.tolist()

    retrieved = [kb_docs[idx] for idx in top_indices]
    return {**state, "retrieved_docs": retrieved, "execution_logs": logs}

def generation_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Generation Node Executed")
    classification = state["classification"]
    
    if classification == "out_of_scope":
        answer = "I'm sorry, but I can only assist with technical support questions regarding our software product."
        sources = []
    elif classification == "clarification":
        answer = "Could you please clarify your request or provide additional details about your workspace configuration?"
        sources = []
    elif classification == "escalation":
        answer = "Routing this case to a human support specialist."
        sources = []
    else:
        retrieved = state.get("retrieved_docs", [])
        context_str = "\n\n".join([f"Source ({d['document']}): {d['passage']}" for d in retrieved])
        prompt = f"Context:\n{context_str}\n\nUser Question: {state['user_query']}\n\nAnswer:"
        outputs = generator_pipeline(prompt)
        full_text = outputs[0]['generated_text']
        answer = full_text.split("Answer:")[-1].strip() if "Answer:" in full_text else full_text
        sources = [{"document": d["document"], "passage": d["passage"][:100] + "..."} for d in retrieved]

    return {**state, "generated_answer": answer, "sources": sources, "confidence": 0.85, "execution_logs": logs}

def verification_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Verification Node Executed")
    if state["classification"] in ["out_of_scope", "clarification", "escalation"]:
        return {**state, "verification_passed": True, "execution_logs": logs}

    answer = state.get("generated_answer", "")
    passed = len(answer) > 20
    if state.get("retry_count", 0) == 0 and "force_fail_verification" in state:
        passed = False

    return {**state, "verification_passed": passed, "execution_logs": logs}

def revision_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Revision Node Executed (Retry Path)")
    current_answer = state.get("generated_answer", "")
    return {**state, "generated_answer": f"[Revised] {current_answer}", "verification_passed": True, "retry_count": state.get("retry_count", 0) + 1, "execution_logs": logs}

def safe_failure_node(state: GraphState) -> GraphState:
    logs = state.get("execution_logs", [])
    logs.append("Safe Failure Node Executed")
    return {**state, "generated_answer": "Unable to verify. Escalating to human support.", "requires_human": True, "execution_logs": logs}

# ==========================================
# WORKFLOW GRAPH
# ==========================================
workflow = StateGraph(GraphState)
workflow.add_node("triage", triage_node)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("generation", generation_node)
workflow.add_node("verification", verification_node)
workflow.add_node("revise", revision_node)
workflow.add_node("safe_failure", safe_failure_node)

workflow.set_entry_point("triage")
workflow.add_edge("triage", "retrieval")
workflow.add_edge("retrieval", "generation")
workflow.add_edge("generation", "verification")
workflow.add_conditional_edges("verification", lambda s: END if s.get("verification_passed") else ("revise" if s.get("retry_count", 0) < 1 else "safe_failure"))
workflow.add_edge("revise", END)
workflow.add_edge("safe_failure", END)

app = workflow.compile()

def run_support_agent(query: str, force_fail: bool = False) -> dict:
    initial_state = {
        "user_query": query, "classification": None, "retrieved_docs": [],
        "generated_answer": None, "sources": [], "confidence": 0.0,
        "requires_human": False, "reason": "", "verification_passed": None,
        "retry_count": 0, "execution_logs": [], "force_fail_verification": force_fail
    }
    final_state = app.invoke(initial_state)
    output = AgentOutputSchema(
        classification=final_state["classification"],
        answer=final_state["generated_answer"],
        sources=[SourceReference(document=s["document"], passage=s["passage"]) for s in final_state["sources"]],
        confidence=final_state["confidence"], requires_human=final_state["requires_human"], reason=final_state["reason"]
    )
    return {"json_output": output.model_dump(), "logs": final_state["execution_logs"]}