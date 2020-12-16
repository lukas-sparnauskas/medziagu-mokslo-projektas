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
        Material(3, "Aliuminis", 0.000023, material_info.aliuminis),
        Material(4, "Gintaras", 0.000055, material_info.gintaras),
        Material(5, "Bronza", 0.0000177, material_info.bronza),
        Material(6, "Kalcis", 0.0000223, material_info.kalcis),
        Material(7, "Kobaltas", 0.000012, material_info.kobaltas),
        Material(8, "Platina", 0.000009, material_info.platina),
        Material(9, "Cirkonis", 0.0000057, material_info.cirkonis)

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