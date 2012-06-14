function dopics(args)
    fname = subwrd(args,1)
    crufname = subwrd(args,2)
    var = subwrd(args,3)
    outpref = subwrd(args,4)
    dom = subwrd(args,5)
    'sdfopen 'fname
    'q file'
    rec1=sublin(result,5)
    tsize=subwrd(rec1,12)
    if (tsize>1)
        seasons.1='DJF'
        seasons.2='MAM'
        seasons.3='JJA'
        seasons.4='SON'
    endif
    if (tsize=1)
        seasons.1='year'
    endif

    'sdfopen 'crufname
    cnt=1
    while(cnt<=tsize)
        'set t 'cnt
        say '*** Processing tstep 'cnt
        'c'
        'set gxout shaded'
        'set mpdset hires'
        'set display color white'
        'set cterp on'
        'set csmooth on'
        'run def_domains.gs 'dom
        'run def_levs.gs 'dom' 'var
        'set grads off'
        if (var='TA')
            'd 'var'.1-273.15'
        endif
        if (var='TAMAX')
            'd 'var'.1-273.15'
        endif
        if (var='TAMIN')
            'd 'var'.1-273.15'
        endif
        if(var='RT')
            'd 'var'.1'
        endif
        'run colbar.gs'
        'draw title RegCM 'outpref' 'var' 'seasons.cnt
        'printim RCM-'outpref'.'var'.dom-'dom'.t-'seasons.cnt'.png'
        'c'
        'set grads off'
        'run def_levs.gs 'dom' 'var
        'd 'var'.2'
        'run colbar.gs'
        'draw title CRU 'var' 'seasons.cnt
        'printim CRU.'var'.dom-'dom'.t-'seasons.cnt'.png'
        'c'
        'set grads off'
        'run def_levs_diff.gs 'dom' 'var
        if (var='TA')
            'd 'var'.1 - 273.15 - 'var'.2'
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if (var='TAMAX')
            'd 'var'.1 - 273.15 - 'var'.2'
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if (var='TAMIN')
            'd 'var'.1 - 273.15 - 'var'.2'
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if(var='RT')
            'd (RT.1-RT.2)/RT.2'
            'draw title (RegCM-CRU)/CRU 'outpref' 'var' 'seasons.cnt
        endif
        'run colbar.gs'
        'printim RCM-CRU-perc-'outpref'.'var'.dom-'dom'.t-'seasons.cnt'.png'
        if (var='RT')
            'c'
            'set grads off'
            'run def_levs_diff.gs 'dom' RTsub'
            'd RT.1-RT.2'
            'run colbar.gs'
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
            'printim RCM-CRU-'outpref'.'var'.dom-'dom'.t-'seasons.cnt'.png'
        endif
        if (rc != 0); break; endif
        cnt = cnt+1
    endwhile
    'quit'
return
