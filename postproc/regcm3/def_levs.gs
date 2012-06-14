function deflevs(args)
    dom = subwrd(args,1)
    var = subwrd(args,2)
    'run define_colors.gs'
    say '*** Processing domain 'dom' variable 'var
    if(dom = 1)
        if(var = 'TA')
            'set clevs     6    8   10    12   14   16   18   20   22   24   26   28   30'
            'set rbcols 22   92  23    93   24   94   25    95  26   96    27   97   28   29'
        endif
        if (var = 'RT')
            'set clevs     1  2  3  4  5  6  7  8  9  10  11  12  13'
            'set rbcols  0 41 42 82 43 83 44 84 45 85  46  47  48  49'
        endif
        if (var = 'SWI')
            'set clevs   -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 1 2 3 4 5 6 7 8 9 10'
            'set rbcols 49  48  47  46  45  44  43  42  81  41 0 21 91 22 23 24 25 26 27 28 29'
        endif
        if (var = 'WIND')
            'set clevs    0  0.2  0.4  0.6  0.8  1.0  1.2  1.4'
            'set rbcols 0  31   33   34   35   36   37   38   39'
        endif
        if(var = 'TAMAX')
            'set clevs     15  17   19    21   23   25   27   29   31   33   35   37   39'
            'set rbcols  45  44  43    42    41  21   22   23   24   25   26   27   28   29'
        endif
        if(var = 'TAMIN')
            'set clevs     00  03   06    09   12   15   18   21   24   27'
            'set rbcols  41  21  22   23   24   94   25    26    27   28   29'
        endif
    endif
return
