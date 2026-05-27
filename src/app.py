"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

import json
import os
from copy import deepcopy
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Slalom Capabilities Management API",
    description="API for managing consulting capabilities and consultant expertise",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Consultant registrations are persisted independently of capability definitions.
DATA_DIR = current_dir / "data"
CONSULTANT_DATA_FILE = DATA_DIR / "consultants.json"


class ConsultantRecord(BaseModel):
    email: str
    name: str | None = None
    practice_area: str | None = None
    title: str | None = None
    availability: int | None = None
    certifications: list[str] = Field(default_factory=list)
    capability_registrations: list[str] = Field(default_factory=list)


class ConsultantImportPayload(BaseModel):
    consultants: list[ConsultantRecord]


DEFAULT_CAPABILITIES = {
    "Cloud Architecture": {
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,  # hours per week available across team
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
    },
    "Data Analytics": {
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology", 
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
    },
    "DevOps Engineering": {
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"], 
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
    },
    "Digital Strategy": {
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
    },
    "Change Management": {
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
    },
    "UX/UI Design": {
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
    },
    "Cybersecurity": {
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
    },
    "Business Intelligence": {
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
    },
    "Agile Coaching": {
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
    }
}


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_valid_email(email: str) -> None:
    normalized_email = normalize_email(email)
    local_part, separator, domain = normalized_email.partition("@")

    if not separator or not local_part or "." not in domain:
        raise HTTPException(status_code=400, detail="A valid consultant email is required")


