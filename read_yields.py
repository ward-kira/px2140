'''

        Superclass to extract yield data from tables
        and from mppnp simulations

        Christian Ritter 11/2013

        Two classes: One for reading and extracting of
        NuGrid table data, the other one for SN1a data.



'''


import matplotlib.pyplot as plt
import numpy as np
import os

color=['r','k','b','g']
marker_type=['o','p','s','D']
line_style=['--','-','-.',':']


#global notebookmode
notebookmode=False

#class read_yields():
#
#       def __init__(self,nugridtable='element_yield_table.txt',sn1a_table='sn1a_ivo12_stable_z.txt'):
#
#               self.sn1a_table=sn1a_table
#               self.nugridtable=nugridtable    ,...

class read_nugrid_yields():

    def __init__(self,nugridtable,isotopes=[],excludemass=[]):

        '''
                dir : specifing the filename of the table file

        '''
        table=nugridtable

        import os
        if '/' in table:
            self.label=table.split('/')[-1]
        else:
            self.label=table
        self.path=table
        if notebookmode==True:
            os.system('sudo python cp.py '+nugridtable)
            file1=open('tmp/'+nugridtable)
            lines=file1.readlines()
            file1.close()
            os.system('sudo python delete.py '+nugridtable)
        else:
            file1=open(nugridtable)
            lines=file1.readlines()
            file1.close()
        header1=[]
        table_header=[]
        age=[]
        yield_data=[]
        kin_e=[]
        lum_bands=[]
        m_final=[]
        header_done=False
	ignore=False
	######read through all lines
        for line in lines:
            if 'H' in line[0]:
                if not 'Table' in line:
                    if header_done==False:
                        header1.append(line.strip())
                    else:
                        table_header[-1].append(line.strip())
                else:
		    ignore=False
		    for kk in range(len(excludemass)):
		    	if float(excludemass[kk]) == float(line.split(',')[0].split('=')[1]):
				ignore=True
				#print 'ignore',float(line.split(',')[0].split('=')[1])
				break
		    #print line,'ignore',ignore
		    if ignore==True:
		        header_done=True
		        continue
		    
                    table_header.append([])
                    table_header[-1].append(line.strip())
                    yield_data.append([])
                    lum_bands.append([])
                    m_final.append([])
                    header_done=True
		if ignore==True:
		    continue
                if 'Lifetime' in line:
                    age.append(float(line.split(':')[1]))
                if 'kinetic energy' in line:
                    kin_e.append(float(line.split(':')[1]))
                if 'band' in line:
                    lum_bands[-1].append(float(line.split(':')[1]))
                if 'Mfinal' in line:
                    m_final[-1].append(float(line.split(':')[1]))
                continue
	    if ignore==True:
		continue
            if '&Isotopes &Yields' in line or '&Elements &Yields' in line:
                title_line=line.split('&')[1:]
                column_titles=[]
                for t in title_line:
                    yield_data[-1].append([])
                    column_titles.append(t.strip())
                #print column_titles
                continue
            #iso ,name and yields
	    iso_name=line.split('&')[1].strip()
	    #print line
	    #print line.split('&')
            yield_data[-1][0].append(line.split('&')[1].strip())
            #if len(isotopes)>0:
            #        if not iso_name in isotopes:
	    #else:    	    
	    yield_data[-1][1].append(float(line.split('&')[2].strip()))
            # for additional data
            for t in range(2,len(yield_data[-1])):
                if column_titles[t] == 'A' or column_titles[t] =='Z':
                    yield_data[-1][t].append(int(line.split('&')[t+1].strip()))

                else:
                    yield_data[-1][t].append(float(line.split('&')[t+1].strip()))
	#choose only isotoopes and right order
        ######reading finished
	#In [43]: tablesN.col_attrs
	#Out[43]: ['Isotopes', 'Yields', 'X0', 'Z', 'A']
	if len(isotopes)>0:
		#print 'correct for isotopes'
		data_new=[]
		for k in range(len(yield_data)):
			#print 'k'
			data_new.append([])
			#print 'len',len(yield_data[k])
			#print ([[]]*len(yield_data[k]))[0]
			for h in range(len(yield_data[k])):
				data_new[-1].append([])
			#print 'testaa',data_new[-1]
			data_all=yield_data[k]
			for iso_name in isotopes:
				if iso_name in data_all[0]:
					#print 'test',data_all[1][data_all[0].index(iso_name)]
					for hh in range(1,len(data_all)):
						data_new[-1][hh].append(data_all[hh][data_all[0].index(iso_name)])
					#data_new[-1][1].append(data_all[2][data_all[0].index(iso_name)])
					#data_new[-1][1].append(data_all[2][data_all[0].index(iso_name)])
				else:
                                        for hh in range(1,len(data_all)):
                                                data_new[-1][hh].append(0)
					#data_new[-1][1].append(0)
					#print 'GRID exclude',iso_name
				data_new[-1][0].append(iso_name)
		#print 'new list'
		#print data_new[0][0]
		#print data_new[0][1]
		yield_data=data_new
        self.yield_data=yield_data
        #table header points to element in yield_data
        self.table_idx={}
        i=0
        self.table_attrs=[]
        self.table_mz=[]
        self.metallicities=[]
        for table1 in table_header:
            for k in range(len(table1)):
                table1[k]=table1[k][2:]
                if 'Table' in table1[k]:
                    self.table_idx[table1[k].split(':')[1].strip()]=i
                    tablename=table1[k].split(':')[1].strip()
                    self.table_mz.append(tablename)
                    metal=tablename.split(',')[1].split('=')[1][:-1]
                    if float(metal) not in self.metallicities:
                        self.metallicities.append(float(metal))
                if table1 ==table_header[0]:
                    if 'Table' in table1[k]:
                        table1[k] = 'Table (M,Z):'
                    self.table_attrs.append(table1[k].split(':')[0].strip())

                #table1.split(':')[1].strip()
            i+=1
        #define  header
        self.header_attrs={}
        #print 'header1: ',header1
        for h in header1:
            self.header_attrs[h.split(':')[0][1:].strip()]=h.split(':')[1].strip()
        self.col_attrs=column_titles
        self.age=age
        self.kin_e=kin_e
        self.lum_bands=lum_bands
        self.m_final=m_final

    def set(self,M=0,Z=-1,specie='',value=0):

	'''
	    Replace the values in column 3 which
	    are usually the yields with value.
	    Use in combination with the write routine
	    to write out modification into new file.

	    M: initial mass to be modified
	    Z: initial Z to 
	    specie: quantity (e.g. yield) of specie will be modified

        '''

        inp='(M='+str(float(M))+',Z='+str(float(Z))+')'
        idx=self.table_idx[inp]
        data=self.yield_data[idx]
        idx_col=self.col_attrs.index('Yields')
        set1=self.yield_data[idx][idx_col]
        specie_all= data[0]
        for k in range(len(set1)):
                    if specie == specie_all[k]:
                        #return set1[k]
			self.yield_data[idx][idx_col][k] = value

    def write_table(self,filename='isotope_yield_table_mod.txt'):

	'''
		Allows to write out table in NuGrid yield table format.
		Note that method has to be generalized for all tables
		and lines about NuGrid removed.

		fname: Table name

		needs ascii_table.py from NuGrid python tools

	'''
	#part of the NuGrid python tools
	import ascii_table as ascii1

	import getpass
	user=getpass.getuser()
	import time
	date=time.strftime("%d %b %Y", time.localtime())
	
	
	tables=self.table_mz


	#write header attrs
	f=open(filename,'w')
	self.header_attrs
	
	out=''
	l='H NuGrid yields Set1: '+self.header_attrs['NuGrid yields Set1']+'\n'
	out = out +l
	l='H Data prepared by: '+user+'\n'	
	out=out +l
	l='H Data prepared date: '+date+'\n'
	out=out +l	
	l='H Isotopes: '+ self.header_attrs['Isotopes'] +'\n'
	out = out +l
	l='H Number of metallicities: '+self.header_attrs['Number of metallicities']+'\n'
	out = out +l
	l='H Units: ' + self.header_attrs['Units'] + '\n'
	out = out + l
	f.write(out)
	f.close()

	for k in range(len(tables)):
		print 'Write table ',tables[k]
		mass=float(self.table_mz[k].split(',')[0].split('=')[1])
		metallicity=float(self.table_mz[k].split(',')[1].split('=')[1][:-1])
		data=self.yield_data[k]	
		idx_y=self.col_attrs.index('Yields')
		yields=data[idx_y]
		idx_x0=self.col_attrs.index('X0')
		mass_frac_ini=data[idx_x0]
		idx_specie=self.col_attrs.index(self.col_attrs[0])
		species=data[idx_specie]
		remn_mass=self.m_final[k][0]
		finalmheader='Mfinal: '+'{:.3E}'.format(remn_mass)
		special_header='Table: (M='+str(mass)+',Z='+str(metallicity)+')'
	
		dcols=[self.col_attrs[0],'Yields','X0']
		data=[species,list(yields),mass_frac_ini]

		ascii1.writeGCE_table(filename=filename,headers=[special_header,finalmheader],data=data,dcols=dcols)

		#add ages
		time=self.age[k]
		
		f1=open(filename,'r')
		lines=f1.readlines()
		f1.close()
		i=-1
		line1=''
		while (True):
			i+=1
			if i>len(lines)-1:
				break
			line=lines[i]
			line1+=lines[i]
			if tables[k] in lines[i]:
				line1+=('H Lifetime: '+'{:.3E}'.format(time)+'\n')
		f1=open(filename,'w')
		f1.write(line1)
		f1.close()





    def get(self,M=0,Z=-1,quantity='',specie=''):

        '''
                Allows to extract table data in 2 Modes:

                1) For extracting of table data for
                   star of mass M and metallicity Z.
                   Returns either table attributes,
                   given by yield.table_attrs
                   or table columns,
                   given by yield.col_attrs.

                2) For extraction of a table attribute
                   from all available tables. Can be
                   directly used in the following way:

                   get(tableattribute)


                M: Stellar mass in Msun
                Z: Stellar metallicity (e.g. solar: 0.02)
                quantity: table attribute or table column
                specie: optional, return certain specie


        '''
	#scale down to Z=0.00001
	#print 'get yields   ',Z
	if float(Z) == 0.00001:
		#scale abundance
		if quantity=='Yields':
			return self.get_scaled_Z(M=M,Z=Z,quantity=quantity,specie=specie)
		#Take all other parameter from Z=0.0001 case
		else:
			Z=0.0001

        all_tattrs=False
        if Z ==-1:
            if M ==0 and len(quantity)>0:
                quantity1=quantity
                all_tattrs=True
            elif (M in self.table_attrs) and quantity == '':
                quantity1=M
                all_tattrs=True
            else:
                print 'Error: Wrong input'
                return 0
            quantity=quantity1


        if (all_tattrs==False) and (not M ==0):
            inp='(M='+str(float(M))+',Z='+str(float(Z))+')'
            idx=self.table_idx[inp]
        #print 'len tableidx:',len(self.table_idx)
        #print 'len age',len(self.age)
        if quantity=='Lifetime':
            if all_tattrs==True:
                data=self.age
            else:
                data=self.age[idx]
            return data
        if quantity =='Total kinetic energy':
            if all_tattrs==True:
                data=self.kin_e
            else:
                data=self.kin_e[idx]
            return data
        if quantity == 'Lyman-Werner band':
            if all_tattrs==True:
                data=[list(i) for i in zip(*self.lum_bands)][0]
            else:
                data=self.lum_bands[idx][0]
            return data
        if quantity== 'Hydrogen-ionizing band':
            if all_tattrs==True:
                data=[list(i) for i in zip(*self.lum_bands)][1]
            else:
                data=self.lum_bands[idx][1]
            return data
        if quantity == 'High-energy band':
            if all_tattrs==True:
                data=[list(i) for i in zip(*self.lum_bands)][2]
            else:
                data=self.lum_bands[idx][2]
            return data
        if quantity == 'Mfinal':
            if all_tattrs==True:
                data=self.m_final
            else:
                data=self.m_final[idx][0]
            return data
        if quantity== 'Table (M,Z)':
            if all_tattrs==True:
                data=self.table_mz
            else:
                data=self.table_mz[idx]
            return data
        if quantity=='masses':
            data_tables=self.table_mz
            masses=[]
            for table in data_tables:
                if str(float(Z)) in table:
                    masses.append(float(table.split(',')[0].split('=')[1]))


            return masses
        else:
            data=self.yield_data[idx]
            if specie=='':
                idx_col=self.col_attrs.index(quantity)
                set1=data[idx_col]
                return set1
            else:
                idx_col=self.col_attrs.index('Yields')
                set1=data[idx_col]
                specie_all= data[0]
                for k in range(len(set1)):
                    if specie == specie_all[k]: #bug was here
                        return set1[k]

    def get_scaled_Z(self,table, table_yields,iniabu,iniabu_scale,M=0,Z=0,quantity='Yields',specie=''):

	'''
		Scaled down yields of isotopes 'He','C', 'O', 'Mg', 'Ca', 'Ti', 'Fe', 'Co','Zn','H','N'
	 	down to Z=1e-5 and Z=1e-6 (for Brian). The rest is set to zero.
	'''

	#print '####################################'
	#print 'Enter routine  get_scaled_Z'

	elem_prim=['He','C', 'O', 'Mg', 'Ca', 'Ti', 'Fe', 'Co','Zn','H']
	elem_sec=['N']

	##Scale down

	import utils as u
	import re
	#table=ry.read_nugrid_yields('yield_tables/prodfac_iso_table.txt')
	#table_yields=ry.read_nugrid_yields('yield_tables/isotope_yield_table.txt')
	#iniabu=u.iniabu('yield_tables/iniabu/iniab1.0E-05GN93_alpha.ppn')
	#iniabu_scale=u.iniabu('yield_tables/iniabu/iniab1.0E-04GN93_alpha.ppn')
	
	iniiso=[]
	iniabu_massfrac=[]
	for k in range(len(iniabu.habu)):
		iso=iniabu.habu.keys()[k]
		iniiso.append(re.split('(\d+)',iso)[0].strip().capitalize()+'-'+re.split('(\d+)',iso)[1])
		iniabu_massfrac.append(iniabu.habu.values()[k])
	#iniabu_scale=u.iniabu('yield_tables/iniabu/iniab1.0E-04GN93_alpha.ppn')
	iniiso_scale=[]
	iniabu_scale_massfrac=[]
	for k in range(len(iniabu_scale.habu)):
		iso=iniabu_scale.habu.keys()[k]
		iniiso_scale.append(re.split('(\d+)',iso)[0].strip().capitalize()+'-'+re.split('(\d+)',iso)[1])
		iniabu_scale_massfrac.append(iniabu_scale.habu.values()[k])


	grid_yields=[]
	grid_masses=[]
	isotope_names=[]
	origin_yields=[]
	for k in range(len(table.table_mz)):
		if 'Z=0.0001' in table.table_mz[k]:
			#print table.table_mz[k]
			mini=float(table.table_mz[k].split('=')[1].split(',')[0])
			grid_masses.append(mini)
			#this is production factor (see file name)
			prodfac=table.get(M=mini,Z=0.0001,quantity='Yields')
			isotopes=table.get(M=mini,Z=0.0001,quantity='Isotopes')
			#this is yields
			yields=table_yields.get(M=mini,Z=0.0001,quantity='Yields')
			mtot_eject=sum(yields)
			origin_yields.append([])
			#print 'tot eject',mtot_eject
			mout=[]
			sumnonh=0
			isotope_names.append([])
			for h in range(len(isotopes)):
				if not (isotopes[h].split('-')[0] in (elem_prim+elem_sec) ):
					#Isotopes/elements not considered/scaled are set to 0
					#mout.append(0)
					#isotope_names[-1].append(isotopes[h])
					continue
				isotope_names[-1].append(isotopes[h])
				idx=iniiso.index(isotopes[h])
				inix=iniabu_massfrac[idx]
				idx=iniiso_scale.index(isotopes[h])
				inix_scale=iniabu_scale_massfrac[idx]
				prodf=prodfac[isotopes.index(isotopes[h])]
				origin_yields[-1].append(yields[isotopes.index(isotopes[h])])
				if isotopes[h].split('-')[0] in elem_prim:
					#primary 
					mout1=(prodf-1.)*(inix_scale*mtot_eject) + (inix*mtot_eject)
					#check if amount destroyed was more than it was initial there
					if mout1<0:
						#print 'Problem with ',isotopes[h]
						#print 'Was more destroyed than evailable'
						#Then only what was there can be destroyed
						mout1=0
					#if isotopes[h] == 'C-13':
					#	print 'inix',inix
					#	print 'inixscale',inix_scale
					#	print 'prodf',prodf
					#	print (prodf)*(inix_scale*mtot_eject)
					#	print (inix*mtot_eject)	
				else:
					#secondary
					mout1=(prodf-1.)*(inix*mtot_eject) + (inix*mtot_eject)
				if (not isotopes[h]) == 'H-1' and (mout1>0):
					sumnonh+= (mout1 - (inix*mtot_eject))
				mout.append(mout1)
			#for mass conservation, assume total mass lost is same as in case of Z=0.0001
			idx_h=isotope_names[-1].index('H-1')		
			mout[idx_h]-=sumnonh
			for k in range(len(mout)):
				mout[k] = float('{:.3E}'.format(mout[k]))		
			grid_yields.append(mout)	



	####data

	idx=grid_masses.index(M)

        all_tattrs=False

	

        if specie=='':
	    return grid_yields[idx]
        else:
	    set1=data[idx]
	    names=isotope_names[idx]
	    for k in range(len(names)):
	        if specie in names[k]:
		    return set1[k]



