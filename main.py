from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="AI Foreign Trade Agent System")

# =========================
# Memory Database
# =========================

clients_db = {}
tasks_db = {}
success_cases = []
failed_cases = []

# =========================
# Agents
# =========================

class SchedulerAgent:

    def monday_plan(self, salesman):

        return {
            "salesman": salesman,
            "new_clients_target": 35,
            "markets": [
                "USA",
                "Germany",
                "Middle East"
            ],
            "focus": [
                "high-end customers",
                "flexible supply chain buyers",
                "fast delivery buyers"
            ]
        }


class TargetDiscoveryAgent:

    def search(self, product):

        return [
            {
                "company": "XXX Lighting USA",
                "pain_points": [
                    "slow delivery",
                    "unstable suppliers",
                    "out of stock"
                ],
                "probability": "78%"
            },
            {
                "company": "XXX Furniture Germany",
                "pain_points": [
                    "slow sampling",
                    "lack of innovation"
                ],
                "probability": "64%"
            }
        ]


class PainPointAgent:

    def analyze(self, company):

        return {
            "company": company,
            "pain_points": [
                "slow lead time",
                "high MOQ",
                "unstable quality",
                "slow new product updates"
            ]
        }


class MailAgent:

    def generate(self, company, own_product, pain_points):

        subject = f"Helping {company} Improve Supply Chain Efficiency"

        content = f"""
Dear {company},

We noticed that many companies in your industry are struggling with:
- {pain_points[0]}
- {pain_points[1]}

Our company specializes in:
{own_product}

We can help improve delivery speed, lower MOQ, and stabilize quality.

Would you be open to a quick discussion?

Best Regards
"""

        return {
            "subject": subject,
            "content": content
        }


class ReplyAgent:

    def analyze_reply(self, reply):

        if "price" in reply.lower():
            return {
                "intent": "High Intent",
                "reason": "Customer is discussing pricing",
                "suggestion": "Do not immediately reduce price. Push quality and case studies."
            }

        if "sample" in reply.lower():
            return {
                "intent": "Medium-High Intent",
                "reason": "Customer wants samples",
                "suggestion": "Push fast sampling and factory capability."
            }

        return {
            "intent": "Unknown",
            "reason": "Need more communication",
            "suggestion": "Continue follow-up"
        }


class FollowupAgent:

    def should_followup(self, opened_times):

        if opened_times >= 3:
            return {
                "followup": True,
                "strategy": "Send case-study style follow-up email after 3 days"
            }

        return {
            "followup": False,
            "strategy": "Low-value customer"
        }


class NegotiationAgent:

    def strategy(self, customer_type):

        strategies = {
            "price_sensitive": "Small discount + emphasize quality",
            "high_end": "Push factory tour and certifications",
            "bulk_buyer": "Push production capacity"
        }

        return strategies.get(customer_type, "Normal communication")


class WorkflowAgent:

    def next_step(self, current_stage):

        flow = {
            "development": "quotation",
            "quotation": "sampling",
            "sampling": "production",
            "production": "inspection",
            "inspection": "shipping",
            "shipping": "completed"
        }

        return flow.get(current_stage, "completed")


class MemoryAgent:

    def update_memory(self, client_name, note):

        if client_name not in clients_db:
            clients_db[client_name] = {
                "history": [],
                "stage": "development"
            }

        clients_db[client_name]["history"].append({
            "time": str(datetime.now()),
            "note": note
        })

        return clients_db[client_name]


scheduler_agent = SchedulerAgent()
target_agent = TargetDiscoveryAgent()
pain_agent = PainPointAgent()
mail_agent = MailAgent()
reply_agent = ReplyAgent()
followup_agent = FollowupAgent()
negotiation_agent = NegotiationAgent()
workflow_agent = WorkflowAgent()
memory_agent = MemoryAgent()

# =========================
# API Models
# =========================

class TargetRequest(BaseModel):
    product: str

class MailRequest(BaseModel):
    company: str
    own_product: str

class ReplyRequest(BaseModel):
    reply: str

class MemoryRequest(BaseModel):
    client_name: str
    note: str

class WorkflowRequest(BaseModel):
    client_name: str
    current_stage: str

# =========================
# APIs
# =========================

@app.get("/")

def home():
    return {"status": "running"}


@app.get("/weekly-plan/{salesman}")

def weekly_plan(salesman: str):
    return scheduler_agent.monday_plan(salesman)


@app.post("/find-targets")

def find_targets(req: TargetRequest):
    return target_agent.search(req.product)


@app.post("/analyze-company")

def analyze_company(req: MailRequest):

    pain_points = pain_agent.analyze(req.company)

    return pain_points


@app.post("/generate-mail")

def generate_mail(req: MailRequest):

    pain_points = pain_agent.analyze(req.company)

    mail = mail_agent.generate(
        req.company,
        req.own_product,
        pain_points["pain_points"]
    )

    return mail


@app.post("/analyze-reply")

def analyze_reply(req: ReplyRequest):

    return reply_agent.analyze_reply(req.reply)


@app.post("/update-memory")

def update_memory(req: MemoryRequest):

    return memory_agent.update_memory(
        req.client_name,
        req.note
    )


@app.post("/workflow")

def workflow(req: WorkflowRequest):

    next_stage = workflow_agent.next_step(
        req.current_stage
    )

    if req.client_name not in clients_db:
        clients_db[req.client_name] = {
            "history": [],
            "stage": req.current_stage
        }

    clients_db[req.client_name]["stage"] = next_stage

    return {
        "client": req.client_name,
        "current_stage": req.current_stage,
        "next_stage": next_stage
    }


@app.get("/dashboard")

def dashboard():

    return {
        "total_clients": len(clients_db),
        "clients": clients_db,
        "success_cases": success_cases,
        "failed_cases": failed_cases
    }
