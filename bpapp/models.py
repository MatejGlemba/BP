from django.db import models
# Create your models here.

class User(models.Model):
    name = models.TextField()
    password = models.TextField()
        
# Číselníky
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

# Catalog
class Katalog(models.Model):
    id = models.AutoField(primary_key=True)
    katalogId = models.CharField(max_length=20, null=True)
    konspekt = models.IntegerField(null=True)
    autor = models.CharField(max_length=400, null=True)
    vydavatelstvo = models.CharField(max_length=400, null=True)

# Modely analýz
class Analyza1Model(models.Model):
    id = models.AutoField(primary_key=True)
    pouzivatelId = models.CharField(max_length=150, null=True)
    vek = models.IntegerField(null=True)
    pohlavie = models.CharField(max_length=4, null=True)
    psc_id = models.ForeignKey(PscObvodu, on_delete=models.CASCADE, null=True)
    casVytvoreniaTransakcie = models.DateField(null=True)
          
class Analyza2Model(models.Model):
    id = models.AutoField(primary_key=True)
    transakciaId = models.IntegerField()
    typOperacie_id = models.ForeignKey(TypOperacie, on_delete=models.CASCADE)
    casVytvoreniaTransakcie = models.DateField()
    dlzkaVypozicky = models.IntegerField()
    autor = models.CharField(max_length=400)
    vydavatelstvo = models.CharField(max_length=400)
    konspekt_id = models.ForeignKey(Konspekt, on_delete=models.CASCADE)

class Analyza3Model(models.Model):
    id = models.AutoField(primary_key=True)
    transakciaId = models.IntegerField()
    vekovaSkupina_id = models.ForeignKey(VekovaSkupina, on_delete=models.CASCADE)
    konspekt_id = models.ForeignKey(Konspekt, on_delete=models.CASCADE)
