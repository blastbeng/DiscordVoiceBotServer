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

names_plural = [ "I Cessi",
          "Gli Stronzi",
          "I Brutti",
          "Le Merde",
          "Le Minchie",
          "Le Troie",
          "I Cazzi",
          "Le Pucchiacche",
          "I Pazzi Mentali",
          "I Luridi",
          "I Pezzenti",
          "Gli Analfabeti",
          "Gli Incapaci",
          "I Putridi",
          "Le Puttane",
          "I Piglianculo",
          "I Coglioni",
          "I Drogati",
          "I Masochisti",
          "I Sadici",
          "I Sadomasochisti",
          "Le Vulve",
          "I Laidi",
          "Gli Eunuchi",
          "I Succhiapalle",
          "Gli Eroinomani",
          "Le Guerriere Sailor",
          "Le Bestie di Satana",
          "I Latex4ever",
          "I Buchi Spanati",
          "Gli incompetenti"]

names_single = [ "Il Cesso",
          "Lo Stronzo",
          "Il Brutto",
          "La Merda",
          "La Minchia",
          "La Troia",
          "Il Cazzo",
          "La Pucchiacca",
          "Il Pazzo Mentale",
          "Il Lurido",
          "Il Pezzente",
          "L'Analfabeta",
          "L'Incapace",
          "Il Putrido",
          "La Puttana",
          "Il Piglianculo",
          "Il Coglione",
          "Il Drogato",
          "Il Masochista",
          "Il Sadico",
          "Il Sadomasochista",
          "La Vulva",
          "Il Laido",
          "L'EunucO",
          "IL Succhiapalle",
          "L'Eroinomane",
          "La Guerriera Sailor",
          "La Bestia di Satana",
          "Il Latex4ever",
          "Il Buco Spanato",
          "L'incompetente"]


names_single_base = [ "Cesso",
          "Stronzo",
          "Brutto",
          "Merda",
          "Minchia",
          "Troia",
          "Cazzo",
          "Pucchiacca",
          "Pazzo Mentale",
          "Lurido",
          "Pezzente",
          "Analfabeta",
          "apace",
          "Putrido",
          "Puttana",
          "Piglianculo",
          "Coglione",
          "Drogato",
          "Masochista",
          "Sadico",
          "Sadomasochista",
          "Vulva",
          "Laido",
          "EunucO",
          "Succhiapalle",
          "Eroinomane",
          "Guerriera Sailor",
          "Bestia di Satana",
          "Latex4ever",
          "Buco Spanato",
          "Incompetente"]

def get_insults():
    try:
        sentence = random.choice(words) + " " + random.choice(words) + " " + random.choice(words)
        return sentence
    except:
        return "stronzo mi sono spaccato male, blast deve sistemarmi"
