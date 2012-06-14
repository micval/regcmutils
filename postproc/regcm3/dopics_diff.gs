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
        'run def_levs_diff.gs 'dom' 'var
        'set grads off'
        'd 'var'.1'
        'run colbar.gs'
        if (var='TA')
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if (var='TAMAX')
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if (var='TAMIN')
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        if(var='RT')
            'draw title (RegCM-CRU)/CRU 'outpref' 'var' 'seasons.cnt
        endif
        if(var='RTsub')
            'draw title RegCM-CRU 'outpref' 'var' 'seasons.cnt
        endif
        'run colbar.gs'
        'printim RCM-CRU-'outpref'.'var'.dom-'dom'.t-'seasons.cnt'.png'
        if (rc != 0); break; endif
        cnt = cnt+1
    endwhile
    'quit'
return
