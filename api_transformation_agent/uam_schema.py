from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

# --- Policy Definitions ---

class PolicyBase(BaseModel):
    name: str = Field(..., description="Name of the policy instance")
    enabled: bool = True
    
class AuthenticationPolicy(PolicyBase):
    type: Literal["authentication"] = "authentication"
    subtype: Literal["apikey", "oauth2", "jwt"]
    location: str = "header" # header, query
    key_name: str = "apikey" # e.g. x-api-key

class RateLimitPolicy(PolicyBase):
    type: Literal["ratelimit"] = "ratelimit"
    quota: int
    interval: str # e.g. "minute", "hour"
    identifier: str = "ip" # what to rate limit by

class ThreatProtectionPolicy(PolicyBase):
    type: Literal["threat_protection"] = "threat_protection"
    subtype: Literal["xml", "json", "sql"]
    
class BackendPolicy(PolicyBase):
    type: Literal["backend"] = "backend"
    target_url: str

# Union for all known policies
UAMPolicy = Union[AuthenticationPolicy, RateLimitPolicy, ThreatProtectionPolicy, BackendPolicy]

# --- Core Structure ---

class Route(BaseModel):
    name: str
    paths: List[str] = Field(..., description="URL paths e.g. /v1/users")
    methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="HTTP Methods")
    policies: List[UAMPolicy] = Field(default_factory=list, description="Ordered logic chain")

class Service(BaseModel):
    name: str = Field(..., description="Name of the Service/API")
    base_url: str = Field(..., description="Downstream/Target URL")
    routes: List[Route] = Field(default_factory=list)
    global_policies: List[UAMPolicy] = Field(default_factory=list)

class UAMEnvelope(BaseModel):
    services: List[Service]
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Original source metadata")
