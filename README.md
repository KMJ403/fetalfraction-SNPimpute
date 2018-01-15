fetalfraction-SNPimpute guidelines v1.0
=
It was designed to run on Ubuntu 14.04.5 LTS (GNU/Linux 4.4.0-66-generic x86_64) platform.

Installing
-
* PLINK v1.90b3.45 64-bit : https://www.cog-genomics.org/plink2
* vcfCooker v1.17 : https://github.com/statgen/gotcloud/releases
* shapeit2 v2.r837 : https://mathgen.stats.ox.ac.uk/genetics_software/shapeit/shapeit.html
* Minimac3 v2.0.1 : https://genome.sph.umich.edu/wiki/Minimac3
* Bcftools v1.3.1-209-g1618245 : http://www.htslib.org/download/
* vcftools v0.1.11 : http://vcftools.sourceforge.net/downloads.html

Phasing
-
**Change the PLINK(ped/map) file to vcf format.**
	
	plink --file sample --recode vcf --no-pheno --no-fid --no-parents --no-sex --out sample
The vcf file is separated into 22 vcf files by chromosome.

If the vcf files are not sorted, use the following command to sort and then compress the file.

	vcf-sort sample_chrN.vcf | bgzip -c > sample_chrN.vcf.gz
*chrN : chr1~22*

**Converts vcf files to PLINK Binary files(BED/BIM/FAM) format for Phasing step.**


	vcfCooker --in-vcf sample_chrN.vcf.gz --write-bed --out sample_chrN
**Estimation of haplotypes(aka phasing).**

genetic maps can be downloaded from [here](https://mathgen.stats.ox.ac.uk/genetics_software/shapeit/shapeit.html#gmap).

	shapeit --input-bed sample_chrN.bed sample_chrN.bim sample_chrN.fam --input-map genetic_map_chrN_combined_b37.txt --output-max sample_chrN.phased --effective-size 11418

**Convert the haps file(.haps) to vcf format.**


	shapeit -convert --input-haps sample_chrN.phased --output-vcf sample_chrN.phased.vcf

Imputation
-
1000 genome phase 3 reference panel download : 

http://www.internationalgenome.org

ftp://share.sph.umich.edu/minimac3/G1K_P3_VCF_Files.tar.gz

**Using Minimac3 v2.0.1 for imputation.**


	Minimac3 --refHaps refPanel.chrN.vcf --haps sample_chrN.phased.vcf --prefix sample_chrN.phased.imputed --chr N --noPhoneHome --format GT,DS,GP --allTypedSites --cpus 30
A detailed description of command line options can be found at [here](https://genome.sph.umich.edu/wiki/Minimac3_-_Full_List_of_Options).

Filtering
-
MAF filtering code can be downloaded from [here](https://github.com/KMJ403/fetalfraction-SNPimpute/tree/master/code).

Command line options :

*-vcf : Input the imputed vcf file.*

*-maf : minor allele frequency value. SNVs whose maf value is less than the set value are removed(recommend MAF 0.07 for 1000GP3).*

**maf filtering**


	python maf-filtering_v1.py –vcf sample_chrN.phased.imputed.dose.vcf –maf 0.07
**indels remove**


	bcftools view --exclude-types indels 0.07_sample_chrN.phased.imputed.dose.vcf -o sample_chrN.filter1.vcf
**Change the vcf file to PLINK(ped/map) format.**


	vcftools --vcf sample_chrN.filter1.vcf --out sample_chrN.filter1 --plink
**Last filtering**


	plink --file sample_chrN.filter1 --geno 0.1 --mind 0.1 --hwe 1e-3 --recode --out sample_chrN.filter2 --noweb
**Modify the format of the ped file.**

Reformatting code can be downloaded from [here](https://github.com/KMJ403/fetalfraction-SNPimpute/tree/master/code).

	python ped-reformat_v1.py sample_chrN.filter2.ped
Estimation fetal fraction
-
Using imputed PLINK(ped/map) files. Estimating fetal fraction code can be downloaded from [here](https://github.com/KMJ403/fetalfraction-SNPimpute/tree/master/code).

Command line options :

*-N : pileup file. The name of this pileup file MUST be the same as the name of the sample ID in the PLINK file.*

*-I : Input directory. The input directory should contain all ped/map files from chr1 to chr22 and pileup files.*

*-O : Output directory(output file : sampleID.FF).*

**Estimation fetal fraction**


	python fetalfraction-SNPimpute_v2.py -N sampleID.pileup -I /input/data/ -O /output/data/
We provide 'pileup file' and 'imputed(using 1000GP3) PLINK file' to help you understand the input values. These files contain only information about chromosome 22. 

Sample source can be downloaded from [here](https://github.com/KMJ403/fetalfraction-SNPimpute/tree/master/sample).
