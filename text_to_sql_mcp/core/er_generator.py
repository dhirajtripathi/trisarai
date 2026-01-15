from typing import Dict, Any

class ERDiagramGenerator:
    """
    Generates Mermaid.js Entity Relationship Diagrams from Schema JSON.
    """
    
    @staticmethod
    def generate_mermaid(schema: Dict[str, Any]) -> str:
        if not schema:
            return ""
            
        mermaid = ["erDiagram"]
        
        # 1. SQL Tables
        tables = schema.get("tables", [])
        for table in tables:
            t_name = table["name"]
            
            # Table Definition
            mermaid.append(f"    {t_name} {{")
            for col in table.get("columns", []):
                c_name = col["name"]
                c_type = col["type"]
                desc = col.get("description", "")
                row = f"        {c_type} {c_name}"
                if desc:
                    row += f" \"{desc}\""
                mermaid.append(row)
            mermaid.append("    }")
            
            # Relationships (FKs)
            # Schema structure: [{"constrained_columns": ["user_id"], "referred_table": "users"}]
            for fk in table.get("foreign_keys", []):
                ref_table = fk["referred_table"]
                # Assuming 1:many for simplicity in visualization: 1 ref_table -> many current_table
                # user_id FK in orders -> users ||--o{ orders
                mermaid.append(f"    {ref_table} ||--o{{ {t_name} : \"has\"")

        # 2. NoSQL Collections (Simpler representation)
        collections = schema.get("collections", [])
        for col_name in collections:
            mermaid.append(f"    {col_name} {{")
            mermaid.append("        json document")
            mermaid.append("    }")

        return "\n".join(mermaid)
