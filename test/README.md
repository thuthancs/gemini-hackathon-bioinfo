# gemini-hackathon-bioino
## note
- edge case on fasta file: if the user inputs a big DNA fasta file
- 2 types of audience:
    - 2 modes: manual input vs agentic search
    - who knows where mutation happens
    - those who have no idea -> use gemini deep research to find where exactly does mutation happen on the original fasta file
        - takes the research papers -> synthesize -> reason to locate the mutation where the insertion happens -> return the masked sequence -> esm_api.py
    - if the user inputs protein faste -> just input into esm_api.py

- [ ] Design system prompt for Gemini for each case above

## feature 1: search & scan
- input their own **fasta file**: only include the mRNA mutation for the sequence
- search for the whole fasta file -> scan -> cut the unnecessary parts -> keep the mutated mRNA sequence that is reponsible for amino acid mutation 

## feature 2: esm-v2
- done

## feature 3: alphafold 
- from esm results -> input amino acids to alpha fold -> protein structure