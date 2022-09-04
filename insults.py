import random

words = [ 
"aborto",
"alcolizzato",
"analfabeta",
"autoinculati",
"baciacazzi",
"baciaculi",
"baciami il culo",
"baciami il cazzo",
"baciami la minchia",
"bagascia",
"bastardo",
"battone",
"bestia di satana",
"bestia",
"bimbominkia",
"bitume",
"bocchinaro", 
"brutto",
"buzzurro",
"cafone",
"cagata bianca",
"cagacazzi",
"cagaminchia",
"cannato",
"carogna",
"cattivo",
"cazzone",
"ciucciami la minchia",
"ciucciami lo scroto",
"cocainomane",
"coglionazzo",
"coglione",
"colata di sborra",
"colata di merda",
"crucco",
"culattone",
"culo sfondato"
"deficiente",
"disagio",
"disagiato",
"drogato",
"eroinomane",
"fancazzista",
"fammi un bocchino",
"fammi una sega",
"farabutto",
"fetido",
"ficcati un dito in culo",
"fogna", 
"frocio",
"fuso mentale",
"gallinaio",
"gay",
"iena",
"ignobile",
"ignorante",
"imbecille",
"immondizia",
"impertinente",
"incapace",
"infame",
"infetto",
"inginocchiati e baciami",
"larva",
"latrina", 
"lavativo", 
"leccaculo",
"leccafighe",
"leccami il cazzo",
"lecchino",
"lo sai cosa sei vero? brutto",
"lombrico", 
"lurido",
"maiale",
"malandrino",
"melanzana",
"merda",
"merdaccia",
"mi fai ribrezzo",
"mi fai schifo",
"mignotta",
"mignottone",
"minchione",
"mongoloide",
"nutria",
"omosessuale",
"pazzo mentale",
"pedofilo",
"pezzente",
"piciu",
"pirla",
"polentone",
"pollo,"
"pompinaro",
"porco",
"pulisciti il cazzo",
"pulisciti il culo",
"pulisciti la bocca",
"pulisciti la figa",
"pusillanime",
"puttaniere",
"quaquaraqua",
"ratto",
"reietto",
"rompicazzo",
"rompicoglioni",
"sacco di merda", 
"sadomasochista",
"scassacazzi",
"scemo",
"schifo", 
"schifoso",
"secchione",
"sessodipendente",
"spacciatore", 
"spazzatura",
"spruzzata di merda",
"stronzo",
"stronzone",
"stupido",
"succhiacazzi", 
"succhiami la minchia", 
"tamarro",
"terrone",
"testa di cazzo",
"testa di culo",
"testa di figa",
"testa di minchia",
"topo di fogna",
"usuraio",
"vaffanculo",
"vai a cagare",
"vai a fare in culo",
"vai a dare via il culo",
"vegetale", 
"verme",
"villano",
"viscido",
"vucumpra" ]

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
