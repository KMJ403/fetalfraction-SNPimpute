#!/usr/bin/python
###########################################################################################################################
# fetalfraction-SNPimpute.py version 2.0
# Python 2.7.6
# Author: Minjeong Kim 
# Contact: baekho403@gmail.com
# This code is for estimating fetal fraction using imputed PLINK(ped/map) files.
# * Naming rules : sampleID.pileup / chrN.ped / chrN.map (For ped and map files, they must have the format 'chrN.map' and 'chrN.ped')
# The sampleID of the pileup file should be the same as the name of the same sample in the ped / map file.
# The input directory should contain all ped/map files from chr1 to chr22 and pileup files.
# * Command example : python fetalfraction-SNPimpute_v1.py -N sampleID.pileup -I /input/data/ -O /output/data/
# -N : pileup file. The name of this pileup file MUST be the same as the name of the sample ID in the PLINK file.
# -I : Input directory. The input directory should contain all ped/map files from chr1 to chr22 and pileup files.
# -O : Output directory(output file : sampleID.FF).
###########################################################################################################################
import re
import os
import sys, getopt
import commands
snp = {}
FF = [0.0]*2
input_dir = './'
output_dir = './'
# Match the map / ped file and save it as a dictionary.
def make_dict(sampleID):
    chr_check = ['0']*22
    found_sampleID = 0
    for i in range(1,23):
        # For ped and map files, they must have the format 'chrN.map' and 'chrN.ped'
        if os.path.exists(input_dir+'chr'+str(i)+'.map') and os.path.exists(input_dir+'chr'+str(i)+'.ped'):
            input_map = open(input_dir+'chr'+str(i)+'.map','r')   # Open the /input_dir/chrN.map
            text_map = input_map.readlines()
            input_ped = open(input_dir+'chr'+str(i)+'.ped','r')   # Open the /input_dir/chrN.ped
            text_ped = input_ped.readlines()
            for line in text_ped:
                arr_ped = line.split('\t')
                if arr_ped[0] == sampleID:
                    found_sampleID = 1  # Check if sampleID exists in the ped file.
                    break
            if found_sampleID == 0:
                print('!!! Error : No matching sampleID exists.')
                sys.exit(1)
            n=1
            # Combine the map file and the ped file.
            # key = 'chrN_position'
            for line in text_map:
                arr_map = line.split('\t')
                position = arr_map[3].split('\n')
                position = position[0]
                key = 'chr'+arr_map[0]+'_'+position
                if not snp.has_key(key):
                    snp[key] = []
                snp[key].append(key)
                snp[key].append(arr_ped[n])
                n = n+1
            input_map.close()
            input_ped.close()
            print ('chr'+str(i)+' ped/map check. Dictionary finish.')
            chr_check[i-1]='1'
        elif os.path.exists(input_dir+'chr'+str(i)+'.map') or os.path.exists(input_dir+'chr'+str(i)+'.ped'):
            print('!!! Error : chr'+str(i)+' ped or map file does not exist.')
            print('You need a pair of ped / map files of the same chromosome.')
            sys.exit(1)
        else:
            print('chr'+str(i)+' ped and map file does not exist.')
    # ped/map file check.
    try:
        ck = chr_check.index('1')
    except:
        print('!!! Error : There is no ped/map file.')
        sys.exit(1)
###########################################################################################################################
# Find SNPs whose map position matches the position of the pileup file.
def match(fullname, sampleID):
    chr = 'chr0'
    # 'sampleID_match_list' is created.
    output = open(output_dir+sampleID+'_match_list-temporary','w+')
    input = open(input_dir+fullname,'r')
    for line in input:
        arr = line.split('\t')
        try:
            if arr[0] == 'chrX':
                break
            else:
                if chr != arr[0]:
                    chr = arr[0]
                    print(chr+' position matching...')
                # key = 'chrN_position'
                key = arr[0]+'_'+arr[1]
                # Find the same key in PLINK(pad/map) files and pileup file.
                if snp[key][0] == key:
                    output.write(snp[key][1]+'\t'+line)
        except:
            pass
    input.close()
    output.close()
###########################################################################################################################
# Generate homozygous alleles list(A).
def homo(sampleID):
    input = open(output_dir+sampleID+'_match_list-temporary','r')
    output = open(output_dir+sampleID+'_A-temporary','w+')
    text = input.readlines()
    for line in text:
        arr =line.split()
        # Find homozgous alleles. (ex. A A)
        if len(arr)>6 and len(arr[0])<2 and arr[0]==arr[1] :
            if arr[6].find('*')==-1:
                ref = arr[0]
                if ref == 'A' or ref == 'C' or ref == 'G' or ref == 'T':
                    output.write(line)
            else:
                if arr[6].find('A')!=-1 or arr[6].find('C')!=-1 or arr[6].find('G')!=-1 or arr[6].find('T')!=-1 or arr[6].find('a')!=-1 or arr[6].find('c')!=-1 or arr[6].find('g')!=-1 or arr[6].find('t')!=-1:
                    ref = arr[0]
                    if ref == 'A' or ref == 'C' or ref == 'G' or ref == 'T':
                        output.write(line)
    input.close()
    output.close()
