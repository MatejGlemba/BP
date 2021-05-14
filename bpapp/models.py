from django.db import models

# Create your models here.
class User(models.Model):
    name = models.TextField()
    password = models.TextField()

#class Transakcia(models.Model):
#    ArlID = models.CharField(null=True)
#    tcreate = models.DateTimeField(null=True)
#    idRow = models.CharField(null=True)
#    op = models.CharField(null=True)
#    tag = models.CharField(null=True)
#    DatOP = models.CharField(null=True)
#    Pobocka = models.CharField(null=True)
#    holding = models.CharField(null=True)
#    catId = models.CharField(null=True)
#    Tcat_020a = models.CharField(null=True)
#    Tcat_020q = models.CharField(null=True)
#    Tcat_020c = models.CharField(null=True)
#    Tcat_T015a = models.CharField(null=True)
#    Tcat_T035a = models.CharField(null=True)
#    Tcat_T080a = models.CharField(null=True)
#    isanonym = models.CharField(null=True)
#    pohlavi = models.CharField(null=True)
#    userHash = models.CharField(null=True)
#    userTyp = models.CharField(null=True)
#    psc = models.CharField(null=True)
#    vek = models.CharField(null=True)
#    casVypujceni = models.CharField(null=True)
#    DelkaTransakce = models.CharField(null=True)
#    pocetProlongaci = models.CharField(null=True)
#    pocetUpominek = models.CharField(null=True)
        
class Katalog(models.Model):
    id = models.IntegerField(primary_key=True)
    katalog = models.TextField(null=True)

# Číselníky
class Pohlavie(models.Model):
    id = models.IntegerField(primary_key=True)
    pohlavie = models.CharField(max_length=4)

class TypOperacie(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    nazov = models.CharField(max_length=25)

class PscObvodu(models.Model):
    psc = models.IntegerField(primary_key=True)
    obvod = models.CharField(max_length=40)

class Konspekt(models.Model):
    id = models.IntegerField(primary_key=True)
    nazov = models.CharField(max_length=100)

class VekovaSkupina(models.Model):
    id = models.IntegerField(primary_key=True)
    skupina = models.CharField(max_length=7)

# Modely analýz
class Analyza1Model(models.Model):
    id = models.IntegerField(primary_key=True)
    pouzivatelId = models.CharField(max_length=50)
    vek = models.IntegerField()
    pohlavie_id = models.ForeignKey(Pohlavie, on_delete=models.CASCADE)
    psc_id = models.ForeignKey(PscObvodu, on_delete=models.CASCADE)
    casVytvoreniaTransakcie = models.DateTimeField()

class Analyza2Model(models.Model):
    id = models.IntegerField(primary_key=True)
    transakciaId = models.IntegerField()
    typOperacie_id = models.ForeignKey(TypOperacie, on_delete=models.CASCADE)
    casVytvoreniaTransakcie = models.DateTimeField()
    dlzkaVypozicky = models.IntegerField()
    autor = models.CharField(max_length=50)
    vydavatelstvo = models.CharField(max_length=50)
    konspekt_id = models.ForeignKey(Konspekt, on_delete=models.CASCADE)

class Analyza3Model(models.Model):
    id = models.IntegerField(primary_key=True)
    transakciaId = models.IntegerField()
    vekovaSkupina_id = models.ForeignKey(VekovaSkupina, on_delete=models.CASCADE)
    konspekt_id = models.ForeignKey(Konspekt, on_delete=models.CASCADE)
