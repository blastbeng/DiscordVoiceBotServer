import random

words = [ "Brutto", "Schifoso",  "Ignobile",  "Mi fai schifo",  "Baciami il culo",  "Leccami il cazzo", "Incapace", "Viscido", "Fetido", "Mongoloide", 
"Lo sai cosa sei vero? Brutto",  "Impertinente",  "Infetto",  "Mi fai ribrezzo",  "Fammi un bocchino",  "Ciucciami la minchia",  
"Viscido", "Baciami il culo",  "Incapace", "Inginocchiati e baciami", "Cattivo",  "stronzo", "bastardo",  
"minchione",  "figlio di una bagascia",  "bastardone",  "stronzone", "puttaniere", "sadomasochista", "testa di cazzo",  "gallinaio",  
"analfabeta",  "coglionazzo",  "pedofilo",  "testa di minchia",  "cazzone",  "scemo di un",  "deficiente",  "stupido di un",  
"mongoloide",  "fuso mentale",  "coglione",  "baciaculi",  "baciacazzi",  "lecchino",  "secchione",  "figlio di mignotta", 
"omosessuale", "scassacazzi",  "stronzo", "bastardo",  "alcolizzato",  "figlio di una bagascia",  "bastardo",  "stronzo", 
"puttaniere", "usuraio", "sadomasochista", "drogato",  "gallinaio",  "analfabeta",  "ignorante",  "pedofilo",  "schifoso",  
"gay",  "frocio",  "mignottone",  "sessodipendente",  "handicappato",  "porco",  "minchione",  "testa di minchia",  "testa di cazzo",  
"testa di figa", "leccafighe" ]

def get_insults():
    try:
        sentence = words[random.randint(0,len(words)-1)] + (" ") + words[random.randint(0,len(words)-1)] + (" ") + words[random.randint(0,len(words)-1)]
        return sentence
    except:
        return "stronzo mi sono spaccato male, blast deve sistemarmi"