###########################################################################################################################
# Find non-maternal-alleles(B).
def filter(sampleID):
    ps = 0
    input = open(output_dir+sampleID+'_A-temporary','r')
    output = open(output_dir+sampleID+'_B-temporary','w+')
    text = input.readlines()
    for line in text:
        arr =line.split()
        ref = arr[0]
        alt_list = list(arr[6])
        A = []
        B = []
        for i in range(len(alt_list)):
            if ps > 0:   # insertion, deletion pass
                ps = ps-1
                continue
            if alt_list[i] == '+' or alt_list[i] == '-':
                ps = int(alt_list[i+1])+1
                if isNumber(alt_list[i+2]):
                    ps = int(alt_list[i+1])*10 + int(alt_list[i+2]) + 2
                try:
                    if isNumber(alt_list[i+3]):
                        ps = int(alt_list[i+1])*100 + int(alt_list[i+2])*10 + int(alt_list[i+3]) + 3
                except IndexError:
                    continue
                continue
            if alt_list[i]=='^':
                ps = 1
                continue
            if alt_list[i] == ref or alt_list[i] == ref.lower(): # homozygous alleles
                A.append(alt_list[i])
                FF[0]=FF[0]+1   # count homozygous alleles
            if alt_list[i]== 'A' or alt_list[i]== 'C' or alt_list[i]== 'G' or alt_list[i]== 'T' or alt_list[i]== 'a' or alt_list[i]== 'c' or alt_list[i]== 'g' or alt_list[i]== 't':
                if (ref.lower() != alt_list[i]) and (ref != alt_list[i]):	# non-maternal alleles
                    B.append(alt_list[i])
                    FF[1]=FF[1]+1
        if len(B)>0:
            output.write(arr[0]+' '+arr[1]+'\t'+arr[2]+'\t'+arr[3]+'\t'+arr[4]+'\t'+arr[5]+'\t'+arr[6]+'\t'+str(A)+'\t'+str(B)+'\n')
    input.close()
    output.close()
###########################################################################################################################
# fetal fraction calculation.
def cal_ff(sampleID):   # input : sampleID_match_list, sampleID_A, sampleID_B
    output = open(output_dir+sampleID+'_FF','w+')
    NMA_fraction = (FF[1]/(FF[0]+FF[1]))*100  # fraction of non maternal alleles = (B/(A+B))*100
    # ** This parameter applies to imputation using 1000 Genome phase3. **
    # ** Please use 'Fetal_fraction=10.54*NMA_fraction-15.42' for HRC v1.1. **
    # ** This parameter is not absolute and may vary depending on the fitering method and the state of the data. **
    Fetal_fraction = 5.76*NMA_fraction-17.36
    output.write('non maternal alleles fraction'+'\t'+'fetal fraction'+'\n')
    output.write(str(NMA_fraction)+'\t'+str(Fetal_fraction))
###########################################################################################################################
# Delete temporary files.
def delete_file(sampleID):
    try:
        print('Delete temporary files.')
        cmd = 'rm '+output_dir+sampleID+'_*-temporary'
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            sys.stderr.write(output)
            sys.exit(1)
    except:
        print('ERROR!!')
        pass
###########################################################################################################################
def isNumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
###########################################################################################################################
########################################################## MAIN ###########################################################
###########################################################################################################################
print('################## fetalfraction-SNPimpute v2.0 ###################')
print('Checking command...')
if len(sys.argv)==7:
    try:
        N = sys.argv.index('-N')
        I = sys.argv.index('-I')
        O = sys.argv.index('-O')
        filename = sys.argv[N+1]
        sampleID = filename.split('.')
        sampleID = sampleID[0]
        input_dir = sys.argv[I+1]
        output_dir = sys.argv[O+1]
    except:
        print('!!! Error : Command not found!')
        sys.exit(1)
else :
    print('!!! Error : Please enter all commands.')
    sys.exit(1)

print('################## INFO ###################')
print('filename : '+filename)
print('sampleID : '+sampleID)
print('input dir : '+input_dir)
print('output dir : '+output_dir)

if not os.path.exists(input_dir+filename):
    print('!!! Error : '+input_dir+filename+' file does not exist.')
    sys.exit(1)
print('################## MAKE DICTIONARY ###################')
make_dict(sampleID)
print('################## MATCHING... ###################')
match(filename, sampleID)
print('################## COUNTING... ###################')
if os.path.exists(output_dir+sampleID+'_match_list-temporary'):
    homo(sampleID)
    print('Create homozygous list...')
else :
    print('!!! Error : '+sampleID+'_match_list-temporary file does not exist.')
    sys.exit(1)
if os.path.exists(output_dir+sampleID+'_A-temporary'):
    filter(sampleID)
    print('Create non_maternal_alleles list...')
else :
    print('!!! Error : '+sampleID+'_A-temporary file does not exist.')
    sys.exit(1)
print('################## CALCULATING FETAL FRACTION ###################')
cal_ff(sampleID)
delete_file(sampleID)   # ** If you do not want to delete temporary files(match_list, A_list, B_list), comment out this line.
print('')
print('* New file : '+sampleID+'_FF')
print('FINISH')

###########################################################################################################################