#!/bin/bash -x

year1=1990
year2=2008
timespec=monavg
realm=SRF
domainname='AFR-44'
gcmodel='ERAINT'
cmip5experiment='historical'
cmip5ensemblemember='r1i1p1'
rcmodel='CUNI-RegCM'
rcmversion='v1'
experiment='evaluation'
today=`date '+%Y-%m-%d-T%H:%M:%SZ'`
domainfile=cordex-africa-domain-cuni-3.nc
prefixin="$realm-cordex-africa-grell-$year1-$year2"

ln -sf globalattributes-${experiment}.txt globalattributes.txt
ln -sf vardefs-${realm}.txt vardefs.txt

if [ $timespec == 'monavg' -o $timespec == 'seasavg' ]; then
    numperiods=3
    perioddates[1]='1990-01-01,1990-12-31'
    starttimes[1]='199001'
    endtimes[1]='199012'
    taxis[1]='1990-01-16,00:00:00,1mon'

    perioddates[2]='1991-01-01,2000-12-31'
    starttimes[2]='199101'
    endtimes[2]='200012'
    taxis[2]='1991-01-16,00:00:00,1mon'

    perioddates[3]='2001-01-01,2008-12-31'
    starttimes[3]='200101'
    endtimes[3]='200812'
    taxis[3]='2001-01-16,00:00:00,1mon'

    outfrequency=${timespec%avg}
    cell_methods='time: mean'
    cdotdef='1mon'
elif [ $timespec == 'dayavg' ]; then
    outfrequency='day'
    cell_methods='time: mean'
fi

echo "@@@ cdo splitvar processing"
cdo -r setreftime,1949-12-01,00:00:00,days -settaxis,$year1-01-01,00:00,$cdotdef $prefixin.$timespec.nc $prefixin.$timespec-2.nc
cdo splitvar $prefixin.$timespec-2.nc $prefixin.$timespec.

while read vardef; do
    varin=`echo $vardef |cut -d: -f1`
    varout=`echo $vardef |cut -d: -f2`
    long_name=`echo $vardef |cut -d: -f3`
    standard_name=`echo $vardef |cut -d: -f4`
    units=`echo $vardef |cut -d: -f5`

    echo "@@@ apply time axis correction"
    ./correct-time-${timespec}.py $prefixin.$timespec.$varin.nc $year1 $year2

    echo "@@@ processing $varin -> $varout"
    ncrename -v $varin,$varout $prefixin.$timespec.$varin.nc
    while read atline; do
        attname=`echo $atline |cut -d: -f1`
        attval=`echo $atline |cut -d: -f2 |sed "s/{TODAY}/$today/; s/{FREQUENCY}/$outfrequency/"`

        ncatted -a ${attname},global,o,c,"$attval" $prefixin.$timespec.$varin.nc
    done <globalattributes.txt # end while read atline

    ncatted -a long_name,$varout,o,c,"$long_name" $prefixin.$timespec.$varin.nc
    ncatted -a standard_name,$varout,o,c,"$standard_name" $prefixin.$timespec.$varin.nc
    ncatted -a units,$varout,o,c,"$units" $prefixin.$timespec.$varin.nc
    ncatted -a coordinates,$varout,o,c,"lon lat" $prefixin.$timespec.$varin.nc
    ncatted -a cell_methods,$varout,o,c,"$cell_methods" $prefixin.$timespec.$varin.nc
    ncrename -v lon,nic -v lat,nic2 $prefixin.$timespec.$varin.nc
    ncks -A -v lon,lat $domainfile $prefixin.$timespec.$varin.nc
    ncks -v $varout,time_bnds -d lat,12,237 -d lon,12,225 $prefixin.$timespec.$varin.nc $prefixin.$timespec.$varin.2.nc
    mv $prefixin.$timespec.$varin.2.nc $prefixin.$timespec.$varin.nc

    for((peri=1;peri<=$numperiods;peri++)); do
        echo "@@@ processing period $peri"
        cdo seldate,${perioddates[$peri]} $prefixin.$timespec.$varin.nc $prefixin.$timespec.$varin.per_$peri.nc
        ncrename -d x,lon -d y,lat -d gsize,bnds $prefixin.$timespec.$varin.per_$peri.nc
        ncatted -a bounds,time,c,c,"time_bnds" $prefixin.$timespec.$varin.per_$peri.nc
        ncatted -h -a history,global,d,, $prefixin.$timespec.$varin.per_$peri.nc
        mv $prefixin.$timespec.$varin.per_$peri.nc ${varout}_${domainname}_${gcmodel}_${cmip5experiment}_${cmip5ensemblemember}_${rcmodel}_${rcmversion}_${outfrequency}_${starttimes[$peri]}_${endtimes[$peri]}.nc
    done # end for((peri...
done <vardefs.txt # end while read vardef
