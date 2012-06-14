#!/bin/bash  -x

domergetime=0
dotimeseries=1
dotimeseriesvalues=1
domaps=0
year0=1990
year1=2002
timespan="${year0}-${year1}"
#timespan=1990
experiments="grell kuo emanuel regcm411"
#experiments="grell kuo emanuel regcm4"
#experiments="regcm411"
timespec="ymonavg"
timespeccru="ymonavg"

domains=3
domainnames[1]="itcz"
domaindefs[1]="-18,52,-15,15"

domainnames[0]="inner"
domaindefs[0]="-18,52,-35,38" #-38,38

domainnames[2]="sahara"
domaindefs[2]="-15,35,15,30"

#domainnames[0]="WA"
#domaindefs[0]="-20,10,4,12"

#domainnames[2]="_"
#domaindefs[2]="-20,55,-45,43"

if [ $domergetime -eq 1 ]; then

for exp in $experiments; do
    filelist=""
    outfile=SRF-${exp}-${timespan}.selvar.monavg.nc
    for((y=$year0;y<=$year1;y++)); do
        filelist="$filelist orig/SRF-${exp}-${y}AVG.selvar.monavg.nc"
    done
    cdo mergetime $filelist $outfile
done

fi # domergetime

if [ $dotimeseries -eq 1 ]; then

for((d=0;d<$domains;d++)); do
    domn=${domainnames[$d]}
    domd=${domaindefs[$d]}

    if [ $dotimeseriesvalues -eq 1 ]; then
        cdo sellonlatbox,$domd CRU-${timespan}.${timespeccru}.nc CRU-${timespan}.$domn.${timespeccru}.nc
        cdo sellonlatbox,$domd ERAINT-${timespan}.${timespeccru}.nc ERAINT-${timespan}.$domn.${timespeccru}.nc
        for _e in $experiments; do
            cdo sellonlatbox,$domd SRF-${_e}-${timespan}.selvar.${timespec}.nc SRF-${_e}-${timespan}.$domn.selvar.${timespec}.nc
        done
    fi

    filelist=""
    for _e in $experiments; do
        filelist=$filelist" "SRF-${_e}-${timespan}.${domn}.selvar.${timespec}.nc
    done
#    ./timeseries.py TA ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> TA-${timespan}-${domn}.${timespec}.txt
#    ./timeseries.py RT ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> RT-${timespan}-${domn}.${timespec}.txt
#    ./timeseries.py TAMAX ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> TAMIN-${timespan}-${domn}.${timespec}.txt
#    ./timeseries.py TAMIN ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> TAMAX-${timespan}-${domn}.${timespec}.txt
    ./timeseries.py TA ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist ERAINT-${timespan}.${domn}.${timespeccru}.nc &> TA-${timespan}-${domn}.${timespec}.txt
    ./timeseries.py RT ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist ERAINT-${timespan}.${domn}.${timespeccru}.nc &> RT-${timespan}-${domn}.${timespec}.txt
    ./timeseries.py TAMAX ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> TAMIN-${timespan}-${domn}.${timespec}.txt
    ./timeseries.py TAMIN ${domn}-masked $timespec CRU-${timespan}.${domn}.${timespeccru}.nc $filelist &> TAMAX-${timespan}-${domn}.${timespec}.txt
done

fi # dotimeseries

if [ $domaps -eq 1 ]; then

cdo -r settaxis,2000-12-15,00:00,1mon -timavg CRU-${timespan}.monavg.nc CRU-${timespan}.allavg.nc

for _e in $experiments; do
    cdo -r settaxis,2000-12-15,00:00,1mon -timavg SRF-${_e}-${timespan}.selvar.monavg.nc SRF-${_e}-${timespan}.selvar.allavg.nc

    grads -blc "run dopics.gs SRF-${_e}-${timespan}.selvar.allavg.nc CRU-${timespan}.allavg.nc TA ${_e} 1"
    grads -blc "run dopics.gs SRF-${_e}-${timespan}.selvar.allavg.nc CRU-${timespan}.allavg.nc RT ${_e} 1"
    grads -blc "run dopics.gs SRF-${_e}-${timespan}.selvar.allavg.nc CRU-${timespan}.allavg.nc TAMAX ${_e} 1"
    grads -blc "run dopics.gs SRF-${_e}-${timespan}.selvar.allavg.nc CRU-${timespan}.allavg.nc TAMIN ${_e} 1"
done

fi # domaps
