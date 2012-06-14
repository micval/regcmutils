function deflevsdiff(args)
    dom = subwrd(args,1)
    var = subwrd(args,2)
    'run define_colors.gs'
    say '*** Processing domain 'dom' variable 'var
    if(dom = 1)
        if(var = 'TA')
            'set clevs    -6   -5   -4    -3   -2   -1   1    2    3    4    5    6'
            'set rbcols 49   48   47   45    43   41   0  21   23   25    27   28  29'
        endif
        if (var = 'RT')
*            'set clevs    0  1  2  3  4  5  6  7  8  9  10  11  12  13'
*            'set rbcols  0 41 81 42 82 43 83 44 84 45 85  46  47  48  49'
            'set rbcols 99  29 28 27 26 25 24 23 22 21 0 41 42 43 44 45 46 47 48 49 89'
*            'set clevs -100 -90 -80 -70 -60 -50 -40 -30 -20 -10 10 20 30 40 50 60 70 80 90 100'
            'set clevs   -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 1  2 3 4 5 6 7 8 9 10'
        endif
        if (var ='RTsub')
            'set clevs    -4 -3 -2 -1 1  2  3  4  5  6  7  8  9  10'
            'set rbcols  24 23 22 21 0 41 42 43 44 45 46 47 48 49  89'
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
            'set clevs    -8   -6   -4    -2    2    4    6    8    10   12'
            'set rbcols 47  45    43   41    0    21   23   25   27   28   29'
        endif
        if(var = 'TAMIN')
            'set clevs    -8   -6   -4    -2    2    4    6    8    10   12'
            'set rbcols 47  45    43   41    0    21   23   25   27   28   29'
        endif
    endif
return
