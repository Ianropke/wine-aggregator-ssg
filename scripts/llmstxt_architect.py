import os
import glob

CONTENT_DIR = "src/content/wines"
PUBLIC_DIR = "public"
LLMS_TXT_PATH = os.path.join(PUBLIC_DIR, "llms.txt")
LLMS_FULL_TXT_PATH = os.path.join(PUBLIC_DIR, "llms-full.txt")

def generate_manifests():
    mdx_files = glob.glob(os.path.join(CONTENT_DIR, "*.mdx"))
    
    llms_txt = "> Velkommen til Wine Price Aggregator - den ultimative datadrevne vinkurator baseret på QPR og Hedonic Pricing.\n"
    llms_txt += "> Platformen aflægger 'wine snobbery' via algoritmisk autoritet og Letterboxd-inspirerede anmeldelser.\n\n"
    llms_txt += "## Anmeldelser\n"
    
    full_text = llms_txt + "\n---\n\n"
    
    for file_path in sorted(mdx_files):
        filename = os.path.basename(file_path)
        base_name = filename.replace('.mdx', '')
        
        # Link in llms.txt uses .md extension as requested in manifesto (section 9)
        llms_txt += f"- [Link til anmeldelse af {base_name}](/wines/{base_name}.md)\n"
        
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read()
            full_text += f"# {base_name}\n\n{content}\n\n---\n\n"
            
    with open(LLMS_TXT_PATH, "w", encoding='utf-8') as f:
        f.write(llms_txt)
        
    with open(LLMS_FULL_TXT_PATH, "w", encoding='utf-8') as f:
        f.write(full_text)
        
    print(f"Generated {LLMS_TXT_PATH} and {LLMS_FULL_TXT_PATH}")

if __name__ == "__main__":
    generate_manifests()