def unique_values(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def default_name_from_email(email: str) -> str:
    local_part = email.split("@", maxsplit=1)[0]
    return " ".join(part.capitalize() for part in local_part.split("."))


def build_default_consultant_store() -> dict[str, dict]:
    consultants: dict[str, dict] = {}

    for capability_name, details in DEFAULT_CAPABILITIES.items():
        for email in details["consultants"]:
            normalized_email = normalize_email(email)
            consultant = consultants.setdefault(
                normalized_email,
                {
                    "email": normalized_email,
                    "name": default_name_from_email(normalized_email),
                    "practice_area": details["practice_area"],
                    "title": "Consultant",
                    "availability": None,
                    "certifications": [],
                    "capability_registrations": [],
                },
            )
            consultant["capability_registrations"].append(capability_name)

    for consultant in consultants.values():
        consultant["capability_registrations"] = unique_values(
            consultant["capability_registrations"]
        )

    return consultants


def serialize_consultant_store(store: dict[str, dict]) -> dict[str, list[dict]]:
    return {
        "consultants": [
            store[email]
            for email in sorted(store)
        ]
    }


def write_consultant_store(store: dict[str, dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONSULTANT_DATA_FILE.write_text(
        json.dumps(serialize_consultant_store(store), indent=2) + "\n",
        encoding="utf-8",
    )


def validate_consultant_record(record: ConsultantRecord, row_number: int) -> tuple[dict | None, dict | None]:
    normalized_email = normalize_email(record.email)
    capability_registrations = unique_values(record.capability_registrations)
    validation_errors = []

    if not normalized_email:
        validation_errors.append("email is required")
    else:
        local_part, separator, domain = normalized_email.partition("@")
        if not separator or not local_part or "." not in domain:
            validation_errors.append("email must be a valid address")

    unknown_capabilities = [
        capability_name
        for capability_name in capability_registrations
        if capability_name not in DEFAULT_CAPABILITIES
    ]
    if unknown_capabilities:
        validation_errors.append(
            "unknown capabilities: " + ", ".join(sorted(unknown_capabilities))
        )

    if validation_errors:
        return None, {
            "row": row_number,
            "email": normalized_email or record.email,
            "errors": validation_errors,
        }

    consultant = {
        "email": normalized_email,
        "name": record.name or default_name_from_email(normalized_email),
        "practice_area": record.practice_area,
        "title": record.title,
        "availability": record.availability,
        "certifications": unique_values(record.certifications),
        "capability_registrations": capability_registrations,
    }
    return consultant, None


def load_consultant_store() -> dict[str, dict]:
    if not CONSULTANT_DATA_FILE.exists():
        consultant_store = build_default_consultant_store()
        write_consultant_store(consultant_store)
        return consultant_store

    raw_payload = json.loads(CONSULTANT_DATA_FILE.read_text(encoding="utf-8"))
    raw_consultants = raw_payload.get("consultants", [])
    consultant_store: dict[str, dict] = {}
    validation_errors = []

    for row_number, raw_consultant in enumerate(raw_consultants, start=1):
        consultant_record = ConsultantRecord.model_validate(raw_consultant)
        consultant, error = validate_consultant_record(consultant_record, row_number)

        if error:
            validation_errors.append(error)
            continue

        if consultant["email"] in consultant_store:
            validation_errors.append(
                {
                    "row": row_number,
                    "email": consultant["email"],
                    "errors": ["duplicate consultant email in persistent store"],
                }
            )
            continue

        consultant_store[consultant["email"]] = consultant

    if validation_errors:
        raise RuntimeError(
            "Invalid consultant persistence file: "
            + json.dumps(validation_errors, indent=2)
        )

    return consultant_store


def build_capabilities(store: dict[str, dict]) -> dict[str, dict]:
    capabilities = deepcopy(DEFAULT_CAPABILITIES)

    for capability in capabilities.values():
        capability["consultants"] = []

    for consultant in store.values():
        for capability_name in consultant["capability_registrations"]:
            capabilities[capability_name]["consultants"].append(consultant["email"])

    for capability in capabilities.values():
        capability["consultants"].sort()

    return capabilities


consultant_store = load_consultant_store()
capabilities = build_capabilities(consultant_store)


def refresh_persistent_state() -> None:
    global capabilities

    capabilities = build_capabilities(consultant_store)
    write_consultant_store(consultant_store)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities():
    return capabilities


@app.get("/consultants")
def get_consultants():
    return serialize_consultant_store(consultant_store)


@app.get("/consultants/export")
def export_consultants():
    return serialize_consultant_store(consultant_store)


@app.post("/consultants/import")
def import_consultants(payload: ConsultantImportPayload):
    imported_store: dict[str, dict] = {}
    validation_errors = []

    for row_number, consultant_record in enumerate(payload.consultants, start=1):
        consultant, error = validate_consultant_record(consultant_record, row_number)

        if error:
            validation_errors.append(error)
            continue

        if consultant["email"] in imported_store:
            validation_errors.append(
                {
                    "row": row_number,
                    "email": consultant["email"],
                    "errors": ["duplicate consultant email in import payload"],
                }
            )
            continue

        imported_store[consultant["email"]] = consultant

    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Import validation failed",
                "errors": validation_errors,
            },
        )

    consultant_store.clear()
    consultant_store.update(imported_store)
    refresh_persistent_state()

    return {"message": f"Imported {len(imported_store)} consultants"}


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str):
    """Register a consultant for a capability"""
    ensure_valid_email(email)
    normalized_email = normalize_email(email)

    # Validate capability exists
    if capability_name not in capabilities:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get the specific capability
    capability = capabilities[capability_name]

    # Validate consultant is not already registered
    if normalized_email in capability["consultants"]:
        raise HTTPException(
            status_code=400,
            detail="Consultant is already registered for this capability"
        )

    consultant = consultant_store.get(
        normalized_email,
        {
            "email": normalized_email,
            "name": default_name_from_email(normalized_email),
            "practice_area": capability["practice_area"],
            "title": "Consultant",
            "availability": None,
            "certifications": [],
            "capability_registrations": [],
        },
    )
    consultant["capability_registrations"] = unique_values(
        consultant["capability_registrations"] + [capability_name]
    )
    consultant_store[normalized_email] = consultant
    refresh_persistent_state()

    return {"message": f"Registered {normalized_email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str):
    """Unregister a consultant from a capability"""
    normalized_email = normalize_email(email)

    # Validate capability exists
    if capability_name not in capabilities:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get the specific capability
    capability = capabilities[capability_name]

    # Validate consultant is registered
    if normalized_email not in capability["consultants"]:
        raise HTTPException(
            status_code=400,
            detail="Consultant is not registered for this capability"
        )

    consultant = consultant_store.get(normalized_email)
    if consultant is None:
        raise HTTPException(status_code=404, detail="Consultant not found")

    consultant["capability_registrations"] = [
        registration
        for registration in consultant["capability_registrations"]
        if registration != capability_name
    ]
    refresh_persistent_state()

    return {"message": f"Unregistered {normalized_email} from {capability_name}"}
