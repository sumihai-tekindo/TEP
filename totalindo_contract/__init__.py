# -*- coding: utf-8 -*-

from . import controllers
from . import models

def terbilang(self, satuan):
		huruf = ["","Satu","Dua","Tiga","Empat","Lima","Enam","Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
		hasil = ""; 
		if satuan < 12: 
			hasil = hasil + huruf[satuan]; 
		elif satuan < 20: 
			hasil = hasil + self.terbilang(satuan-10)+" Belas"; 
		elif satuan < 100:
			hasil = hasil + self.terbilang(satuan/10)+" Puluh "+self.terbilang(satuan%10); 
		elif satuan < 200: 
			hasil=hasil+"Seratus "+self.terbilang(satuan-100); 
		elif satuan < 1000: 
			hasil=hasil+self.terbilang(satuan/100)+" Ratus "+self.terbilang(satuan%100); 
		elif satuan < 2000: 
			hasil=hasil+"Seribu "+self.terbilang(satuan-1000); 
		elif satuan < 1000000: 
			hasil=hasil+self.terbilang(satuan/1000)+" Ribu "+self.terbilang(satuan%1000); 
		elif satuan < 1000000000:
			hasil=hasil+self.terbilang(satuan/1000000)+" Juta "+self.terbilang(satuan%1000000);
		elif satuan < 1000000000000:
			hasil=hasil+self.terbilang(satuan/1000000000)+" Milyar "+self.terbilang(satuan%1000000000)
		elif satuan >= 1000000000000:
			hasil="Angka terlalu besar, harus kurang dari 1 Trilyun!"; 
		return hasil;   