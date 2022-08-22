import random

words = [ "brutto", "schifoso",  "ignobile",  "mi fai schifo",  "baciami il culo",  "leccami il cazzo", "incapace", "viscido", "fetido", "mongoloide", 
"lo sai cosa sei vero? brutto",  "impertinente",  "infetto",  "mi fai ribrezzo",  "fammi un bocchino",  "ciucciami la minchia",  
"viscido", "baciami il culo",  "incapace", "inginocchiati e baciami", "cattivo",  "stronzo", "bastardo",  
"minchione",  "bagascia",  "bastardone",  "stronzone", "puttaniere", "sadomasochista", "testa di cazzo",  "gallinaio",  
"analfabeta",  "coglionazzo",  "pedofilo",  "testa di minchia",  "cazzone",  "scemo",  "deficiente",  "stupido",  
"mongoloide",  "fuso mentale",  "coglione",  "baciaculi",  "baciacazzi",  "lecchino",  "secchione",  "mignotta", 
"omosessuale", "scassacazzi",  "stronzo", "bastardo",  "alcolizzato",  "bastardo",  "stronzo", 
"puttaniere", "usuraio", "sadomasochista", "drogato",  "gallinaio",  "analfabeta",  "ignorante",  "pedofilo",  "schifoso",  
"gay",  "frocio",  "mignottone",  "sessodipendente",  "handicappato",  "porco",  "minchione",  "testa di minchia",  "testa di cazzo",  
"testa di figa", "leccafighe", "merda", "merdaccia", "infame", "bimbominkia", "cafone", "crucco", "farabutto", "pirla", "piciu", "polentone"
"terrone", "quaquaraqua", "tamarro", "vucumpra", "eroinomane", "cocainomane", "cannato", "pezzente", "lurido", "verme",
"nutria", "larva", "spazzatura", "immondizia", "bitume", "colata di sborra", "cagata bianca", "spruzzata di merda",
"pulisciti la bocca", "pompinaro", "bocchinaro", "succhiacazzi", "fogna", "latrina", "schifo"]

def get_insults():
    try:
        #sentence = random.choice(words) + " " + random.choice(words) + " " + random.choice(words)
        #return sentence

        size = len(words)
        n = random.randint(0,size-1)
        sentence = words[n]
        #sentence = random.choice(words);

        words2 = words;
        words2.remove(sentence)
        
        size2 = len(words2)
        n2 = random.randint(0,size2-1)
        sentence2 = words2[n2]

        words3 = words2;
        words3.remove(sentence2)
        
        size3 = len(words3)
        n3 = random.randint(0,size3-1)
        sentence3 = words3[n3]

        insult = sentence + " " + sentence2 + " " + sentence3
        return insult
    except Exception as e:
        print(e)
        return "stronzo mi sono spaccato male, blast deve sistemarmi"
