#!/bin/bash -x

year1=1960
year2=2005
timespec=dayavg
realm=STS
domainname='EUR-44'
gcmodel='ERAINT'
cmip5experiment='historical'
cmip5ensemblemember='r1i1p1'
rcmodel='CUNI-RegCM'
rcmversion='v1'
experiment='historical'
today="2012-12-11-T23:15:09Z"
bufferzonewidth=12

outfrequency='day'
cell_methods='time: mean'

docorrectatt=1
docorrectvar=1
dotimesplit=0
dotimemerge=1
dobufferzonecut=1

xdimname='x'
ydimname='y'

decades=3
dec_start[0]=1989
dec_end[0]=1990
dec_start[1]=1991
dec_end[1]=2000
dec_start[2]=2001
dec_end[2]=2008

if [ ! -f vardefs.txt ]; then
    ln -s vardefs-$realm-$timespec.txt vardefs.txt
fi

for file in $@; do
    if [ "$dobufferzonecut" == "1" ]; then
        jx=`./getncdim.py $file $xdimname`
        iy=`./getncdim.py $file $ydimname`
        startx=$bufferzonewidth
        starty=$bufferzonewidth

        endx=`expr $jx - $bufferzonewidth - 1`
        endy=`expr $iy - $bufferzonewidth - 1`
        ncks -d $xdimname,$startx,$endx -d $ydimname,$starty,$endy $file tmp_$file
    fi
    variable=`echo $file |cut -d. -f3`

    if [ "$docorrectvar" == "1" ]; then
        vardef=`grep "^$variable" vardefs.txt`
        varin=`echo $vardef |cut -d: -f1`
        varout=`echo $vardef |cut -d: -f2`
        long_name=`echo $vardef |cut -d: -f3`
        standard_name=`echo $vardef |cut -d: -f4`
        units=`echo $vardef |cut -d: -f5`

        ncrename -v $varin,$varout tmp_$file
        ncatted -a long_name,$varout,o,c,"$long_name" tmp_$file
        ncatted -a standard_name,$varout,o,c,"$standard_name" tmp_$file
        ncatted -a units,$varout,o,c,"$units" tmp_$file
#        ncatted -a cell_methods,$varout,o,c,"$cell_methods" tmp_$file
    fi

    if [ "$docorrectatt" == "1" ]; then
        while read atline; do
            attname=`echo $atline |cut -d: -f1`
            attval=`echo $atline |cut -d: -f2 |sed "s/{TODAY}/$today/; s/{FREQUENCY}/$outfrequency/"`
            ncatted -a ${attname},global,o,c,"${attval}" tmp_$file
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
            cdo setreftime,1949-12-01,00:00 -settaxis,${dec_start[$i]}-01-01,12:00,1day -selyear,$my_years tmp_$file ${varout}_${domainname}_${gcmodel}_${cmip5experiment}_${cmip5ensemblemember}_${rcmodel}_${rcmversion}_${outfrequency}_${dec_start[$i]}0101-${dec_end[$i]}1231.nc
        done
    fi

    if [ "$docorrectvar" == "1" ]; then
        mv tmp_$file `echo tmp_$file | sed "s/$varin/$varout/"`
    fi
done

if [ "$dotimemerge" == "1" ]; then
    ./domerge.py
fi