class read_yield_sn1a_tables():

    def __init__(self,sn1a_table,isotopes):


        '''
                Read SN1a tables.
                Fills up missing isotope yields
                with zeros.
                If different Zs are available
                do ...

        '''

        import re
        if notebookmode==True:
            os.system('sudo python cp.py '+sn1a_table)
            f1=open('tmp/'+sn1a_table)
            lines=f1.readlines()
            f1.close()
            os.system('sudo python delete.py '+sn1a_table)
        else:
            f1=open(sn1a_table)
            lines=f1.readlines()
            f1.close()
        iso=[]
        self.header=[]
        self.col_attrs=[]
        yields=[]
        metallicities=[]
        for line in lines:
            #for header
            if 'H' in line[0]:
                self.header.append(line)
                continue
            if ('Isotopes' in line) or ('Elements' in line):
                l=line.replace('\n','').split('&')[1:]
                self.col_attrs=l
                metallicities=l[1:]
                #print metallicities
                # metallicity dependent yields
                #if len(l)>2:
                #else:
                for k in l[1:]:
                    yields.append([])
                continue
            linesp=line.strip().split('&')[1:]
            iso.append(linesp[0].strip())
            #print iso
            for k in range(1,len(linesp)):
                yields[k-1].append(float(linesp[k]))

        yields1=[]
        #fill up the missing isotope yields with zero
        for z in range(len(yields)):
            yields1.append([])
            for iso1 in isotopes:
                #iso1=iso1.split('-')[1]+iso1.split('-')[0]
                #ison= iso1+((10-len(iso1))*' ')
                if iso1 in iso:
                    yields1[-1].append(yields[z][iso.index(iso1)])
                else:
                    yields1[-1].append(0.)
        self.yields=yields1
        self.metallicities=[]
        for m in metallicities:
            self.metallicities.append(float(m.split('=')[1]))
        #self.metallicities=metallicities
        #print yields1

    def get(self,Z=0,quantity='Yields',specie=''):



        '''
                Allows to extract SN1a table data.
                If metallicity dependent yield tables
                were used, data is taken for the closest metallicity available
                to reach given Z

                quantity: yields only possible atm



        '''
        idx = (np.abs(np.array(self.metallicities)-Z)).argmin()
        yields=self.yields[idx]

        return np.array(yields)



