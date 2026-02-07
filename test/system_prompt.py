import google.generativeai as genai
import PIL.Image

def generate_final_report(api_key, text_data, image_path):
    """
    Sends the metrics and the screenshot to Gemini for the final report.
    """
    
    # 1. Configure the Model with the System Prompt
    genai.configure(api_key=api_key)
    
    system_instruction = """
    ROLE: You are an expert Computational Structural Biologist...
    (Paste the full text from Section 1 above here)
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro", # Pro is better for images than Flash
        system_instruction=system_instruction
    )

    # 2. Load the Visual Evidence (The PNG from your visualizer)
    # Note: In your app, you can use 'stmol' to take a snapshot or 
    # use a library like 'py3Dmol's get_image() function.
    protein_image = PIL.Image.open(image_path)

    # 3. Construct the User Message (The specific case data)
    # We assume 'text_data' is a dictionary with your calculated values
    user_prompt = f"""
    Please analyze this case:
    
    1. CONTEXT:
       - Gene: {text_data['gene']}
       - Pathogenic Mutation: {text_data['bad_mut']}
       - Rescue Mutation: {text_data['rescue_mut']}
    
    2. METRICS:
       - RMSD Score: {text_data['rmsd']} Angstroms
       - Local pLDDT Score at mutation site: {text_data['plddt']}
       - Chemical Change: {text_data['chem_change']} (e.g. Leu->Phe)
       
    3. ATTACHMENT:
       - See the attached PNG showing the superimposed structures (Red=Mutant, Blue=WT).
    """

    # 4. Send to Gemini (Text + Image)
    print("🤖 Gemini is analyzing the structure and physics...")
    response = model.generate_content([user_prompt, protein_image])
    
    return response.text

# --- USAGE EXAMPLE ---
# data = {
#    "gene": "TP53",
#    "bad_mut": "A45G",
#    "rescue_mut": "L88F",
#    "rmsd": 0.45,
#    "plddt": 88.5,
#    "chem_change": "Hydrophobic Leucine to Aromatic Phenylalanine (Larger)"
# }
# report = generate_final_report("YOUR_KEY", data, "snapshot_of_protein.png")
# print(report)