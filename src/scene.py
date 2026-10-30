from cfg import OBJECTS

class Scene:


    def __init__(self, filename="model.obj"):
        self.coords = []
        self.fs = []
        self.load_obj(filename)


    def load_obj(self, filename):
        with open(OBJECTS + "/model.obj", encoding='utf-8') as file:
            for line in file:
                sp = line.split()
                if sp[0] == "v":
                    self.coords.append([float(x) for x in sp[1:4]])
                elif sp[0] == "f":
                    add_el = [int(x.split("/")[0]) - 1 for x in sp[1:]]
                    self.fs.append(add_el)
