from markovipy import MarkoviPy
obj = MarkoviPy("./config/sentences.txt")
#obj = MarkoviPy("./config/Gerontion_utf8.txt")
print(obj.generate_sentence())