mkdir ribotyper-results
/rna/infernal-1.1.2/bin/esl-sfetch --index sequences.fasta > /dev/null
/rna/infernal-1.1.2/bin/esl-seqstat --dna -a sequences.fasta > ribotyper-results/ribotyper-results.ribotyper.seqstat
/usr/bin/time -p /rna/infernal-1.1.2/bin/cmsearch  --F1 0.02 --doF1b --F1b 0.02 --F2 0.001 --F3 0.00001 --trmF3 --nohmmonly --notrunc --noali  -T 10. -Z 0.000348 --cpu 0 --verbose --tblout ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl /rna/ribovore/models/ribo.0p20.extra.cm sequences.fasta > /dev/null 2> ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err.tmp;tail -n 3 ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err.tmp > ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.time;awk 'n>=3 { print a[n%3] } { a[n%3]=$0; n=n+1 }' ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err.tmp > ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err;rm ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err.tmp;
rm ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.err
grep -v ^# ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl | sort -k 1,1 -k 3,3rn > ribotyper-results/ribotyper-results.ribotyper.r1.cmsearch.tbl.sorted
sort -n ribotyper-results/ribotyper-results.ribotyper.r1.unsrt.short.out >> ribotyper-results/ribotyper-results.ribotyper.r1.short.out
sort -n ribotyper-results/ribotyper-results.ribotyper.r1.unsrt.long.out >> ribotyper-results/ribotyper-results.ribotyper.r1.long.out
/rna/infernal-1.1.2/bin/esl-sfetch -f sequences.fasta ribotyper-results/ribotyper-results.ribotyper.LSU_rRNA_bacteria.sfetch > ribotyper-results/ribotyper-results.ribotyper.LSU_rRNA_bacteria.fa
/usr/bin/time -p /rna/infernal-1.1.2/bin/cmsearch  --hmmonly  -T 10. -Z 0.000348 --cpu 0 --verbose --tblout ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl /rna/ribovore/models/ribo.0p15.LSU_rRNA_bacteria.cm ribotyper-results/ribotyper-results.ribotyper.LSU_rRNA_bacteria.fa > /dev/null 2> ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err.tmp;tail -n 3 ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err.tmp > ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.time;awk 'n>=3 { print a[n%3] } { a[n%3]=$0; n=n+1 }' ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err.tmp > ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err;rm ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err.tmp;
rm ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl.err
cat ribotyper-results/ribotyper-results.ribotyper.r2.LSU_rRNA_bacteria.cmsearch.tbl > ribotyper-results/ribotyper-results.ribotyper.r2.all.cmsearch.tbl
grep -v ^# ribotyper-results/ribotyper-results.ribotyper.r2.all.cmsearch.tbl | sort -k 1,1 -k 15,15rn -k 16,16g > ribotyper-results/ribotyper-results.ribotyper.r2.all.cmsearch.tbl.sorted
sort -n ribotyper-results/ribotyper-results.ribotyper.r2.unsrt.short.out >> ribotyper-results/ribotyper-results.ribotyper.r2.short.out
sort -n ribotyper-results/ribotyper-results.ribotyper.r2.unsrt.long.out >> ribotyper-results/ribotyper-results.ribotyper.r2.long.out
# Wed Nov 25 10:43:29 GMT 2020
# Linux hx-noah-07-15.ebi.ac.uk 3.10.0-693.5.2.el7.x86_64 #1 SMP Fri Oct 13 10:46:25 EDT 2017 x86_64 GNU/Linux
# RIBO-SUCCESS