class read_yield_rawd_tables():

    def __init__(self,rawd_table,isotopes):


        '''
                Read RAWD tables.
                Fills up missing isotope yields
                with zeros.
                If different Zs are available
                do ...

        '''

        import re
        if notebookmode==True:
            os.system('sudo python cp.py '+rawd_table)
            f1=open('tmp/'+rawd_table)
            lines=f1.readlines()
            f1.close()
            os.system('sudo python delete.py '+rawd_table)
        else:
            f1=open(rawd_table)
            lines=f1.readlines()
            f1.close()
        iso=[]
        self.header=[]
        self.col_attrs=[]
        yields=[]
        metallicities=[]
        for line in lines:
            #for header
            if 'H' in line[0]:
                self.header.append(line)
                continue
            if ('Isotopes' in line) or ('Elements' in line):
                l=line.replace('\n','').split('&')[1:]
                self.col_attrs=l
                metallicities=l[1:]
                #print metallicities
                # metallicity dependent yields
                #if len(l)>2:
                #else:
                for k in l[1:]:
                    yields.append([])
                continue
            linesp=line.strip().split('&')[1:]
            iso.append(linesp[0].strip())
            #print iso
            for k in range(1,len(linesp)):
                yields[k-1].append(float(linesp[k]))

        yields1=[]
        #fill up the missing isotope yields with zero
        for z in range(len(yields)):
            yields1.append([])
            for iso1 in isotopes:
                #iso1=iso1.split('-')[1]+iso1.split('-')[0]
                #ison= iso1+((10-len(iso1))*' ')
                if iso1 in iso:
                    yields1[-1].append(yields[z][iso.index(iso1)])
                else:
                    yields1[-1].append(0.)
        self.yields=yields1
        self.metallicities=[]
        for m in metallicities:
            self.metallicities.append(float(m.split('=')[1]))
        #self.metallicities=metallicities
        #print yields1

    def get(self,Z=0,quantity='Yields',specie=''):



        '''
                Allows to extract rawd table data.
                If metallicity dependent yield tables
                were used, data is taken for the closest metallicity available
                to reach given Z

                quantity: yields only possible atm



        '''
        idx = (np.abs(np.array(self.metallicities)-Z)).argmin()
        yields=self.yields[idx]

        return np.array(yields)




