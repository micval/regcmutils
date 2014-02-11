#!/bin/bash

declare -A globalattr
while read line ; do
    att=`echo $line |cut -d: -f1`
    val=`echo $line |cut -d: -f2`

    globalattr[$att]="$val"
done < globalattributes.txt

year1=2006
year2=2100
timespec=dayavg
realm=STS
domainname=${globalattr[CORDEX_domain]}
gcmodel=${globalattr[driving_model_id]}
cmip5experiment=${globalattr[experiment_id]}
cmip5ensemblemember=${globalattr[driving_model_ensemble_member]}
rcmodel=${globalattr[model_id]}
rcmversion=${globalattr[rcm_version_id]}
experiment=${globalattr[experiment_id]}
today=`date`
bufferzonewidth=12

outdomainfile=${domainname}_cdo.txt

outfrequency='day'
cell_methods='time: mean'
outprefix='esgf'

dobufferzonecut=1
dointerpolate=1
docorrectatt=1
docorrectvar=1
docorrectdim=0
dotimesplit=0
dotimemerge=1

xdimname='x'
ydimname='y'

#decades=10
#dec_start[0]=1960
#dec_end[0]=1960
#dec_start[1]=1961
#dec_end[1]=1965
#dec_start[2]=1966
#dec_end[2]=1970
#dec_start[3]=1971
#dec_end[3]=1975
#dec_start[4]=1976
#dec_end[4]=1980
#dec_start[5]=1981
#dec_end[5]=1985
#dec_start[6]=1986
#dec_end[6]=1990
#dec_start[7]=1991
#dec_end[7]=1995
#dec_start[8]=1996
#dec_end[8]=2000
#dec_start[9]=2001
#dec_end[9]=2005

decades=19
dec_start[0]=2006
dec_end[0]=2010
dec_start[1]=2011
dec_end[1]=2015
dec_start[2]=2016
dec_end[2]=2020
dec_start[3]=2021
dec_end[3]=2025
dec_start[4]=2026
dec_end[4]=2030
dec_start[5]=2031
dec_end[5]=2035
dec_start[6]=2036
dec_end[6]=2040
dec_start[7]=2041
dec_end[7]=2045
dec_start[8]=2046
dec_end[8]=2050
dec_start[9]=2051
dec_end[9]=2055
dec_start[10]=2056
dec_end[10]=2060
dec_start[11]=2061
dec_end[11]=2065
dec_start[12]=2066
dec_end[12]=2070
dec_start[13]=2071
dec_end[13]=2075
dec_start[14]=2076
dec_end[14]=2080
dec_start[15]=2081
dec_end[15]=2085
dec_start[16]=2086
dec_end[16]=2090
dec_start[17]=2091
dec_end[17]=2095
dec_start[18]=2096
dec_end[18]=2100

if [ ! -f vardefs.txt ]; then
    ln -s vardefs-$realm-$timespec.txt vardefs.txt
fi

for infile in $@; do
    file=${infile##*/}
    tmpfilename=$file
    if [ "$dobufferzonecut" == "1" ]; then
        jx=`./getncdim.py $infile $xdimname`
        iy=`./getncdim.py $infile $ydimname`
        startx=$bufferzonewidth
        starty=$bufferzonewidth

        endx=`expr $jx - $bufferzonewidth - 1`
        endy=`expr $iy - $bufferzonewidth - 1`
        tmpfilename=tmp_$file
        ncks -d $xdimname,$startx,$endx -d $ydimname,$starty,$endy $infile $tmpfilename
    else
        cp $infile $tmpfilename
    fi
    variable=`echo $file |cut -d. -f3`

    if [ "$dointerpolate" == "1" ]; then
        tmpfilename2=`basename $tmpfilename .nc`.$domainname.nc
        cdo remapbil,$outdomainfile $tmpfilename $tmpfilename2
        rm $tmpfilename
        tmpfilename=$tmpfilename2
    fi

    if [ "$docorrectvar" == "1" ]; then
        vardef=`grep "^$variable" vardefs.txt`
        varin=`echo $vardef |cut -d: -f1`
        varout=`echo $vardef |cut -d: -f2`
        long_name=`echo $vardef |cut -d: -f3`
        standard_name=`echo $vardef |cut -d: -f4`
        units=`echo $vardef |cut -d: -f5`
        cell_methods=`echo $vardef |cut -d: -f7`
        postproc=`echo $vardef |cut -d: -f8`

        if [ "$varin" != "$varout" ]; then
            ncrename -v $varin,$varout $tmpfilename
        fi

        ncatted -a long_name,$varout,o,c,"$long_name" -a standard_name,$varout,o,c,"$standard_name" -a units,$varout,o,c,"$units" $tmpfilename
        if [ "$postproc" != "" ]; then
            cdo $postproc $tmpfilename tmp2_$file
            mv tmp2_$file $tmpfilename
        fi
    fi

    if [ "$docorrectatt" == "1" ]; then
        while read atline; do
            attname=`echo $atline |cut -d: -f1`
            attval=`echo $atline |cut -d: -f2 |sed "s/{TODAY}/$today/; s/{FREQUENCY}/$outfrequency/"`
            ncatted -a ${attname},global,o,c,"${attval}" $tmpfilename
        done <globalattributes.txt # end while read atline
    fi

    if [ "$dotimesplit" == "1" ]; then
        for((i=0;i<$decades;i++)); do
            my_years=''
            for((y=${dec_start[$i]};y<=${dec_end[$i]};y++)); do
                if [ "$my_years" != "" ]; then
                    my_years=$my_years","
                fi
                my_years=$my_years"$y"
            done
            cdo setreftime,1949-12-01,00:00 -settaxis,${dec_start[$i]}-01-01,12:00,1day -selyear,$my_years $tmpfilename ${varout}_${domainname}_${gcmodel}_${cmip5experiment}_${cmip5ensemblemember}_${rcmodel}_${rcmversion}_${outfrequency}_${dec_start[$i]}0101-${dec_end[$i]}1231.nc
        done
    fi

    if [ "$docorrectdim" == "1" ]; then
        ncrename -v xlon,lon -v xlat,lat -d $xdimname,xc -d $ydimname,yc -v rcm_map,Lambert_conformal $tmpfilename
        ncatted -a coordinates,$varout,o,c,"lon lat" $tmpfilename
    fi

    if [ `./checkncdim.py $tmpfilename m2` == "True" ]; then
        ./correct-m2-value.py $tmpfilename
        ncrename -v m2,height -d m2,height $tmpfilename
        ncatted -a long_name,height,o,c,"height" $tmpfilename
    fi

    if [ "$docorrectvar" == "1" -a "$varin" != "$varout" ]; then
        mv $tmpfilename `echo $tmpfilename | sed "s/$varin/$varout/"`
    fi
done

if [ "$dotimemerge" == "1" ]; then
    infilename_pattern="tmp_Euro-CORDEX-CMIP5_${realm}.%4d%02d0100.%s" 
    if [ "$dointerpolate" == "1" ]; then
        infilename_pattern=$infilename_pattern"."$domainname".nc"
    else
        infilename_pattern=$infilename_pattern.nc
    fi

    ./domerge.py -s $year1 -e $year2 --mergedfilename_pattern="%s_${domainname}_${gcmodel}_${experiment}_${cmip5ensemblemember}_${rcmodel}_${rcmversion}_${outfrequency}_%4d0101-%4d1231.nc" --variables=pr --infilename_pattern=$infilename_pattern # --cdo_postproc=dayavg 
fi
