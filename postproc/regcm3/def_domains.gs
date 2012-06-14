function defdomains(dom)
    say '*** Define domains'
    if(dom = 1)
        say '*** inner domain set'
        'set lon -20 55'
        'set lat -38 38'
    endif
    if(dom = 2)
        say '*** itcz domain set'
        'set lon -20 55'
        'set lat -10 14'
    endif
    if(dom = 3)
        say '*** Sahara domain set'
        'set lon -20 55'
        'set lat 20 30'
    endif
return