'''
Adapted from NuGrid Utility class


'''

#import numpy as np
#import scipy as sc
#import ascii_table as att
#from scipy import optimize
#import matplotlib.pyplot as pl
#import os

class iniabu():
    '''
    This class in the utils package reads an abundance
    distribution file of the type iniab.dat. It then provides you
    with methods to change some abundances, modify, normalise and
    eventually write out the final distribution in a format that
    can be used as an initial abundance file for ppn. This class
    also contains a method to write initial abundance files for a
    MESA run, for a given MESA netowrk.
    '''
    # clean variables that we will use in this class

    filename = ''

    def __init__(self,filename):
        '''
        Init method will read file of type iniab.dat, as they are for
        example found in the frames/mppnp/USEPP directory.

        An instance of this class will have the following data arrays
        z      charge number
        a      mass number
        abu    abundance
        names  name of species
        habu   a hash array of abundances, referenced by species name
        hindex hash index returning index of species from name

        E.g. if x is an instance then x.names[4] gives you the
        name of species 4, and x.habu['c 12'] gives you the
        abundance of C12, and x.hindex['c 12'] returns
        4. Note, that you have to use the species names as
        they are provided in the iniabu.dat file.

        Example - generate modified input file ppn calculations:

        import utils
        p=utils.iniabu('iniab1.0E-02.ppn_asplund05')
        sp={}
        sp['h   1']=0.2
        sp['c  12']=0.5
        sp['o  16']=0.2
        p.set_and_normalize(sp)
        p.write('p_ini.dat','header for this example')

        p.write_mesa allows you to write this NuGrid initial abundance
        file into a MESA readable initial abundance file.
        '''
        f0=open(filename)
        sol=f0.readlines()
        f0.close

        # Now read in the whole file and create a hashed array:
        names=[]
        z=[]
        yps=np.zeros(len(sol))
        mass_number=np.zeros(len(sol))
        for i in range(len(sol)):
            z.append(int(sol[i][1:3]))
            names.extend([sol[i].split("         ")[0][4:]])
            yps[i]=float(sol[i].split("         ")[1])
            try:
                mass_number[i]=int(names[i][2:5])
            except ValueError:
                #print "WARNING:"
                #print "This initial abundance file uses an element name that does"
                #print "not contain the mass number in the 3rd to 5th position."
                #print "It is assumed that this is the proton and we will change"
                #print "the name to 'h   1' to be consistent with the notation used"
                #print "in iniab.dat files"
                names[i]='h   1'
            mass_number[i]=int(names[i][2:5])
        # now zip them together:
        hash_abu={}
        hash_index={}
        for a,b in zip(names,yps):
            hash_abu[a] = b

        for i in range(len(names)):
            hash_index[names[i]] = i

        self.z=z
        self.abu=yps
        self.a=mass_number
        self.names=names
        self.habu=hash_abu
        self.hindex=hash_index


    def iso_abundance(self,isos):
        '''
        This routine returns the abundance of a specific isotope. Isotope given as, e.g., 'Si-28' or as list ['Si-28','Si-29','Si-30']
        '''
        if type(isos) == list:
            dumb = []
            for it in range(len(isos)):
                dumb.append(isos[it].split('-'))
            ssratio = []
            isos = dumb
            for it in range(len(isos)):
                ssratio.append(self.habu[isos[it][0].ljust(2).lower() + str(int(isos[it][1])).rjust(3)])
        else:
            isos = isos.split('-')
            ssratio = self.habu[isos[0].ljust(2).lower() + str(int(isos[1])).rjust(3)]
        return ssratio


