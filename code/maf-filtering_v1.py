#!/usr/bin/python
###########################################################################################################################
# maf-filtering.py version 1.0
# Python 2.7.6
# author: Minjeong Kim
# This code is for maf filtering.
# * command example : python maf-filtering_v1.py -vcf imputation_chrN.vcf -maf 0.07
# -vcf : Input the imputed vcf file.
# -maf : minor allele frequency value. SNVs whose maf value is less than the set value are removed(recommend MAF 0.07 for 1000GP3 and MAF 0.005 for HRC v1.1).
# output : 0.07_imputation_chrN.vcf
###########################################################################################################################
import sys

def match(vcf_file, maf_value):
    output = open(maf_value+'_'+vcf_file,'w+')
    input = open(vcf_file,'r')    # Open the imputation_chrN.vcf
    maf_value = float(maf_value)
    for line in input:
        arr = line.split('\t')
        # Check header line.
        if arr[0].find('#')==0:
            output.write(line)
        else:
            # Find maf value.
            temp = arr[7].split(';')
            maf = temp[1].split('=')
            maf = float(maf[1])
            if maf>maf_value:
                output.write(line)
    print('maf-filtering finish.')
    input.close()
    output.close()
    
###########################################################################################################################
########################################################## MAIN ###########################################################
###########################################################################################################################
print('################## maf-filtering v1.0 ###################')
print('Checking command...')
if len(sys.argv)==5 :
    try:
        V = sys.argv.index('-vcf')
        M = sys.argv.index('-maf')
        vcf_file = sys.argv[V+1]
        maf_value = sys.argv[M+1]
    except:
        print('Error : Command not found!')
        sys.exit(1)
else :
    print('Error : Please enter all commands.')
    sys.exit(1)
    
print('################## INFO ##################')
print('vcf_file : '+vcf_file)
print('maf_value : '+maf_value)
print('################## matching.... ##################')
match(vcf_file, maf_value)
print('')
print('* New file : '+maf_value+'_'+vcf_file)

###########################################################################################################################
