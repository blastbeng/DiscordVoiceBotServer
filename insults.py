import random

words = [ "Brutto", "Schifoso",  "Ignobile",  "Mi fai schifo",  "Baciami il culo",  "Leccami il cazzo", "Incapace", "Viscido", "Fetido", "Mongoloide", 
"Lo sai cosa sei vero? Brutto",  "Impertinente",  "Infetto",  "Mi fai ribrezzo",  "Fammi un bocchino",  "Ciucciami la minchia",  
"Viscido", "Baciami il culo",  "Incapace", "Inginocchiati e baciami", "Cattivo",  "stronzo", "bastardo",  
"minchione",  "figlio di una bagascia",  "bastardone",  "stronzone", "puttaniere", "sadomasochista", "testa di cazzo",  "gallinaio",  
"analfabeta",  "coglionazzo",  "pedofilo",  "testa di minchia",  "cazzone",  "scemo",  "deficiente",  "stupido",  
"mongoloide",  "fuso mentale",  "coglione",  "baciaculi",  "baciacazzi",  "lecchino",  "secchione",  "figlio di mignotta", 
"omosessuale", "scassacazzi",  "stronzo", "bastardo",  "alcolizzato",  "bastardo",  "stronzo", 
"puttaniere", "usuraio", "sadomasochista", "drogato",  "gallinaio",  "analfabeta",  "ignorante",  "pedofilo",  "schifoso",  
"gay",  "frocio",  "mignottone",  "sessodipendente",  "handicappato",  "porco",  "minchione",  "testa di minchia",  "testa di cazzo",  
"testa di figa", "leccafighe" ]

def get_insults():
    try:
        sentence = random.choice(words) + " " + random.choice(words) + " " + random.choice(words)
        return sentence
    except:
        return "stronzo mi sono spaccato male, blast deve sistemarmi"
