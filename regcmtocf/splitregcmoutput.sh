#!/bin/bash


declare -A variables

while read atline; do
    varname=`echo $atline |cut -d: -f1`
    variables[$varname]=$varname
done <vardefs.txt # end while read atline

for file in $@; do
    for var in "${!variables[@]}"; do
        varstoget="iy,jx,xlon,xlat,time,time_bnds,rcm_map,$var"
        if [ `./getncdimofvar.py $file m2 $var` == "True" ]; then
            varstoget=$varstoget",m2"
        fi
        ncks -v $varstoget $file `basename $file .nc`.$var.nc
    done
done
