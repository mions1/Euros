import os

paesi_file = open('paesi.txt', 'r')

for nazione in paesi_file:
	nazione = nazione.replace('\n','')
	valori_file = open('valori.txt', 'r')
	for valore in valori_file:
		try:
			valore = valore.replace('\n','')
			if (float(valore) > 0.06 and float(valore) < 0.9):
				valore = valore.replace('.',',')
				old = './'+nazione+'/'+valore+'.jpg'
				valore = valore[::-1]
				valore = valore.replace('0','',1)
				valore = valore[::-1]
				new = './'+nazione+'/'+valore+'.jpg'
				os.rename(old,new)
			elif (float(valore) > 0.9):
				valore = valore.replace('.0','')
				old = './'+nazione+'/'+valore+'.jpg'
				valore = valore+(',0')
				new = './'+nazione+'/'+valore+'.jpg'
				os.rename(old,new)
		except (FileNotFoundError):
			continue
	valori_file.close()