def read_iniabu(filename,isotopes):
    import read_yields as ry
    if notebookmode==True:
        os.system('sudo python cp.py '+'iniabu/'+filename)
        iniabu_class=ry.iniabu('tmp/'+filename)
        iniabu= np.array(iniabu_class.iso_abundance(isotopes))
        os.system('sudo python delete.py '+filename)
    else:
        iniabu_class=ry.iniabu(filename)
        iniabu= np.array(iniabu_class.iso_abundance(isotopes))
    return iniabu

def read_strip_param(filename):
	'''
		To read Elses simulatin files
	'''

	import read_yields as ry

	f1=open(filename)
	lines=f1.readlines()
	f1.close()
	info=['timebins','SFR','Mcool','Meject','Minfall','Mreinc','Mcoldgas','Mhotgas','Mejectedgas','Mstripej','Mstriphot','Mstripcold','Mstripstar']
	data=[]
	for k in range(len(lines)):
		#to skip header
		if k <14:
			continue
		#to read column header
		if k==14:
			cheader=lines[k].split()
			idx=[]
			for h in info:
				idx.append(cheader.index(h))
				data.append([])		
			continue
		#units line
		if k==15:
			continue
		line=lines[k].split()
		for i in range(len(idx)):
			data[i].append(float(line[idx[i]]))
	data_dict={}
	for k in range(len(data)):
		data_dict[info[k]]=data[k]		

	return data_dict



