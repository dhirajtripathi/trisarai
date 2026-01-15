import os
import sys

# Add parent dir to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_transformation_agent.parsers.apigee_parser import ApigeeParser
from api_transformation_agent.generators.kong_generator import KongGenerator
from api_transformation_agent.generators.azure_generator import AzureGenerator
import argparse

def main():
    parser = argparse.ArgumentParser(description="API Migration Agent")
    parser.add_argument("--target", default="kong", choices=["kong", "azure"], help="Target platform")
    
    # Setup Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(base_dir, "samples", "apigee", "Proxy1")
    
    target = "kong"
    if len(sys.argv) > 1:
        # Simple arg parsing override
        if "--target" in sys.argv:
            try:
                idx = sys.argv.index("--target")
                target = sys.argv[idx+1]
            except: pass

    print("========================================")
    print("🚀 API TRANSFORMATION AGENT (Any-to-Any)")
    print("========================================")
    print(f"Source: {source_path}")
    print(f"Target: {target.upper()}")
    print("----------------------------------------")
    
    # 1. Parse
    parser_agent = ApigeeParser()
    try:
        uam = parser_agent.parse(source_path)
        print("✅ Parsing Complete. UAM Metadata:", uam.metadata)
    except Exception as e:
        print(f"❌ Parsing Failed: {e}")
        return

    # 2. Generate
    if target == "kong":
        generator = KongGenerator()
        output_file = "kong_output.yaml"
    elif target == "azure":
        generator = AzureGenerator()
        output_file = "azure_output.tf"
    
    try:
        output_content = generator.generate(uam)
        
        full_output_path = os.path.join(base_dir, output_file)
        with open(full_output_path, "w") as f:
            f.write(output_content)
            
        print("✅ Generation Complete.")
        print(f"💾 Output saved to: {full_output_path}")
        print("----------------------------------------")
        print("Generated Config Content:")
        print(output_content)
        
    except Exception as e:
        print(f"❌ Generation Failed: {e}")

if __name__ == "__main__":
    main()
