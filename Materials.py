import material_info

####################################################
##  Medžiagų klasės
class Material:
    def __init__(self, id, name, coef, info):
        self.id = id
        self.name = name
        self.coef = coef
        self.info = info

class Materials:
    items = [
        Material(0, "Varis", 0.0000167, material_info.varis),
        Material(1, "Auksas", 0.0000142, material_info.auksas),
        Material(2, "Geležis", 0.000012, material_info.gelezis),
        Material(3, "Aliuminis", 0.000023, material_info.aliuminis)

        # Jei norit įdėti medžiagą, į šitą listą įdėkit dar vieną Material() su id (+1), vardu, alfa koeficientu ir medžiagos info (aprašytą faile material_info.py)
    ]

    def getCoef(self, id):
        for item in self.items:
            if (item.id == id):
                return item.coef
        return -1

    def getName(self, id):
        for item in self.items:
            if (item.id == id):
                return item.name
        return ""

    def getInfo(self, id):
        for item in self.items:
            if (item.id == id):
                return item.info
        return ""